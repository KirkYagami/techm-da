# Creating Pipelines with Apache Beam & Dataflow

> **Level:** Intermediate (Python basics assumed)
> **Time:** ~60 minutes
> **Goal:** Understand the core primitives of Apache Beam and build progressively complex pipelines, from a simple word count to a multi-stage enrichment pipeline.

---

## 🖥️ Local vs Cloud — What do I need?

| | Local (DirectRunner) | Cloud (DataflowRunner) |
|---|---|---|
| **GCP account needed?** | ❌ No | ✅ Yes |
| **Cost** | Free | Uses $300 credit (~$1–3/job) |
| **Setup time** | `pip install` only | GCP project + APIs + GCS bucket |
| **Best for** | All 5 pipelines in this guide | Scaling to millions of records |

**Recommendation:** All 5 pipelines in this guide run 100% locally using `DirectRunner`. Only Pipeline 5 shows the Dataflow deployment flags — treat that section as "when you're ready to go cloud."

---

## What Is a Pipeline?

A Beam **pipeline** is a directed acyclic graph (DAG) of data transformations.

```
PCollection  →  PTransform  →  PCollection  →  PTransform  →  ...
```

- **PCollection** — an immutable, distributed dataset (like a list, but parallel)
- **PTransform** — a data transformation (map, filter, group, join, etc.)
- **Runner** — the engine that executes the graph (local, Dataflow, Spark, etc.)

---

## Setup

```bash
pip install apache-beam[gcp]
```

---

## Pipeline 1 — Hello World: Word Count

The classic starting point for every Beam tutorial.

```python
# pipeline_01_wordcount.py
import re
import apache_beam as beam

INPUT_TEXT = """
To be or not to be that is the question
Whether tis nobler in the mind to suffer
The slings and arrows of outrageous fortune
Or to take arms against a sea of troubles
"""

with beam.Pipeline() as p:
    (
        p
        # Create a PCollection from an in-memory list of lines
        | "Create Lines"   >> beam.Create(INPUT_TEXT.strip().splitlines())

        # Split each line into words
        | "Split Words"    >> beam.FlatMap(lambda line: re.findall(r"[a-z']+", line.lower()))

        # Emit (word, 1) tuples
        | "Pair with One"  >> beam.Map(lambda word: (word, 1))

        # Sum counts per key
        | "Count Words"    >> beam.CombinePerKey(sum)

        # Filter to words appearing more than once
        | "Filter Common"  >> beam.Filter(lambda kv: kv[1] > 1)

        # Print results
        | "Print"          >> beam.Map(print)
    )
```

Run it:

```bash
python pipeline_01_wordcount.py
# ('to', 5)
# ('the', 3)
# ('or', 2)
# ('of', 2)
```

### What each transform does

| Transform | Input | Output |
|---|---|---|
| `beam.Create(...)` | Python list | PCollection of elements |
| `beam.Map(fn)` | 1 element → 1 element | PCollection |
| `beam.FlatMap(fn)` | 1 element → 0..N elements | PCollection (flattened) |
| `beam.Filter(fn)` | 1 element → keep/discard | PCollection |
| `beam.CombinePerKey(fn)` | (key, value) pairs | (key, combined_value) per key |

---

## Pipeline 2 — Reading & Writing Files

Real pipelines read from and write to persistent storage.

```python
# pipeline_02_files.py
import apache_beam as beam
import re

def parse_log_line(line):
    """Parse an Apache access log line into a dict."""
    # Example: 192.168.1.1 - - [01/Jan/2024] "GET /api/data HTTP/1.1" 200 512
    pattern = r'(\S+) .+ "(\w+) (\S+) \S+" (\d{3}) (\d+)'
    match = re.match(pattern, line)
    if match:
        return {
            "ip":         match.group(1),
            "method":     match.group(2),
            "path":       match.group(3),
            "status":     int(match.group(4)),
            "bytes_sent": int(match.group(5)),
        }
    return None  # malformed line

def format_output(record):
    return f"{record['status']}\t{record['path']}\t{record['ip']}"


with beam.Pipeline() as p:
    parsed = (
        p
        | "Read Log File"  >> beam.io.ReadFromText("access.log")
        | "Parse Lines"    >> beam.Map(parse_log_line)
        | "Drop None"      >> beam.Filter(lambda x: x is not None)
    )

    # Branch 1: write all 4xx errors to a separate file
    (
        parsed
        | "Filter Errors"  >> beam.Filter(lambda r: 400 <= r["status"] < 500)
        | "Format Errors"  >> beam.Map(format_output)
        | "Write Errors"   >> beam.io.WriteToText("errors_output", file_name_suffix=".tsv")
    )

    # Branch 2: count requests per path
    (
        parsed
        | "Key by Path"    >> beam.Map(lambda r: (r["path"], 1))
        | "Count by Path"  >> beam.CombinePerKey(sum)
        | "Format Counts"  >> beam.Map(lambda kv: f"{kv[1]}\t{kv[0]}")
        | "Write Counts"   >> beam.io.WriteToText("path_counts", file_name_suffix=".tsv")
    )
```

**Key point:** A single PCollection can be used by multiple downstream branches. This is called **pipeline branching** and is a fundamental pattern.

---

## Pipeline 3 — Custom DoFn (Stateful Processing)

When `Map` and `Filter` aren't enough, use a `DoFn` — the building block of all Beam transforms.

```python
# pipeline_03_dofn.py
import apache_beam as beam
from apache_beam import pvalue

class SplitByStatus(beam.DoFn):
    """
    Routes records to different output tags based on HTTP status.
    This is called 'multiple output tags'.
    """

    ERROR_TAG   = "errors"
    SUCCESS_TAG = "success"
    SLOW_TAG    = "slow"

    def process(self, record):
        # Always yield to main output
        yield record

        # Additionally tag based on status
        if record["status"] >= 400:
            yield pvalue.TaggedOutput(self.ERROR_TAG, record)

        if record.get("response_ms", 0) > 500:
            yield pvalue.TaggedOutput(self.SLOW_TAG, record)

        if record["status"] < 300:
            yield pvalue.TaggedOutput(self.SUCCESS_TAG, record)


class EnrichWithGeo(beam.DoFn):
    """
    Simulates IP → country lookup.
    In production this would call an external API or lookup table.
    """

    def setup(self):
        # Runs once per worker — great for loading lookup tables or models
        self.ip_to_country = {
            "192.168.": "Internal",
            "10.0.":    "Internal",
            "8.8.":     "US-Google",
        }

    def process(self, record):
        country = "Unknown"
        for prefix, name in self.ip_to_country.items():
            if record["ip"].startswith(prefix):
                country = name
                break
        record["country"] = country
        yield record


# Sample data
sample_records = [
    {"ip": "192.168.1.1", "status": 200, "path": "/api/v1", "response_ms": 120},
    {"ip": "8.8.8.8",     "status": 404, "path": "/missing", "response_ms": 35},
    {"ip": "1.2.3.4",     "status": 500, "path": "/crash",   "response_ms": 801},
    {"ip": "10.0.0.5",    "status": 200, "path": "/health",  "response_ms": 12},
]

with beam.Pipeline() as p:
    records = (
        p
        | "Create"   >> beam.Create(sample_records)
        | "Enrich"   >> beam.ParDo(EnrichWithGeo())
    )

    # Split into tagged outputs
    tagged = records | "Split" >> beam.ParDo(SplitByStatus()).with_outputs(
        SplitByStatus.ERROR_TAG,
        SplitByStatus.SUCCESS_TAG,
        SplitByStatus.SLOW_TAG,
        main="all",
    )

    tagged.errors  | "Log Errors"   >> beam.Map(lambda r: print(f"[ERROR]   {r}"))
    tagged.success | "Log Success"  >> beam.Map(lambda r: print(f"[SUCCESS] {r}"))
    tagged.slow    | "Log Slow"     >> beam.Map(lambda r: print(f"[SLOW]    {r}"))
```

---

## Pipeline 4 — GroupByKey and CoGroupByKey (Joins)

Beam supports joining two PCollections — similar to a SQL JOIN.

```python
# pipeline_04_joins.py
import apache_beam as beam

# Orders dataset
orders = [
    {"order_id": "O001", "user_id": "U1", "amount": 49.99},
    {"order_id": "O002", "user_id": "U2", "amount": 15.00},
    {"order_id": "O003", "user_id": "U1", "amount": 99.50},
    {"order_id": "O004", "user_id": "U3", "amount": 7.25},
]

# Users dataset
users = [
    {"user_id": "U1", "name": "Alice",   "country": "India"},
    {"user_id": "U2", "name": "Bob",     "country": "US"},
    {"user_id": "U3", "name": "Charlie", "country": "UK"},
]

with beam.Pipeline() as p:

    # Key both datasets by user_id
    keyed_orders = (
        p
        | "Create Orders" >> beam.Create(orders)
        | "Key Orders"    >> beam.Map(lambda o: (o["user_id"], o))
    )

    keyed_users = (
        p
        | "Create Users" >> beam.Create(users)
        | "Key Users"    >> beam.Map(lambda u: (u["user_id"], u))
    )

    # CoGroupByKey joins both on the shared key
    joined = (
        {"orders": keyed_orders, "users": keyed_users}
        | "Join"  >> beam.CoGroupByKey()
    )

    def format_join(element):
        user_id, grouped = element
        orders_list = list(grouped["orders"])
        users_list  = list(grouped["users"])

        if not users_list:
            return f"{user_id}: no user profile found"

        user  = users_list[0]
        total = sum(o["amount"] for o in orders_list)
        return (
            f"{user['name']} ({user['country']}) — "
            f"{len(orders_list)} orders, total ${total:.2f}"
        )

    (
        joined
        | "Format" >> beam.Map(format_join)
        | "Print"  >> beam.Map(print)
    )
```

Output:

```
Alice (India) — 2 orders, total $149.49
Bob (US) — 1 orders, total $15.00
Charlie (UK) — 1 orders, total $7.25
```

---

## Pipeline 5 — Full Production Pattern

Combining everything: file I/O, custom DoFns, branching, and pipeline options.

```python
# pipeline_05_production.py
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
import json
import logging

# ── Pipeline options: swap runner here for cloud deployment ──
class MyOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument("--input",  default="input_data.jsonl")
        parser.add_argument("--output", default="output/results")


# ── Transforms as reusable classes ──
class ParseJSON(beam.DoFn):
    def process(self, line):
        try:
            yield json.loads(line)
        except json.JSONDecodeError as e:
            logging.warning(f"Bad JSON: {line[:60]}… — {e}")

class ValidateRecord(beam.DoFn):
    VALID_TAG   = "valid"
    INVALID_TAG = "invalid"

    REQUIRED_FIELDS = ["user_id", "event_type", "timestamp", "value"]

    def process(self, record):
        missing = [f for f in self.REQUIRED_FIELDS if f not in record]
        if missing:
            record["_error"] = f"Missing fields: {missing}"
            yield beam.pvalue.TaggedOutput(self.INVALID_TAG, record)
        else:
            yield beam.pvalue.TaggedOutput(self.VALID_TAG, record)

class NormalizeRecord(beam.DoFn):
    def process(self, record):
        record["event_type"] = record["event_type"].lower().strip()
        record["value"]      = float(record.get("value", 0))
        yield record


def run():
    options = MyOptions()

    with beam.Pipeline(options=options) as p:
        raw = (
            p
            | "Read Input"  >> beam.io.ReadFromText(options.input)
            | "Parse JSON"  >> beam.ParDo(ParseJSON())
        )

        tagged = raw | "Validate" >> beam.ParDo(ValidateRecord()).with_outputs(
            ValidateRecord.VALID_TAG,
            ValidateRecord.INVALID_TAG,
        )

        # Process valid records
        valid_processed = (
            tagged[ValidateRecord.VALID_TAG]
            | "Normalize"   >> beam.ParDo(NormalizeRecord())
            | "Key by Type" >> beam.Map(lambda r: (r["event_type"], r["value"]))
            | "Sum by Type" >> beam.CombinePerKey(sum)
            | "To String"   >> beam.Map(lambda kv: json.dumps({"event": kv[0], "total": kv[1]}))
        )

        valid_processed | "Write Output" >> beam.io.WriteToText(
            options.output,
            file_name_suffix=".jsonl"
        )

        # Write invalid records to a quarantine file
        (
            tagged[ValidateRecord.INVALID_TAG]
            | "Invalid to String" >> beam.Map(json.dumps)
            | "Write Quarantine"  >> beam.io.WriteToText(
                options.output + "_quarantine",
                file_name_suffix=".jsonl"
            )
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
```

---

## Deploying to Cloud Dataflow

Once your pipeline works locally with `DirectRunner`, deploying is just a flag change:

```bash
python pipeline_05_production.py \
  --runner=DataflowRunner \
  --project=YOUR_PROJECT_ID \
  --region=us-central1 \
  --temp_location=gs://YOUR_BUCKET/temp \
  --staging_location=gs://YOUR_BUCKET/staging \
  --input=gs://YOUR_BUCKET/input/data.jsonl \
  --output=gs://YOUR_BUCKET/output/results \
  --num_workers=5 \
  --max_num_workers=20 \
  --autoscaling_algorithm=THROUGHPUT_BASED
```

Dataflow will:
1. Package and upload your code
2. Create a Dataflow job with your pipeline graph
3. Auto-scale workers based on throughput
4. Write results to GCS

---

## Pipeline Primitives — Quick Reference

```
beam.Create([...])             # Create PCollection from in-memory data
beam.io.ReadFromText(path)     # Read lines from file(s) or GCS
beam.io.WriteToText(path)      # Write strings to file(s) or GCS
beam.Map(fn)                   # 1-to-1 transform
beam.FlatMap(fn)               # 1-to-many transform (fn returns iterable)
beam.Filter(fn)                # Keep elements where fn returns True
beam.ParDo(DoFn())             # Apply a full DoFn class
beam.CombinePerKey(fn)         # Aggregate (key, value) pairs by key
beam.GroupByKey()              # Group all values by key → (key, [values])
beam.CoGroupByKey()            # Join two or more keyed PCollections
beam.Flatten([pc1, pc2])       # Merge multiple PCollections into one
beam.Partition(fn, n)          # Split into N PCollections by function
```

---

## Common Patterns

### Reusable composite transforms

```python
# Wrap a chain of transforms in a PTransform subclass for reuse
class ParseAndValidate(beam.PTransform):
    def expand(self, pcoll):
        return (
            pcoll
            | "Parse"    >> beam.Map(json.loads)
            | "Validate" >> beam.Filter(lambda r: "id" in r)
        )

# Use it like a built-in:
p | "Ingest" >> ParseAndValidate()
```

### Side inputs (broadcasting a small dataset)

```python
# Use a dict as a side input for fast lookups inside a DoFn
lookup_table = p | "Load Lookup" >> beam.Create([("US", "USD"), ("IN", "INR")])
lookup_view  = beam.pvalue.AsDict(lookup_table)

def enrich(record, currency_map):
    record["currency"] = currency_map.get(record["country"], "UNK")
    return record

records | "Enrich" >> beam.Map(enrich, currency_map=lookup_view)
```

---

## What to Try Next

- Add a **windowing strategy** to process records by 5-minute tumbling windows
- Replace `WriteToText` with `WriteToBigQuery` for structured output
- Connect to **Pub/Sub** as a streaming source with `ReadFromPubSub`
- Use `beam.metrics.Metrics.counter(...)` to track custom counts visible in the Dataflow UI
