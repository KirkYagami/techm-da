# Ingesting and Processing the Data

### Professional Training Program — Lecture Notes

---

> **Note before we begin:** Every flashy AI demo you've ever seen — the chatbot, the fraud detector, the recommendation engine — sits on top of an unglamorous foundation: a pipeline that reliably moves data from where it's born to where it's needed, in a shape someone can actually use. I've watched brilliant data science teams get completely stuck not because their models were bad, but because nobody had built a trustworthy pipeline underneath them. This is the plumbing of the AI industry. Master it, and everything downstream gets dramatically easier.

---

## Table of Contents
Table of Contents
1. Planning the Data Pipelines
2. Defining Data Sources and Sinks
3. Defining Data Transformation Logic
4. Networking Fundamentals
5. Data Encryption
6. Building the Pipelines
7. Data Cleansing
8. Identifying the Services
9. Transformations
10. Data Acquisition and Import
11. Integrating with New Data Sources
12. Job Automation and Orchestration
13. CI/CD
14. Summary / Quick Reference

---

## 1. Planning the Data Pipelines

Before a single line of code gets written, the most important work happens on a whiteboard — or at least, it should.

A **data pipeline** is a series of steps that moves data from one or more sources, transforms it along the way, and lands it somewhere useful. That sounds simple. The complexity hides in the decisions you make before you start building.

**Why planning matters so much:** I've seen teams jump straight into writing Dataflow code, only to discover three weeks later that they built a real-time streaming pipeline for data that only needed to update once a day — burning compute budget on unnecessary infrastructure. The inverse mistake is just as common: building a simple nightly batch job for data that the business actually needed within minutes, forcing a painful rebuild.

Planning a pipeline means answering a sequence of concrete questions, roughly in this order:

**What does the data look like, and how often does it arrive?** Is this a database table that changes a few times a day, or a continuous stream of clickstream events arriving thousands of times per second? This single question determines whether you need **batch processing** (handling data in discrete chunks, like "all of yesterday's orders") or **stream processing** (handling data continuously, as it arrives).

**What's the acceptable latency?** If a business analyst needs a report by 8 AM, a nightly batch job that finishes at 3 AM is fine. If a fraud-detection system needs to flag a suspicious transaction before it completes, you need near-real-time processing, often with sub-second latency requirements.

**What's the data volume, and how will it grow?** A pipeline that comfortably processes 10,000 records a day might fall over at 10 million. Plan for at least 2-3x your current scale, because data volumes in successful businesses grow faster than anyone predicts.

**Who are the downstream consumers?** A data warehouse for business intelligence has very different requirements than a feature store feeding a real-time ML model. Know your audience before you design the pipeline.

```
Pipeline Planning Checklist
┌──────────────────────────────────────────────────┐
│ □ Data velocity: batch vs. streaming?             │
│ □ Latency requirement: seconds, hours, or days?   │
│ □ Volume today, and volume in 12 months?          │
│ □ Who consumes the output, and in what format?    │
│ □ What happens if the pipeline fails mid-run?     │
│ □ What's the budget for compute and storage?      │
└──────────────────────────────────────────────────┘
```

> **Practitioner insight:** "Batch until proven otherwise" is a good default rule. Streaming pipelines are more complex to build, debug, and maintain than batch pipelines. Only reach for streaming when there's a genuine business requirement for low latency — not because streaming sounds more impressive in a meeting.

---

## 2. Defining Data Sources and Sinks

Every pipeline has a beginning and an end. In data engineering vocabulary, the beginning is a **source** and the end is a **sink**.

**Sources** are everywhere data can originate: an operational database (like PostgreSQL or MySQL) that runs your e-commerce app, a SaaS platform's API (like Salesforce or Stripe), files dropped into cloud storage, IoT sensor readings, application logs, or a real-time event stream from a messaging system like Pub/Sub or Kafka.

**Sinks** are destinations: a data warehouse like BigQuery for analytics, a Cloud Storage bucket for raw archival, an operational database for serving an application, or a feature store that an ML model reads from at inference time.

The relationship between sources and sinks is rarely one-to-one. A common pattern is **fan-in** (many sources feeding one destination, like consolidating sales data from five regional systems into one BigQuery warehouse) or **fan-out** (one source feeding many destinations, like a single event stream powering both a real-time dashboard and a long-term analytics warehouse).

```
Fan-in:                          Fan-out:
Source A ─┐                              ┌→ Real-time dashboard
Source B ─┼→ BigQuery (sink)   Pub/Sub ──┼→ BigQuery (analytics)
Source C ─┘                              └→ Cloud Storage (archive)
```

**A critical practitioner distinction: source of truth vs. copy.** When you pull data from a source system, you're almost always creating a copy for analytical purposes. The original operational database remains the source of truth. This matters because if your pipeline has a bug, you can always re-run it against the source — but only if you haven't accidentally treated your copy as authoritative and let the original drift or get deleted.

> **Practitioner warning:** Document your sources and sinks formally — not just in code comments, but in a data catalog or shared document. I've worked on teams where nobody could answer "where does this BigQuery table actually come from?" six months after the original engineer left. That's not a hypothetical risk; it's the default outcome if you don't actively prevent it.

---

## 3. Defining Data Transformation Logic

Raw data is almost never immediately useful. **Transformation logic** is the set of rules that convert data from its raw, source-system shape into a shape that's useful for its destination.

Transformations generally fall into a few categories, and understanding the difference helps you reason about pipeline design:

**Structural transformations** change the _shape_ of data without changing its meaning — converting a JSON nested object into flat columns, pivoting rows into columns, or splitting one wide table into several normalized ones.

**Semantic transformations** change the _meaning or value_ of data — converting a timestamp from UTC to local time zone, standardizing "USA," "U.S.," and "United States" into a single consistent value, or converting currencies.

**Aggregations** summarize data — computing daily totals from individual transactions, or calculating a rolling 7-day average of sensor readings.

**Enrichment** adds context by joining data from a second source — adding a customer's loyalty tier to each of their transaction records by looking it up from a separate customer table.

Here's the foundational architectural decision every data engineer faces: **ETL versus ELT.**

```
ETL (Extract, Transform, Load)          ELT (Extract, Load, Transform)
─────────────────────────────           ──────────────────────────────
Source → Transform → Load               Source → Load → Transform
(transformation happens                 (raw data loaded first,
 before loading, often in                transformation happens
 the pipeline tool itself)               inside the warehouse, e.g.
                                          using BigQuery SQL)
```

**ETL** transforms data before it lands in the destination — common when you need to clean or restructure data significantly before a downstream system can use it, or when the destination system has limited compute power of its own.

**ELT** loads raw data first, then transforms it using the power of the destination system itself — increasingly popular because modern data warehouses like BigQuery have enormous compute power, and keeping raw data available lets you re-transform it later without re-extracting from the source.

> **Practitioner insight:** Most modern Google Cloud data platforms lean ELT — land raw data in BigQuery or Cloud Storage first, then transform using BigQuery SQL or BigQuery's Spark integration. This isn't a hard rule, but it's the dominant pattern in 2026 because it preserves your raw data as a safety net. If your transformation logic has a bug, you can fix the SQL and re-run — you don't need to re-extract from a fragile source system.

**Defining transformation logic on paper, before coding,** typically takes the form of a mapping document: source field → transformation rule → destination field. This sounds bureaucratic, but it's the artifact that prevents miscommunication between the engineer building the pipeline and the analyst who needs the output.

---

## 4. Networking Fundamentals

Data doesn't move through pipes made of nothing — it moves across networks, and how you architect that network matters enormously for both security and performance.

**Public vs. private connectivity** is the first decision. By default, many Google Cloud services communicate over the public internet (encrypted, but still routed through public infrastructure). For sensitive workloads, **Private Google Access** and **VPC Service Controls** let your resources communicate with Google Cloud APIs without ever leaving Google's private network backbone.

**VPC (Virtual Private Cloud)** is your own logically isolated network within Google Cloud. Most production data pipelines run inside a VPC, where you control IP ranges, firewall rules, and which resources can talk to which.

```
                    ┌─────────────── VPC ───────────────┐
                    │                                     │
[On-prem source] ──→│  [Dataflow workers] → [BigQuery]   │
   (via VPN or       │         ↓                          │
    Interconnect)    │  [Cloud Storage]                   │
                    │                                     │
                    └─────────────────────────────────────┘
```

**Hybrid connectivity** matters whenever your data sources live outside Google Cloud — in an on-premises data center, for instance. **Cloud VPN** provides an encrypted tunnel over the public internet (cheaper, moderate latency). **Cloud Interconnect** provides a dedicated physical or partner connection (more expensive, much higher throughput and lower latency). Choosing between them is a function of data volume and latency sensitivity: a nightly batch transfer of a few gigabytes is fine over VPN; continuous high-volume streaming from an on-prem Kafka cluster usually justifies Interconnect.

**Firewall rules and Private Service Connect** control which services can initiate connections to which others. A well-architected pipeline follows least-privilege networking — your Dataflow workers should only be able to reach the specific BigQuery datasets and Cloud Storage buckets they actually need, not your entire project.

> **Practitioner warning:** Networking issues are some of the hardest pipeline bugs to diagnose because they often fail silently or with unhelpful error messages — a job will simply hang, timeout, or fail with a generic permission-denied error. When a pipeline that worked yesterday suddenly can't reach its source, check firewall rules and VPC configuration before you assume your code is broken.

---

## 5. Data Encryption

Encryption is one of those topics that's invisible when done right and catastrophic when ignored. Two states of data matter here, and they require different protections.

**Encryption at rest** protects data sitting in storage — in a Cloud Storage bucket, a BigQuery table, or a Pub/Sub message that hasn't yet been delivered. Google Cloud encrypts all data at rest by default using Google-managed encryption keys, with no action required from you. For stricter requirements, you can supply **Customer-Managed Encryption Keys (CMEK)** through Cloud KMS, giving your organization direct control over key rotation and revocation. In the most sensitive scenarios — financial services, healthcare, defense — **Customer-Supplied Encryption Keys (CSEK)** let you manage keys entirely outside Google's infrastructure.

**Encryption in transit** protects data while it's moving — between your pipeline components, between a source system and Dataflow, or between Dataflow and BigQuery. Google Cloud encrypts all traffic between its own services automatically using TLS. The places you need to think actively about encryption in transit are the _edges_ of your system: connections to on-premises sources, third-party APIs, or external partners who may not enforce TLS by default.

```
Where encryption applies in a typical pipeline:

[On-prem DB] --TLS/VPN--> [Pub/Sub] --(internal, encrypted)--> [Dataflow]
                                                                     |
                                                          (internal, encrypted)
                                                                     ↓
                                                              [BigQuery]
                                                          (encrypted at rest,
                                                           CMEK optional)
```

**Field-level encryption and tokenization** go beyond whole-dataset encryption — sometimes you need specific sensitive fields (like Social Security numbers or credit card numbers) protected even from people who have legitimate access to the rest of the table. Google Cloud's **Sensitive Data Protection** (formerly Cloud DLP) can automatically discover, classify, and de-identify sensitive fields as part of your pipeline, replacing real values with tokens that can be reversed only by authorized processes.

> **Practitioner insight:** Default encryption is good, but it's not a substitute for thinking about _who can decrypt and read the data_, which is fundamentally an access control question (IAM), not purely an encryption one. Encryption protects against someone stealing the physical bytes; IAM protects against someone with legitimate system access misusing it. You need both.

---

## 6. Building the Pipelines

This is where planning becomes reality. Building a pipeline on Google Cloud generally follows one of three approaches, and the right one depends on your team's skills and the complexity of the task.

**Code-first development**, typically using Apache Beam (which we'll cover in depth in Section 8), gives you maximum flexibility. You write a program that explicitly defines every read, transform, and write step. This is the right choice when your transformation logic is complex, you need custom error handling, or you're integrating with unusual systems that don't have a pre-built connector.

**Template-based development** uses pre-built pipeline templates — Google provides dozens of ready-made Dataflow templates for common patterns (Pub/Sub to BigQuery, Cloud Storage to BigQuery, database change-data-capture, and more). You configure a few parameters and deploy, without writing pipeline code yourself. This dramatically lowers the barrier to entry for common scenarios.

**Visual/low-code development**, typically using Cloud Data Fusion, lets you build pipelines by dragging and dropping connectors and transformation blocks onto a canvas. This is the right choice for teams without deep programming expertise, or for standardizing common ETL patterns across many similar pipelines.

```
Pick your approach based on complexity and team skill:

Simple, standard pattern  →  Dataflow Template (fastest)
Complex custom logic      →  Apache Beam code (most flexible)
Non-technical team        →  Cloud Data Fusion (visual, low-code)
```

**The typical build workflow**, regardless of approach, follows these stages:

1. **Develop and test locally or on a small sample** — never write a pipeline against full production data on your first attempt
2. **Validate against a representative subset** — catch logic errors before they touch the whole dataset
3. **Deploy to a development environment** — run against a copy of real infrastructure, but isolated from production
4. **Promote to production** — ideally through an automated CI/CD process, which we'll cover in Section 13
5. **Monitor continuously** — pipelines that work on day one can break silently as source data evolves

> **Practitioner warning:** The single most common building mistake among beginners is developing directly against production data and production infrastructure. A bug in your transformation logic can corrupt a production table in minutes. Always have a development or staging environment, even if it's smaller and cheaper than production. The cost of that environment is trivial compared to the cost of a corrupted production dataset.

---

## 7. Data Cleansing

If transformation logic is about _reshaping_ data, **data cleansing** is about _fixing_ it. This is unglamorous work, but it's where data quality is won or lost.

**Common data quality problems and how pipelines address them:**

**Missing values.** A customer record with no email address, a sensor reading that failed to transmit. Your pipeline needs an explicit policy: drop the record, fill in a default value, or flag it for manual review. The wrong choice silently corrupts downstream analysis — averaging in zeros for missing numeric values, for instance, can drastically skew your statistics.

**Duplicate records.** The same event arriving twice due to a network retry, or the same customer entered into a CRM under two slightly different names. Deduplication logic — often based on a combination of business keys and timestamps — needs to be deliberate, not assumed.

**Invalid or out-of-range values.** An age field showing "-5" or "250," a date field showing a year of "1900" because of a default placeholder value that was never actually filled in. Validation rules catch these before they pollute your warehouse.

**Inconsistent formatting.** Phone numbers stored as "(555) 123-4567" in one source and "5551234567" in another. Without standardization, a downstream system trying to match records on phone number will simply fail to find matches that should exist.

**Schema drift.** A source system adds a new field, removes an old one, or changes a data type — and your pipeline either breaks or silently drops the new information. This is one of the most underestimated risks in production pipelines because it requires no malicious intent and no obvious error; it's simply what happens when systems evolve independently over time.

```
Data Cleansing Pipeline Stage

Raw Input
   ↓
[Validate schema] → fails? → quarantine for review
   ↓ passes
[Check for nulls/missing] → policy: drop / default / flag
   ↓
[Deduplicate] → based on business key + timestamp
   ↓
[Standardize formats] → phone numbers, dates, currency, casing
   ↓
[Range/sanity checks] → reject impossible values
   ↓
Clean Output
```

> **Practitioner insight:** Build a "quarantine" pattern into your pipelines — records that fail validation should be routed to a separate location for human review, not silently dropped and not allowed to corrupt the main dataset. This single pattern prevents two failure modes simultaneously: silent data loss, and silent data corruption.

> **Practitioner warning:** Data cleansing rules become stale. The validation logic you wrote when the business had 10,000 customers in one country may actively reject valid data once you expand internationally — a phone number format check tuned for US numbers will flag every legitimate international number as invalid. Revisit cleansing rules whenever your business or data sources change meaningfully.

---

## 8. Identifying the Services

Google Cloud offers a deep toolbox for data ingestion and processing. Choosing the right service — or the right combination — is one of the most consequential decisions a data engineer makes. Let's go through each one and, critically, understand _when_ you'd reach for it.

### Dataflow

**Dataflow** is Google Cloud's fully managed, serverless service for executing **Apache Beam** pipelines. The word "serverless" here matters: you never provision or manage virtual machines. You submit a pipeline definition, and Dataflow automatically provisions workers, scales them up and down based on load, and tears them down when the job finishes.

Dataflow's defining strength is its **unified model for both batch and streaming** — the same programming model (Apache Beam) handles "process this file once" and "process this never-ending stream of events" with largely the same code. This is genuinely valuable: many teams start with a batch pipeline and later need to convert it to streaming as business requirements evolve, and Beam's unified model makes that transition far less painful than switching frameworks entirely.

### Apache Beam

**Apache Beam** isn't a Google Cloud service — it's an open-source programming model (now widely adopted across the industry) for defining data pipelines. You write your pipeline once using the Beam SDK (available in Java, Python, and Go), and you can then run it on different execution engines, called **runners** — Dataflow is one runner, but Apache Spark and Apache Flink can also run Beam pipelines.

This portability matters more than it might initially seem. If you ever need to move off Google Cloud, or run the same logic in a different environment, your Beam pipeline code doesn't need a rewrite — only the runner configuration changes.

**The core Beam concepts** you need to know:

- A **PCollection** is a distributed dataset — the thing flowing through your pipeline
- A **PTransform** is an operation applied to a PCollection — filtering, mapping, grouping, and so on
- **Bounded** PCollections have a known, fixed size (batch); **unbounded** PCollections are continuous (streaming)

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

options = PipelineOptions([
    '--runner=DataflowRunner',
    '--project=my-project',
    '--region=us-central1',
    '--temp_location=gs://my-bucket/temp/',
])

with beam.Pipeline(options=options) as p:
    (
        p
        | 'ReadLogs' >> beam.io.ReadFromText('gs://my-logs/2026/06/*.json')
        | 'Parse' >> beam.Map(lambda line: json.loads(line))
        | 'FilterErrors' >> beam.Filter(lambda r: r.get('level') == 'ERROR')
        | 'WriteToBQ' >> beam.io.WriteToBigQuery('my-project:logs.errors')
    )
```

### Dataproc

**Dataproc** is Google Cloud's managed service for **Apache Spark and Hadoop**. If Dataflow is serverless-first, Dataproc gives you a managed cluster of VMs running the open-source big data tools your team may already know.

The decision between Dataflow and Dataproc usually comes down to one question: **does your team already have Spark/Hadoop expertise and existing code?** If yes, Dataproc lets you run that code with minimal changes. If you're building from scratch, Dataflow's serverless model means less operational overhead.

**Dataproc Serverless** (now part of Google Cloud Serverless for Apache Spark) bridges the gap — you get Spark's capabilities without managing cluster lifecycle, paying only for the compute consumed during job execution, much like Dataflow's billing model.

|Factor|Dataflow|Dataproc|
|---|---|---|
|Programming model|Apache Beam|Spark / Hadoop / Spark SQL|
|Infrastructure management|None (fully serverless)|Cluster-based (or serverless mode)|
|Best for|New pipelines, unified batch+streaming|Existing Spark/Hadoop investment|
|Ecosystem|Beam connectors|Full Spark ecosystem (MLlib, Spark SQL)|
|Typical team profile|Cloud-native data engineers|Teams migrating from on-prem Hadoop|

### Cloud Data Fusion

**Cloud Data Fusion** is a fully managed, visual data integration service built on the open-source CDAP framework. Its defining feature is a **drag-and-drop interface** with prebuilt connectors for hundreds of data sources — databases, SaaS applications, file systems — letting you build ETL/ELT pipelines with minimal or no code.

Data Fusion is the right tool when you need to standardize pipeline-building across a team with mixed technical skill levels, or when you're integrating with many different systems that already have prebuilt connectors, making custom coding unnecessary.

### BigQuery

**BigQuery** is Google Cloud's serverless, columnar data warehouse — and increasingly, it's also a processing engine in its own right. Beyond storing and querying data with SQL, BigQuery now supports running **Spark code directly inside BigQuery Studio**, supports **continuous queries** for real-time analytical processing, and offers **BigQuery ML** for training models directly with SQL.

For many ELT-style pipelines, BigQuery is both the sink _and_ the transformation engine — raw data lands in BigQuery, and SQL (or Spark within BigQuery) does the transformation work, eliminating a separate processing layer entirely.

### Pub/Sub

**Pub/Sub** is Google Cloud's globally distributed, fully managed messaging service — the backbone of event-driven and streaming architectures. Publishers send messages to a topic; subscribers receive them, either by pulling or via push delivery. Pub/Sub provides at-least-once delivery, dead-letter queues for handling problematic messages, and now supports **Single Message Transforms (SMTs)** for lightweight, real-time message validation and enrichment without needing a separate processing step.

Pub/Sub is almost always the entry point for streaming data — sensor events, application logs, clickstream data — which then typically flows into Dataflow for processing before landing in BigQuery or Cloud Storage.

### Apache Spark and the Hadoop Ecosystem

**Apache Spark** is an open-source distributed processing engine, prized for its speed (processing data largely in-memory) and its rich ecosystem — Spark SQL, MLlib for machine learning, and Spark Streaming. On Google Cloud, you typically run Spark via Dataproc or the newer Serverless for Apache Spark.

The broader **Hadoop ecosystem** (HDFS for distributed storage, MapReduce for processing, Hive for SQL-like querying) represents an earlier generation of big data tooling. Many enterprises still run substantial Hadoop workloads, and Dataproc exists largely to give those teams a managed, cloud-native path without forcing an immediate rewrite.

### Apache Kafka

**Apache Kafka** is the most widely adopted open-source distributed event streaming platform in the industry, known for extremely high throughput and a partition-based model for horizontal scaling. On Google Cloud, you have two paths: run Kafka yourself (self-managed), or use **Google Cloud Managed Service for Apache Kafka**, which handles cluster operations for you while preserving full Kafka API compatibility.

**Kafka versus Pub/Sub** is a common point of confusion for beginners. Both are messaging/streaming systems, but they have different scaling models — Kafka uses partitions (subscribers must coordinate around partition assignment), while Pub/Sub leases individual messages to subscribers, removing that coordination burden. Many organizations choose Pub/Sub for new, cloud-native projects because it's simpler to operate, while organizations with existing Kafka investments either migrate or use **Managed Kafka Connect** to bridge the two ecosystems.

```
Service Decision Map

Need to ingest streaming events?           → Pub/Sub (or Managed Kafka)
Need to process/transform that stream?     → Dataflow (Apache Beam)
Have existing Spark/Hadoop code?           → Dataproc
Need visual, low-code pipeline building?   → Cloud Data Fusion
Need a warehouse + can transform in SQL?   → BigQuery (ELT pattern)
Need to orchestrate multi-step workflows?  → Cloud Composer (Section 12)
```

> **Practitioner insight:** Real production architectures almost always combine several of these services rather than choosing just one. A very common pattern: Pub/Sub ingests streaming events → Dataflow processes and enriches them → BigQuery stores and serves the results → Cloud Composer orchestrates the surrounding batch jobs. Knowing each tool deeply matters less than knowing how to compose them correctly.

---

## 9. Transformations

We touched on transformation logic conceptually in Section 3 — now let's get concrete about _how_ transformations are actually implemented across these services.

**SQL-based transformations** are the dominant pattern when your data already lives in BigQuery. SQL is accessible to a much broader range of practitioners than pipeline code, and BigQuery's query engine is extraordinarily powerful for aggregations, joins, and window functions at scale.

```sql
-- A typical BigQuery transformation: daily revenue by region
SELECT
  DATE(transaction_timestamp) AS sale_date,
  region,
  SUM(amount) AS total_revenue,
  COUNT(*) AS transaction_count
FROM `my-project.raw.transactions`
WHERE amount > 0  -- basic sanity filter
GROUP BY sale_date, region
ORDER BY sale_date DESC
```

**Programmatic transformations** in Apache Beam or Spark are necessary when your logic is too complex for SQL, when you need custom error handling, or when you're processing unstructured or semi-structured data (like parsing free-text log files) before it ever reaches a structured destination.

```python
# Beam transformation example: enrich and reshape streaming events
def enrich_event(event, customer_lookup):
    event['customer_tier'] = customer_lookup.get(event['customer_id'], 'unknown')
    event['processed_at'] = datetime.utcnow().isoformat()
    return event

pipeline | 'Enrich' >> beam.Map(enrich_event, customer_lookup=side_input)
```

**Visual transformations** in Cloud Data Fusion let you chain together prebuilt transformation blocks (filter, join, aggregate, format conversion) on a canvas, generating the underlying Spark code automatically.

**A practitioner principle worth internalizing: push transformation logic as close to the consumer as reasonably possible, but keep raw data preserved.** This is the philosophical core of the ELT pattern — don't discard the original data in the name of efficiency. Storage is cheap; lost raw data is often unrecoverable.

> **Practitioner warning:** Transformation logic scattered across SQL views, Beam pipelines, and Data Fusion pipelines — with no single source of truth for "how is this metric calculated" — is one of the most common causes of conflicting numbers in different dashboards. When two reports disagree, it's almost always because someone implemented the same transformation differently in two different places. Centralize and document your transformation definitions.

---

## 10. Data Acquisition and Import

**Data acquisition** is the practical, often unglamorous work of actually getting data out of its source system and into your cloud environment for the first time.

**Batch import patterns** include uploading files directly to Cloud Storage (simple, but manual unless automated), using the **BigQuery Data Transfer Service** for scheduled, managed imports from common SaaS sources (Google Ads, YouTube, Google Analytics, and others), and using **Database Migration Service** or **Datastream** for change-data-capture from operational databases.

**Datastream** deserves particular attention as a modern pattern: rather than periodically re-extracting an entire database table, Datastream captures _changes_ to source databases (inserts, updates, deletes) in near real time and streams them to BigQuery or Cloud Storage. This is dramatically more efficient than repeated full extracts, and it now supports replication into **BigLake Iceberg tables**, enabling open lakehouse architectures where the same data can be queried by multiple processing engines.

**Streaming import patterns** rely on Pub/Sub (for application and event data) or Managed Kafka (for high-throughput, partition-based streaming) as the entry point, typically followed by Dataflow for processing.

**One-time historical loads versus ongoing incremental loads** is a distinction every pipeline needs to handle explicitly. The first time you connect to a new source, you often need to import years of historical data — a fundamentally different operation, with different volume and performance characteristics, than the ongoing daily or streaming updates that follow. Many beginners build a pipeline that handles incremental updates well but breaks (or takes days) when asked to process the initial historical backfill.

```
Acquisition Pattern Selection

New SaaS source (Salesforce, Stripe, etc.) → BigQuery Data Transfer Service
On-prem database, need real-time sync     → Datastream (CDC)
Files arriving periodically                → Cloud Storage + scheduled trigger
Continuous application events              → Pub/Sub
High-throughput existing Kafka system      → Managed Kafka / Kafka Connect
```

> **Practitioner insight:** Always test your acquisition pattern against the _full_ expected historical volume before going live, not just a recent sample. A connector that handles "yesterday's data" in 30 seconds might take 14 hours to handle "the last 5 years," and you want to discover that during testing, not during a live cutover.

---

## 11. Integrating with New Data Sources

Businesses change. New systems get adopted, partnerships form, acquisitions happen — and your pipelines need to absorb new data sources without destabilizing what already works.

**The integration checklist for any new source:**

**Understand the source's data contract.** What's the schema? Does it change frequently? Is there documentation, or do you need to reverse-engineer it from sample data? Sources without a stable, documented schema are higher-risk and deserve extra defensive coding (schema validation, quarantine patterns) from day one.

**Determine the access pattern.** Does the source offer an API, a database connection, file exports, or a webhook/event stream? This determines which Google Cloud service is the natural fit — an API typically suggests a custom Beam pipeline or a Cloud Function trigger; a database often suggests Datastream; a SaaS platform might already have a BigQuery Data Transfer Service connector built for it.

**Assess data quality at the source.** Before building anything, pull a sample and look for the cleansing issues described in Section 7. It's far cheaper to discover that a source has messy timestamps before you've built three downstream systems depending on them being clean.

**Plan for source instability.** External sources — especially third-party APIs — change without warning: rate limits get added, fields get renamed, authentication mechanisms get upgraded. Build your integration with the assumption that it _will_ break eventually, with monitoring and alerting that tells you quickly when it does, rather than discovering the failure when a business stakeholder asks why a dashboard hasn't updated in a week.

```
New Source Integration Workflow

1. Document the data contract (schema, update frequency, access method)
2. Identify the right ingestion service (Datastream / Pub/Sub / Data Fusion / custom)
3. Build in a dev/staging environment first
4. Validate data quality against real samples
5. Add monitoring & alerting for the new pipeline
6. Document in the data catalog
7. Promote to production via CI/CD
```

> **Practitioner warning:** Resist the temptation to hard-code assumptions about a new source's data into your pipeline — for instance, assuming a field will always be present, or that values fall within a certain range, without explicitly validating it. New sources are exactly where schema drift and unexpected values are most likely to appear, precisely because you don't yet have months of operational history to know what "normal" looks like.

---

## 12. Job Automation and Orchestration

Individual pipelines rarely run in isolation. A real-world data platform involves dozens or hundreds of jobs with dependencies on each other — "don't run the daily sales report job until the data ingestion job has completed successfully." **Orchestration** is the discipline of managing those dependencies, schedules, retries, and failure handling.

### Cloud Composer

**Cloud Composer** is Google Cloud's fully managed version of **Apache Airflow**, the industry-standard open-source orchestration tool. You define workflows as **DAGs (Directed Acyclic Graphs)** — Python code describing tasks and their dependencies — and Composer handles scheduling, retries, and monitoring.

```python
from airflow import DAG
from airflow.providers.google.cloud.operators.dataflow import DataflowTemplatedJobStartOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime, timedelta

with DAG(
    'daily_sales_pipeline',
    schedule_interval='0 2 * * *',  # 2 AM daily
    start_date=datetime(2026, 1, 1),
    default_args={'retries': 3, 'retry_delay': timedelta(minutes=5)},
) as dag:

    ingest = DataflowTemplatedJobStartOperator(
        task_id='ingest_sales_data',
        template='gs://dataflow-templates/latest/GCS_Text_to_BigQuery',
    )

    transform = BigQueryInsertJobOperator(
        task_id='transform_sales_data',
        configuration={"query": {"query": "CALL my_dataset.transform_sales()"}},
    )

    ingest >> transform  # 'transform' only runs after 'ingest' succeeds
```

**Why DAGs matter as a concept, not just syntax:** a Directed Acyclic Graph forces you to be explicit about dependencies. Task B can't run before Task A if B depends on A's output. This sounds obvious, but in practice, ungoverned scripts (cron jobs running independently, with implicit and undocumented timing assumptions) are a major source of subtle, hard-to-diagnose data quality bugs — a report generates using yesterday's incomplete data because the ingestion job that should have finished first was still running.

**Cloud Composer 3** now offers access to **Apache Airflow 3**, bringing meaningful improvements: DAG versioning (so you can see exactly which version of a workflow ran on a given day — valuable for debugging and audits), scheduler-managed backfills (simplifying the historical reprocessing scenario discussed in Section 10), and a modernized UI.

A newer, complementary option is **serverless Composer**, designed to simplify orchestration setup further by removing infrastructure management entirely and focusing purely on workflow definition, with a large library of prebuilt connectors.

### Cloud Workflows

**Cloud Workflows** is a lighter-weight orchestration service, designed for connecting serverless services and APIs rather than complex, long-running data pipelines. Where Composer/Airflow shines at orchestrating many interdependent, scheduled data jobs, Workflows is better suited to simpler, event-triggered sequences — "when a file lands in Cloud Storage, trigger a Cloud Function, then call an API, then write a result."

|Factor|Cloud Composer (Airflow)|Cloud Workflows|
|---|---|---|
|Best for|Complex, scheduled, multi-step data pipelines|Lightweight, event-driven service orchestration|
|Complexity|Higher — full DAG authoring in Python|Lower — YAML/JSON-based workflow definitions|
|Typical trigger|Schedule (cron-like)|Event (Pub/Sub message, HTTP call, file upload)|
|Ecosystem|Deep GCP + open-source Airflow operator library|Native GCP service integrations, simpler scope|

> **Practitioner insight:** A common mistake is reaching for Composer/Airflow for every orchestration need, even simple ones, because it's the "default" tool people know. If your need is genuinely simple — trigger one function after one event — Cloud Workflows or even a Cloud Function trigger is lighter-weight, cheaper, and easier to maintain than spinning up a full Airflow environment.

> **Practitioner warning:** Orchestration tools manage _when_ jobs run, but they don't automatically guarantee _data correctness_. A pipeline can run successfully (no errors, all green checkmarks) while still producing wrong results because of a logic bug. Build data quality checks (row counts, null checks, range validations) as explicit tasks within your DAGs — don't rely on "the job didn't fail" as a proxy for "the data is correct."

---

## 13. CI/CD

**Continuous Integration / Continuous Deployment (CI/CD)** brings software engineering discipline to data pipeline development — and it's the difference between a pipeline that one person understands and maintains by hand, versus a pipeline a whole team can safely modify.

**Why data pipelines need CI/CD just as much as application code:** pipeline code has bugs, just like any other code. Without automated testing and controlled deployment, a small change — a typo in a SQL transformation, an off-by-one error in a date filter — can silently corrupt production data for days before anyone notices.

**The typical CI/CD workflow for data pipelines on Google Cloud:**

```
Developer writes pipeline code
         ↓
[Git commit / pull request]
         ↓
[Cloud Build triggers automatically]
         ↓
Run automated tests:
  - Unit tests (transformation logic in isolation)
  - Integration tests (against a sample dataset)
  - Schema validation
         ↓
Tests pass? ──No──→ Block merge, notify developer
         ↓ Yes
[Deploy to staging environment]
         ↓
Run pipeline against staging data, validate output
         ↓
[Manual or automated approval]
         ↓
[Deploy to production via Cloud Build/Artifact Registry]
         ↓
[Monitor production run closely]
```

**Key components on Google Cloud:**

**Cloud Build** is Google Cloud's CI/CD service — it can run automatically on every git push, executing your test suite, building any necessary containers, and deploying updated pipeline code or Dataflow templates.

**Artifact Registry** stores versioned build artifacts — container images for custom Beam/Dataflow workers, for instance — ensuring that what you tested is exactly what gets deployed, with no drift between environments.

**Infrastructure as Code (IaC)**, typically using Terraform, extends CI/CD principles beyond pipeline code to the infrastructure itself — your Pub/Sub topics, BigQuery datasets, Composer environments, and IAM permissions are defined in version-controlled configuration files rather than manually clicked together in the console. This means your entire data platform's configuration is reviewable, auditable, and reproducible.

**Testing data pipelines specifically** requires some adaptation from typical software testing:

- **Unit tests** validate individual transformation functions against known inputs and expected outputs — does this date-parsing function correctly handle a malformed date string?
- **Integration tests** run a small version of the full pipeline against a representative sample dataset, checking that the end-to-end behavior is correct
- **Schema tests** validate that source and destination schemas match expectations, catching schema drift (Section 7) before it reaches production
- **Data quality tests**, run post-deployment, validate row counts, null rates, and value distributions against historical baselines — catching problems that only manifest with real production data volume

> **Practitioner insight:** "Tested in staging" for a data pipeline often means something different than for application code — staging data rarely perfectly represents the messiness of production data at full scale. Build a habit of running new pipeline versions in **shadow mode** when possible: deploy the new version alongside the old one, compare outputs, and only fully cut over once you've confirmed the new version produces consistent (or deliberately, correctly different) results.

> **Practitioner warning:** Pipelines deployed by hand, through console clicks, with no record of what changed or when, are extremely common in early-stage teams — and extremely painful once something breaks and nobody can answer "what changed recently?" The investment in CI/CD pays for itself the very first time you need to roll back a bad deployment in minutes instead of hours of manual archaeology.

---

## 14. Summary / Quick Reference

### The End-to-End Picture

```
┌────────────────────────────────────────────────────────────────────┐
│                     DATA INGESTION & PROCESSING                      │
│                                                                       │
│  PLAN                                                                │
│  └── Batch vs. streaming, latency needs, volume, consumers          │
│                                                                       │
│  SOURCES & SINKS                                                     │
│  └── Operational DBs, APIs, files, streams → warehouses, stores     │
│                                                                       │
│  ACQUIRE                                                              │
│  ├── Datastream (CDC)        ├── BigQuery Data Transfer Service      │
│  └── Pub/Sub / Kafka (streaming)                                     │
│                                                                       │
│  PROCESS                                                              │
│  ├── Dataflow (Apache Beam) — serverless, unified batch+stream       │
│  ├── Dataproc — managed Spark/Hadoop                                 │
│  ├── Cloud Data Fusion — visual, low-code ETL                        │
│  └── BigQuery — SQL-based ELT transformation                         │
│                                                                       │
│  CLEANSE & TRANSFORM                                                  │
│  └── Validation, deduplication, standardization, enrichment          │
│                                                                       │
│  SECURE                                                               │
│  └── VPC/networking, encryption at rest & in transit, IAM, DLP       │
│                                                                       │
│  ORCHESTRATE                                                          │
│  ├── Cloud Composer (Airflow) — complex, scheduled DAGs              │
│  └── Cloud Workflows — lightweight, event-driven                     │
│                                                                       │
│  DEPLOY SAFELY                                                        │
│  └── CI/CD via Cloud Build, Artifact Registry, Terraform/IaC         │
└────────────────────────────────────────────────────────────────────┘
```

---

### Key Decision Guide

|Question|Answer|
|---|---|
|"Batch or streaming?"|Default to batch unless there's a genuine low-latency business need.|
|"Dataflow or Dataproc?"|Dataflow for new/serverless work; Dataproc if you have existing Spark/Hadoop code.|
|"ETL or ELT?"|Default to ELT (land raw in BigQuery, transform with SQL) — preserves raw data as a safety net.|
|"Pub/Sub or Kafka?"|Pub/Sub for new cloud-native projects (simpler ops); Managed Kafka if you have existing Kafka investment.|
|"Composer or Workflows?"|Composer for complex, scheduled, multi-step data pipelines; Workflows for lightweight, event-driven tasks.|
|"Where do I catch bad data?"|Build an explicit quarantine/validation stage — never let it fail silently.|
|"How do I avoid corrupting production?"|Dev/staging environments, CI/CD, and shadow-mode testing before full cutover.|

---

### The Golden Rules of Data Pipelines (Practitioner Edition)

1. **Plan before you build.** The cheapest bug to fix is the one caught on a whiteboard, not in production.
    
2. **Preserve raw data.** Storage is cheap. Once raw data is gone, you can't fix transformation bugs retroactively.
    
3. **Quarantine, don't discard.** Bad records should be visible and reviewable, never silently dropped.
    
4. **Default to batch and ELT.** Add streaming and ETL complexity only when there's a genuine requirement for it.
    
5. **Document your sources and transformations.** "Where does this number come from?" should always have a clear answer.
    
6. **Never test against production.** Always have a dev/staging environment, however small.
    
7. **Automate deployment.** Manual, undocumented pipeline changes are the root cause of most "nobody knows why this broke" incidents.
    
8. **Monitor for drift, not just failure.** A pipeline can run successfully and still produce silently wrong results — build data quality checks as explicit, monitored steps.
    

---

### Quick Terminology Reference

|Term|Plain-English Definition|
|---|---|
|Source / Sink|Where data comes from / where it ends up|
|Batch processing|Handling data in discrete chunks (e.g., "yesterday's orders")|
|Stream processing|Handling data continuously, as it arrives|
|ETL / ELT|Transform-before-load vs. load-then-transform-in-warehouse|
|PCollection / PTransform|Apache Beam's terms for a dataset / an operation on that dataset|
|Runner|The engine that actually executes an Apache Beam pipeline (e.g., Dataflow)|
|CDC (Change Data Capture)|Streaming only the _changes_ to a source database, not full re-extracts|
|DAG|Directed Acyclic Graph — a dependency map of tasks used in orchestration|
|Schema drift|When a source system's structure changes without your pipeline being updated|
|CMEK|Customer-Managed Encryption Keys — you control the key, Google does the encrypting|
|Quarantine pattern|Routing invalid records to a separate location for review instead of dropping them|
|Shadow mode|Running a new pipeline version alongside the old one to compare outputs before cutover|

---

_These notes reflect the Google Cloud data and AI ecosystem as of mid-2026, including Cloud Composer 3 / Airflow 3, BigQuery's expanded Spark and continuous query capabilities, and Managed Service for Apache Kafka. Always verify current service capabilities and pricing at cloud.google.com, as this space evolves quickly._