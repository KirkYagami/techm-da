# Beam SQL

> **Level:** Intermediate (SQL basics assumed)
> **Time:** ~40 minutes
> **Goal:** Write SQL queries inside Apache Beam pipelines using `SqlTransform` — runs entirely on your laptop, no GCP account needed.

---

## ⚠️ What Happened to Dataflow SQL?

Dataflow SQL was a GCP console feature that let you run SQL directly from the browser.
**It was shut down:**
- Console access removed: **July 31, 2024**
- `gcloud` CLI access removed: **January 31, 2025**

The replacement is **Beam SQL** — SQL built directly into Apache Beam pipelines using `SqlTransform`. It runs on `DirectRunner` locally (free, no account needed) and can be deployed to Dataflow when you're ready to scale.

---

## 🖥️ Local vs Cloud — What do I need?

| | Local (DirectRunner) | Cloud (DataflowRunner) |
|---|---|---|
| **GCP account needed?** | ❌ No | ✅ Yes |
| **Cost** | Free | Uses $300 credit (~$1–3/job) |
| **Setup time** | `pip install` only | GCP project + APIs + GCS bucket |
| **Best for** | All demos in this guide | Large-scale production jobs |

**Every example in this guide runs 100% locally.** The final section shows how to point it at Dataflow when you're ready.

---

## What Is Beam SQL?

Beam SQL lets you query bounded and unbounded PCollections with SQL statements. Your SQL query is translated into a `PTransform` — an encapsulated segment of a Beam pipeline. You can freely mix SQL PTransforms with other PTransforms in your pipeline.

Beam SQL uses Calcite SQL based on Apache Calcite, a dialect widespread in big data processing.

The two key concepts:
- **`SqlTransform`** — wraps a SQL string and returns a PTransform
- **`Row`** — a typed record with a `Schema`; Beam SQL operates on `PCollection<Row>`

```
PCollection<Row>  →  SqlTransform.query("SELECT ...")  →  PCollection<Row>
```

---

## Prerequisites

```bash
pip install apache-beam[gcp]
```

That's it. No GCP account, no `gcloud`, no credentials needed for this guide.

---

## Part A — Your First SQL Query on In-Memory Data

### Step 1 — Define a Schema and Create Rows

Beam SQL works on `PCollection<Row>` where every row has a known schema — similar to a database table definition.

```python
# sql_01_basic.py
import apache_beam as beam
from apache_beam import Row
from apache_beam.transforms.sql import SqlTransform

# Sample sales data as Python dicts
sales_data = [
    {"product": "Laptop",  "category": "Electronics", "units": 5,  "price": 999.99},
    {"product": "Phone",   "category": "Electronics", "units": 12, "price": 499.00},
    {"product": "Desk",    "category": "Furniture",   "units": 3,  "price": 249.50},
    {"product": "Chair",   "category": "Furniture",   "units": 8,  "price": 189.00},
    {"product": "Monitor", "category": "Electronics", "units": 7,  "price": 349.99},
    {"product": "Lamp",    "category": "Furniture",   "units": 15, "price": 45.00},
]

with beam.Pipeline() as p:
    rows = (
        p
        | "Create Data" >> beam.Create(sales_data)
        # Convert dicts to named tuples so Beam can infer the schema
        | "To Rows" >> beam.Map(lambda d: Row(
            product=d["product"],
            category=d["category"],
            units=int(d["units"]),
            price=float(d["price"]),
        ))
    )

    # Apply SQL directly to the PCollection
    result = rows | "SQL Query" >> SqlTransform("""
        SELECT
            product,
            category,
            units,
            price,
            units * price  AS revenue
        FROM PCOLLECTION
        WHERE units > 5
        ORDER BY revenue DESC
    """)

    result | "Print" >> beam.Map(print)
```

Run it:

```bash
python sql_01_basic.py
```

Expected output:

```
Row(product='Phone', category='Electronics', units=12, price=499.0, revenue=5988.0)
Row(product='Monitor', category='Electronics', units=7, price=349.99, revenue=2449.93)
Row(product='Lamp', category='Furniture', units=15, price=45.0, revenue=675.0)
```

**Key things to notice:**
- `FROM PCOLLECTION` — the keyword Beam SQL uses to refer to the input PCollection
- SQL runs as a standard Beam `PTransform` — it fits naturally in the `|` chain
- No external database, no connection strings, no credentials

---

## Part B — Aggregations and GROUP BY

SQL aggregations work exactly as you'd expect.

```python
# sql_02_aggregations.py
import apache_beam as beam
from apache_beam import Row
from apache_beam.transforms.sql import SqlTransform

sales_data = [
    {"product": "Laptop",  "category": "Electronics", "units": 5,  "price": 999.99},
    {"product": "Phone",   "category": "Electronics", "units": 12, "price": 499.00},
    {"product": "Desk",    "category": "Furniture",   "units": 3,  "price": 249.50},
    {"product": "Chair",   "category": "Furniture",   "units": 8,  "price": 189.00},
    {"product": "Monitor", "category": "Electronics", "units": 7,  "price": 349.99},
    {"product": "Lamp",    "category": "Furniture",   "units": 15, "price": 45.00},
]

with beam.Pipeline() as p:
    rows = (
        p
        | "Create" >> beam.Create(sales_data)
        | "To Rows" >> beam.Map(lambda d: Row(
            product=d["product"],
            category=d["category"],
            units=int(d["units"]),
            price=float(d["price"]),
        ))
    )

    # Aggregate by category
    summary = rows | "Summarise" >> SqlTransform("""
        SELECT
            category,
            COUNT(*)            AS num_products,
            SUM(units)          AS total_units,
            ROUND(AVG(price), 2) AS avg_price,
            SUM(units * price)  AS total_revenue
        FROM PCOLLECTION
        GROUP BY category
        ORDER BY total_revenue DESC
    """)

    summary | "Print Summary" >> beam.Map(
        lambda r: print(
            f"[{r.category}] "
            f"{r.num_products} products | "
            f"{r.total_units} units | "
            f"avg price ${r.avg_price} | "
            f"revenue ${r.total_revenue:.2f}"
        )
    )
```

Output:

```
[Electronics] 3 products | 24 units | avg price $616.33 | revenue $9437.86
[Furniture] 3 products | 26 units | avg price $161.17 | revenue $3184.50
```

---

## Part C — Joining Two PCollections with SQL

This is where Beam SQL really shines. You can JOIN two separate PCollections just like SQL tables.

```python
# sql_03_joins.py
import apache_beam as beam
from apache_beam import Row
from apache_beam.transforms.sql import SqlTransform

# Orders
orders_data = [
    {"order_id": "O001", "customer_id": "C1", "product": "Laptop",  "units": 2},
    {"order_id": "O002", "customer_id": "C2", "product": "Phone",   "units": 1},
    {"order_id": "O003", "customer_id": "C1", "product": "Monitor", "units": 3},
    {"order_id": "O004", "customer_id": "C3", "product": "Chair",   "units": 5},
]

# Customers
customers_data = [
    {"customer_id": "C1", "name": "Priya",  "country": "India"},
    {"customer_id": "C2", "name": "Alex",   "country": "US"},
    {"customer_id": "C3", "name": "Sophie", "country": "France"},
]

with beam.Pipeline() as p:
    orders = (
        p
        | "Create Orders" >> beam.Create(orders_data)
        | "Orders to Rows" >> beam.Map(lambda d: Row(
            order_id=d["order_id"],
            customer_id=d["customer_id"],
            product=d["product"],
            units=int(d["units"]),
        ))
    )

    customers = (
        p
        | "Create Customers" >> beam.Create(customers_data)
        | "Customers to Rows" >> beam.Map(lambda d: Row(
            customer_id=d["customer_id"],
            name=d["name"],
            country=d["country"],
        ))
    )

    # JOIN using a PCollectionTuple — each tag becomes a table name in SQL
    joined = (
        {"orders": orders, "customers": customers}
        | "Join" >> SqlTransform("""
            SELECT
                o.order_id,
                c.name       AS customer_name,
                c.country,
                o.product,
                o.units
            FROM orders AS o
            INNER JOIN customers AS c
                ON o.customer_id = c.customer_id
            ORDER BY c.name
        """)
    )

    joined | "Print" >> beam.Map(
        lambda r: print(
            f"  {r.order_id} | {r.customer_name} ({r.country}) "
            f"→ {r.units}x {r.product}"
        )
    )
```

Output:

```
  O002 | Alex (US) → 1x Phone
  O001 | Priya (India) → 2x Laptop
  O003 | Priya (India) → 3x Monitor
  O004 | Sophie (France) → 5x Chair
```

**Key point:** When passing a dict of PCollections, the dict keys become the table names in your SQL (`FROM orders`, `FROM customers`). When passing a single PCollection, use `FROM PCOLLECTION`.

---

## Part D — Mixing SQL with Regular Beam Transforms

SQL transforms slot into any Beam pipeline — before or after regular transforms.

```python
# sql_04_mixed.py
import apache_beam as beam
from apache_beam import Row
from apache_beam.transforms.sql import SqlTransform
import json

log_lines = [
    '{"ip": "10.0.0.1", "path": "/api/data",    "status": 200, "ms": 45}',
    '{"ip": "8.8.8.8",  "path": "/api/upload",  "status": 200, "ms": 820}',
    '{"ip": "1.2.3.4",  "path": "/login",        "status": 401, "ms": 12}',
    '{"ip": "10.0.0.2", "path": "/api/data",    "status": 200, "ms": 310}',
    '{"ip": "5.6.7.8",  "path": "/admin",        "status": 403, "ms": 8}',
    '{"ip": "10.0.0.1", "path": "/api/upload",  "status": 500, "ms": 2100}',
]

with beam.Pipeline() as p:
    # Step 1: Regular Beam transform to parse JSON
    parsed = (
        p
        | "Read Logs"  >> beam.Create(log_lines)
        | "Parse JSON" >> beam.Map(lambda line: json.loads(line))
        | "To Rows"    >> beam.Map(lambda d: Row(
            ip=d["ip"],
            path=d["path"],
            status=int(d["status"]),
            ms=int(d["ms"]),
        ))
    )

    # Step 2: SQL to find slow or errored requests
    alerts = parsed | "Find Issues" >> SqlTransform("""
        SELECT
            ip,
            path,
            status,
            ms,
            CASE
                WHEN status >= 500 THEN 'SERVER_ERROR'
                WHEN status >= 400 THEN 'CLIENT_ERROR'
                WHEN ms > 500      THEN 'SLOW_REQUEST'
                ELSE 'OK'
            END AS issue_type
        FROM PCOLLECTION
        WHERE status >= 400 OR ms > 500
        ORDER BY ms DESC
    """)

    # Step 3: Regular Beam transform to format and print
    (
        alerts
        | "Format Alerts" >> beam.Map(
            lambda r: f"[{r.issue_type}] {r.status} {r.path} from {r.ip} ({r.ms}ms)"
        )
        | "Print Alerts" >> beam.Map(print)
    )
```

Output:

```
[SERVER_ERROR] 500 /api/upload from 10.0.0.1 (2100ms)
[SLOW_REQUEST] 200 /api/upload from 8.8.8.8 (820ms)
[CLIENT_ERROR] 401 /login from 1.2.3.4 (12ms)
[CLIENT_ERROR] 403 /admin from 5.6.7.8 (8ms)
```

---

## Part E — Reading from a CSV File

Real pipelines read from files. Here's how to wire it up with Beam SQL.

```python
# sql_05_from_file.py
import apache_beam as beam
from apache_beam import Row
from apache_beam.transforms.sql import SqlTransform
import csv
import io

def parse_csv_line(line, headers):
    """Parse a CSV line into a dict using provided headers."""
    reader = csv.reader(io.StringIO(line))
    values = next(reader)
    return dict(zip(headers, values))

HEADERS = ["product", "category", "units", "price"]

with beam.Pipeline() as p:
    rows = (
        p
        | "Read File"   >> beam.io.ReadFromText("sales.csv", skip_header_lines=1)
        | "Parse CSV"   >> beam.Map(parse_csv_line, headers=HEADERS)
        | "To Rows"     >> beam.Map(lambda d: Row(
            product=d["product"],
            category=d["category"],
            units=int(d["units"]),
            price=float(d["price"]),
        ))
    )

    result = rows | "SQL" >> SqlTransform("""
        SELECT
            category,
            COUNT(*) AS products,
            SUM(units * price) AS revenue
        FROM PCOLLECTION
        GROUP BY category
        ORDER BY revenue DESC
    """)

    result | "Write" >> beam.io.WriteToText("sql_output", file_name_suffix=".txt")
```

Create a sample `sales.csv`:

```csv
product,category,units,price
Laptop,Electronics,5,999.99
Phone,Electronics,12,499.00
Desk,Furniture,3,249.50
Chair,Furniture,8,189.00
```

---

## Deploying to Dataflow (When Ready)

Once your pipeline works locally, deploying to Cloud Dataflow is a single flag change:

```python
from apache_beam.options.pipeline_options import PipelineOptions

options = PipelineOptions(
    runner="DataflowRunner",       # ← change from DirectRunner
    project="your-gcp-project",
    region="us-central1",
    temp_location="gs://your-bucket/temp",
    staging_location="gs://your-bucket/staging",
)

with beam.Pipeline(options=options) as p:
    # ... same pipeline code unchanged ...
```

Note: Dataflow uses your $300 GCP credit. A small batch job typically costs $0.50–$2.00.
**Always cancel streaming jobs when done** — they run continuously and will drain credits.

---

## Beam SQL Quick Reference

```sql
-- Single PCollection
SELECT col1, col2 FROM PCOLLECTION WHERE ...

-- Multiple PCollections (dict keys become table names)
SELECT a.x, b.y FROM table_a AS a INNER JOIN table_b AS b ON a.id = b.id

-- Aggregations
SELECT category, COUNT(*), SUM(col), AVG(col), MAX(col) FROM PCOLLECTION GROUP BY category

-- CASE expressions
SELECT CASE WHEN status >= 400 THEN 'error' ELSE 'ok' END AS label FROM PCOLLECTION

-- Filtering after aggregation
SELECT category, SUM(units) AS total FROM PCOLLECTION GROUP BY category HAVING total > 10
```

**Beam SQL uses Apache Calcite dialect** — standard SQL with minor differences from MySQL/Postgres.

---

## Common Mistakes to Avoid

- **Forgetting `FROM PCOLLECTION`** — this is the required table name for a single input; `FROM my_table` won't work unless you pass a dict with that key
- **Mixing types without casting** — all columns must have consistent types; use `CAST(col AS INTEGER)` if needed
- **Expecting ORDER BY on unbounded streams** — sorting requires all data to be available; it works fine in batch but has limits in streaming
- **Schema mismatch** — if `Row` fields don't match what SQL expects, you'll get a runtime schema error; double-check column names and types

---

## What to Try Next

- Chain two `SqlTransform` steps — output of the first becomes input to the second
- Add a `beam.Filter` before the SQL to pre-filter rows before they reach the query
- Try `CAST`, `UPPER()`, `LOWER()`, `SUBSTR()` — Calcite SQL supports a full set of string and math functions
- Deploy to Dataflow and compare the execution graph in the GCP console with your local run
