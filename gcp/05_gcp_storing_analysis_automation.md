# GCP Data Engineering Review
## Storing Data · Preparing for Analysis · Maintaining and Automating Workloads

> **Level:** Intermediate
> **Who this is for:** Students preparing for real-world GCP data engineering work or the Professional Data Engineer certification exam.
> **How to use this guide:** Concept first, GCP tools second, then a practical example or decision framework you can apply directly.

---

## Table of Contents

### Part A — Storing the Data
1. [Selecting Storage Systems](#1-selecting-storage-systems)
2. [Choosing Managed Services](#2-choosing-managed-services)
3. [Planning for Storage Costs and Performance](#3-planning-for-storage-costs-and-performance)
4. [Lifecycle Management of Data](#4-lifecycle-management-of-data)
5. [Planning for Using a Data Warehouse](#5-planning-for-using-a-data-warehouse)
6. [Using a Data Lake](#6-using-a-data-lake)
7. [Designing for a Data Mesh](#7-designing-for-a-data-mesh)

### Part B — Preparing and Using Data for Analysis
8. [Optimizing Resources](#8-optimizing-resources)
9. [Preparing Data for Visualization](#9-preparing-data-for-visualization)
10. [Sharing Data](#10-sharing-data)
11. [Exploring and Analyzing Data](#11-exploring-and-analyzing-data)

### Part C — Maintaining and Automating Data Workloads
12. [Designing Automation and Repeatability](#12-designing-automation-and-repeatability)
13. [Maintaining Awareness of Failures and Mitigating Impact](#13-maintaining-awareness-of-failures-and-mitigating-impact)
14. [Monitoring and Troubleshooting Processes](#14-monitoring-and-troubleshooting-processes)
15. [Organizing Workloads Based on Business Requirements](#15-organizing-workloads-based-on-business-requirements)

---

# Part A — Storing the Data

---

## 1. Selecting Storage Systems

### What Is It?

Choosing a storage system is one of the most consequential decisions in data architecture. Pick the wrong one and you pay in performance, cost, operational complexity, or all three. The right storage system is determined by the **access pattern** — not the data volume alone.

### The Core Question to Ask First

> "How will this data be read and written?"

The answer drives everything else.

```
One record at a time, by key, in milliseconds?   → Operational / NoSQL store
Millions of rows, full-column scans, SQL?        → Analytical warehouse
Files, blobs, images, raw CSVs?                  → Object storage
Structured rows, joins, ACID transactions?       → Relational database
Key-value pairs with microsecond reads?          → In-memory cache
```

### The Storage Decision Framework

Work through these five dimensions for any storage decision:

```
1. Access pattern
   Point lookup (by key)?          → Bigtable, Firestore, Cloud SQL
   Analytical scan (full columns)? → BigQuery
   File read/write?                → Cloud Storage
   Cached / ephemeral?             → Memorystore

2. Latency requirement
   < 10ms?     → Bigtable, Memorystore
   < 100ms?    → Firestore, Cloud SQL, Spanner
   Seconds OK? → BigQuery, Cloud Storage

3. Consistency requirement
   Strong ACID?        → Spanner, Cloud SQL, AlloyDB
   Eventual OK?        → Bigtable, Cloud Storage
   Per-document ACID?  → Firestore

4. Scale
   Gigabytes:    Cloud SQL
   Terabytes:    Spanner, BigQuery, Bigtable
   Petabytes:    BigQuery, Cloud Storage, Bigtable

5. Schema
   Fixed schema, structured?     → Cloud SQL, Spanner, BigQuery
   Flexible / evolving schema?   → Firestore, Bigtable
   Schema-on-read?               → Cloud Storage (raw files)
```

### The GCP Storage Landscape at a Glance

```
┌─────────────────────────────────────────────────────┐
│                   GCP Storage Services               │
├──────────────┬──────────────────────────────────────┤
│  RELATIONAL  │  Cloud SQL · Spanner · AlloyDB        │
│  (OLTP)      │  Structured, ACID, joins, SQL         │
├──────────────┼──────────────────────────────────────┤
│  ANALYTICAL  │  BigQuery                             │
│  (OLAP)      │  Columnar, petabyte-scale SQL         │
├──────────────┼──────────────────────────────────────┤
│  NoSQL       │  Bigtable · Firestore                 │
│  (Wide-col / │  High throughput, flexible schema,    │
│  Document)   │  low-latency key lookups              │
├──────────────┼──────────────────────────────────────┤
│  OBJECT      │  Cloud Storage (GCS)                  │
│              │  Unstructured files, blobs, backups   │
├──────────────┼──────────────────────────────────────┤
│  IN-MEMORY   │  Memorystore (Redis / Valkey)         │
│              │  Sub-millisecond cache, session store │
└──────────────┴──────────────────────────────────────┘
```

### Common Anti-Patterns to Avoid

```
❌ Using BigQuery for single-row lookups
   → BigQuery scans millions of rows even for one result; use Bigtable or Firestore

❌ Using Cloud SQL for petabyte analytics
   → A single PostgreSQL instance won't parallelize; use BigQuery

❌ Storing structured, frequently-joined data in GCS as CSV
   → CSV on GCS has no indexes, no types, no SQL; load it into BigQuery first

❌ Using Bigtable for complex multi-column queries
   → Bigtable excels at single-key lookups, not analytical queries

❌ Storing ML model artifacts in Firestore
   → Binary blobs belong in GCS; Firestore is for structured documents
```

### Key Takeaway

No single storage service is best for everything. A mature data platform typically uses three to five storage services simultaneously — each doing what it does best. Start with the access pattern, then choose the service.

---

## 2. Choosing Managed Services

### What Is It?

GCP's managed storage services handle provisioning, patching, replication, and scaling automatically. This section covers the six core services in depth — what each one is, how it works, and when to use it.

---

### Cloud Storage (GCS)

**What it is:** Object storage for any file — CSVs, Parquet, images, model artifacts, backups, logs. Think of it as an infinitely scalable file system.

**How it works:** Files (objects) are stored in buckets. Each object has a key (its path), metadata, and binary content. There are no directories — the `/` in a path is just part of the key name.

**Storage classes:**

```
Standard    → Frequently accessed data. Highest cost, no retrieval fee.
Nearline    → Accessed < once per month. Lower storage cost, small retrieval fee.
Coldline    → Accessed < once per quarter. Lower cost, higher retrieval fee.
Archive     → Accessed < once per year. Lowest cost, highest retrieval fee.
```

**When to use it:**

- Raw data landing zone (ingest files from upstream systems)
- Staging between pipeline stages
- Data lake storage (Parquet/Avro files)
- Storing ML model artifacts, logs, backups
- Serving static files or media

```bash
# Create a bucket in a specific region
gsutil mb -l us-central1 -c STANDARD gs://my-data-lake/

# Upload a file
gsutil cp local_file.csv gs://my-data-lake/raw/sales/2024-01-15/

# List objects with their size and storage class
gsutil ls -l gs://my-data-lake/raw/

# Copy an entire directory recursively
gsutil -m cp -r ./local_data/ gs://my-data-lake/raw/

# Make a file publicly readable (use with caution)
gsutil acl ch -u AllUsers:R gs://my-public-bucket/report.pdf
```

---

### BigQuery

**What it is:** A fully managed, serverless data warehouse. You run SQL; GCP handles the distributed compute automatically. No clusters to spin up, no indexes to tune.

**How it works:** BigQuery stores data in a columnar format called Capacitor. When you run a query, it reads only the columns referenced — this is why selecting `SELECT *` on a wide table is expensive and selecting only needed columns is cheap.

**When to use it:**

- Analytics on structured data at any scale
- Data warehouse for reporting and dashboards
- ML feature engineering and training data preparation
- Log analysis, event analytics, marketing attribution

```sql
-- BigQuery pricing is based on bytes scanned
-- Always select only the columns you need

-- ❌ Expensive: scans the entire table
SELECT * FROM `my_project.sales.orders` WHERE year = 2024;

-- ✅ Cheap: scans only three columns
SELECT order_id, amount, customer_id
FROM `my_project.sales.orders`
WHERE year = 2024;

-- Partition tables by date to avoid scanning entire history
CREATE TABLE my_dataset.orders
PARTITION BY DATE(order_date)
CLUSTER BY customer_id, status
AS SELECT * FROM my_dataset.orders_raw;

-- With partitioning, this scans only one day's data
SELECT order_id, amount
FROM my_dataset.orders
WHERE order_date = '2024-01-15';
```

---

### Cloud Bigtable

**What it is:** A fully managed, wide-column NoSQL database designed for massive throughput at low latency. Based on the same technology as Google's internal Bigtable (used for Gmail, Google Maps).

**How it works:** Data is stored in rows, each identified by a unique row key. Rows are sorted lexicographically by key. There are no joins, no SQL, and no secondary indexes — all access patterns must be designed around the row key.

**Key design rule:** The row key is everything. Design it to support your most frequent access pattern.

**When to use it:**

- Time-series data (IoT sensors, application metrics, financial tick data)
- User profile stores with high read/write throughput
- Personalization and recommendation feature stores
- Any workload needing < 10ms reads at millions of QPS

```python
from google.cloud import bigtable
from google.cloud.bigtable import column_family, row_filters

client   = bigtable.Client(project="my-project", admin=True)
instance = client.instance("my-instance")
table    = instance.table("sensor-readings")

# Row key design for time-series: reverse timestamp + sensor ID
# Reverse timestamp ensures newest data is at the top (avoids hotspotting)
import time
def make_row_key(sensor_id: str) -> str:
    reversed_ts = str(9999999999 - int(time.time()))
    return f"{sensor_id}#{reversed_ts}"

# Write a sensor reading
row_key = make_row_key("sensor-001").encode()
row = table.direct_row(row_key)
row.set_cell(
    column_family_id="readings",
    column="temperature",
    value=b"23.4",
)
row.set_cell("readings", "humidity", b"65")
row.commit()

# Read the latest 10 readings for a sensor
prefix = "sensor-001#".encode()
rows = table.read_rows(
    row_set=None,
    filter_=row_filters.RowKeyRegexFilter(b"sensor-001#.*"),
    limit=10,
)
for row in rows:
    for cf, cols in row.cells.items():
        for col, cells in cols.items():
            print(f"  {col.decode()}: {cells[0].value.decode()}")
```

**Bigtable vs BigQuery:**

```
Bigtable:  "Give me the last 10 readings for sensor-001"   → milliseconds
BigQuery:  "What is the average temperature across all sensors last month?" → seconds
```

They complement each other. Use both.

---

### Cloud Spanner

**What it is:** A globally distributed relational database with ACID transactions and horizontal scalability. Combines the relational model of SQL Server/PostgreSQL with the scale of NoSQL.

**How it works:** Spanner uses TrueTime (Google's globally synchronized clock) to guarantee external consistency across regions. You can run a transaction that spans nodes in Tokyo and London and it will be globally consistent.

**When to use it:**

- Global financial systems (inventory, orders, banking)
- Any workload that needs both ACID and horizontal scale
- Systems that have outgrown a single Cloud SQL instance
- Multi-region applications needing < 10ms reads globally

```python
from google.cloud import spanner

client   = spanner.Client(project="my-project")
instance = client.instance("my-instance")
database = instance.database("my-database")

# ACID transaction: transfer funds between accounts
def transfer_funds(transaction, from_account, to_account, amount):
    # Read current balances
    from_row = transaction.execute_sql(
        "SELECT balance FROM Accounts WHERE account_id = @id",
        params={"id": from_account},
        param_types={"id": spanner.param_types.STRING},
    ).one()

    if from_row[0] < amount:
        raise ValueError("Insufficient funds")

    # Debit source, credit destination — atomically
    transaction.execute_update(
        "UPDATE Accounts SET balance = balance - @amt WHERE account_id = @id",
        params={"amt": amount, "id": from_account},
        param_types={"amt": spanner.param_types.FLOAT64,
                     "id": spanner.param_types.STRING},
    )
    transaction.execute_update(
        "UPDATE Accounts SET balance = balance + @amt WHERE account_id = @id",
        params={"amt": amount, "id": to_account},
        param_types={"amt": spanner.param_types.FLOAT64,
                     "id": spanner.param_types.STRING},
    )

database.run_in_transaction(transfer_funds, "ACC001", "ACC002", 500.00)
```

---

### Cloud SQL

**What it is:** Fully managed relational database service supporting MySQL, PostgreSQL, and SQL Server. Handles backups, replication, patching, and failover automatically.

**When to use it:**

- Web applications needing a traditional relational database
- Applications already using MySQL or PostgreSQL on-premises
- Workloads up to ~10 TB with standard relational access patterns
- When you need stored procedures, triggers, or full SQL compatibility

```bash
# Create a Cloud SQL PostgreSQL instance
gcloud sql instances create my-pg-instance \
  --database-version=POSTGRES_15 \
  --tier=db-custom-4-16384 \   # 4 vCPUs, 16 GB RAM
  --region=us-central1 \
  --availability-type=REGIONAL \  # automatic failover to standby
  --backup-start-time=02:00 \
  --enable-point-in-time-recovery

# Create a database
gcloud sql databases create my_app_db --instance=my-pg-instance

# Connect via Cloud SQL Auth Proxy (recommended — no public IP needed)
./cloud-sql-proxy my-project:us-central1:my-pg-instance &
psql "host=127.0.0.1 port=5432 dbname=my_app_db user=postgres"
```

**Cloud SQL vs Spanner:**

```
Cloud SQL:   Single region, up to ~10TB, standard PostgreSQL/MySQL, lower cost
Spanner:     Multi-region, unlimited scale, external consistency, higher cost

Rule: start with Cloud SQL; migrate to Spanner when you hit scale or global distribution limits
```

---

### Firestore

**What it is:** A fully managed, serverless NoSQL document database. Data is stored as documents (JSON-like) organized into collections. Designed for mobile and web application backends.

**How it works:** Documents contain fields of various types (strings, numbers, maps, arrays, timestamps). You can query within a collection on any field (with indexes). Real-time listeners push updates to connected clients automatically.

**When to use it:**

- Mobile and web app backends (user profiles, content, settings)
- Real-time collaborative features (live chat, shared documents)
- Workloads with flexible or evolving schemas
- Serverless applications that need a database without connection pool management

```python
from google.cloud import firestore

db = firestore.Client(project="my-project")

# Write a document
user_ref = db.collection("users").document("user_123")
user_ref.set({
    "name":       "Priya Sharma",
    "email":      "priya@example.com",
    "country":    "India",
    "created_at": firestore.SERVER_TIMESTAMP,
    "preferences": {
        "theme":         "dark",
        "notifications": True,
    },
})

# Query documents by field
active_indian_users = (
    db.collection("users")
    .where("country", "==", "India")
    .where("preferences.notifications", "==", True)
    .limit(50)
    .stream()
)
for doc in active_indian_users:
    print(doc.id, doc.to_dict()["name"])

# Real-time listener (calls callback on every change)
def on_snapshot(docs, changes, read_time):
    for change in changes:
        if change.type.name == "ADDED":
            print(f"New user: {change.document.get('name')}")

db.collection("users").on_snapshot(on_snapshot)
```

---

### Memorystore

**What it is:** Fully managed in-memory data store supporting Redis and Valkey (the open-source Redis fork). Provides sub-millisecond read and write latency.

**When to use it:**

- Session storage for web applications
- Caching database query results or API responses
- Leaderboards, counters, rate limiters
- Pub/sub messaging within an application
- Buffering hot data in front of Bigtable or Cloud SQL

```python
import redis

# Connect to Memorystore Redis instance
r = redis.Redis(host="10.0.0.3", port=6379, decode_responses=True)

# Cache a BigQuery query result for 10 minutes
import json
import hashlib

def get_report(date: str):
    cache_key = f"report:{hashlib.md5(date.encode()).hexdigest()}"

    # Check cache first
    cached = r.get(cache_key)
    if cached:
        print("Cache hit")
        return json.loads(cached)

    # Cache miss — query BigQuery
    print("Cache miss — querying BigQuery")
    result = run_bigquery_query(date)   # your BigQuery call here

    # Store in cache for 10 minutes (600 seconds)
    r.setex(cache_key, 600, json.dumps(result))
    return result

# Use as a rate limiter
def is_rate_limited(user_id: str, limit: int = 100) -> bool:
    key = f"rate:{user_id}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)   # reset window every 60 seconds
    return count > limit
```

---

### Service Selection Quick Reference

| Requirement | Service |
|---|---|
| Raw files, blobs, backups, data lake | Cloud Storage |
| SQL analytics on terabytes/petabytes | BigQuery |
| Millions of reads/writes per second, time-series | Bigtable |
| Global ACID transactions at scale | Spanner |
| Traditional relational app database (< 10 TB) | Cloud SQL / AlloyDB |
| Mobile/web app, flexible schema, real-time sync | Firestore |
| Sub-millisecond cache, session store | Memorystore |

---

## 3. Planning for Storage Costs and Performance

### What Is It?

Storage cost and performance are tightly linked — the fastest storage options are also the most expensive. The goal is to put each piece of data in the tier that matches its value and access frequency.

### Cost Drivers by Service

```
Cloud Storage:
  Storage cost:    $0.020/GB/month (Standard) → $0.004/GB/month (Archive)
  Operations:      Charged per read/write operation
  Retrieval:       Free (Standard), increases with colder tiers
  Egress:          Charged for data leaving a region

BigQuery:
  Storage:         $0.020/GB/month (active) → $0.010/GB/month (long-term, > 90 days)
  Queries:         $6.25/TB scanned (on-demand) OR flat-rate slot reservations
  Streaming:       $0.010/200MB inserted (avoid for bulk loads — use batch)
  Exports:         Free to GCS in the same region

Bigtable:
  Nodes:           $0.65–1.10/node/hour (always-on compute charge)
  Storage:         $0.17/GB/month (SSD) or $0.026/GB/month (HDD)
  Min viable:      1 node minimum → ~$470/month; not for small workloads

Cloud SQL:
  Instances:       Charged per vCPU/hour + RAM/hour while running
  Storage:         $0.17/GB/month (SSD)
  Backups:         Charged separately per GB

Memorystore:
  Charged by:      GB of memory provisioned (always-on)
  No free tier:    Even a 1 GB Redis instance costs ~$25/month
```

### BigQuery Cost Optimization

```sql
-- 1. Use partitioned tables to limit bytes scanned
CREATE TABLE my_dataset.events
PARTITION BY DATE(event_time)
OPTIONS (
  partition_expiration_days = 365,   -- auto-delete partitions older than 1 year
  require_partition_filter = TRUE    -- force queries to specify a date range
);

-- 2. Use clustering to skip irrelevant data within a partition
CREATE TABLE my_dataset.events
PARTITION BY DATE(event_time)
CLUSTER BY user_id, event_type;
-- Queries filtering on user_id + event_type now scan far fewer rows

-- 3. Estimate query cost before running (in BigQuery console or CLI)
-- bq query --dry_run "SELECT ..."
-- Returns: "This query will process X bytes."

-- 4. Use materialized views for repeated aggregations
CREATE MATERIALIZED VIEW my_dataset.daily_revenue AS
SELECT
  DATE(order_time) AS date,
  SUM(amount)      AS revenue,
  COUNT(*)         AS orders
FROM my_dataset.orders
GROUP BY date;
-- BigQuery automatically refreshes and serves queries from the materialized result
```

### GCS Cost Optimization

```bash
# Use storage class transitions in lifecycle rules (see section 4)
# Match storage class to access frequency:

gsutil ls -l gs://my-bucket/raw/2022/    # check last-modified dates
# Files from 2022 that haven't been touched → move to Coldline or Archive

# Compare costs before choosing storage class
# 100 GB accessed once/month:
#   Standard: $2.00/month storage
#   Nearline:  $1.00/month storage + $0.01 retrieval = $1.01 (cheaper!)
# 100 GB accessed once/year:
#   Archive:   $0.40/month storage + $0.05 retrieval = barely $0.45
```

### Performance Optimization Patterns

**BigQuery:**
```sql
-- Avoid SELECT * (scans all columns, wastes money and time)
-- Avoid functions on partitioning columns in WHERE (disables partition pruning)

-- ❌ Disables partition pruning
WHERE DATE_TRUNC(event_time, MONTH) = '2024-01-01'

-- ✅ Uses partition pruning
WHERE event_time >= '2024-01-01' AND event_time < '2024-02-01'

-- Use approximate functions for analytics where exactness isn't critical
SELECT APPROX_COUNT_DISTINCT(user_id) FROM my_dataset.events;
-- ~5x faster and cheaper than COUNT(DISTINCT user_id) on large tables
```

**Bigtable:**
```
Performance is directly proportional to node count.
Rule of thumb:
  SSD: ~10,000 reads/sec or ~10,000 writes/sec per node
  HDD: ~500 reads/sec or ~10,000 writes/sec per node

Avoid row key hotspotting:
  ❌ Sequential keys like 0001, 0002, 0003 → all writes go to one tablet server
  ✅ Hash-prefix or reverse-timestamp keys → writes distributed across all nodes
```

### Key Takeaway

Cost optimization is an ongoing practice, not a one-time setup. Use BigQuery's dry-run to estimate query costs, partition and cluster all large tables, and audit GCS storage classes quarterly against actual access patterns.

---

## 4. Lifecycle Management of Data

### What Is It?

Data has a lifecycle — it is created, used frequently, used less over time, archived, and eventually deleted. Lifecycle management automates moving or deleting data as it ages, keeping costs low without manual intervention.

### GCS Object Lifecycle Rules

Lifecycle rules are JSON policies applied to a bucket. GCS evaluates them daily and automatically transitions or deletes objects that match.

```json
{
  "lifecycle": {
    "rule": [
      {
        "action": { "type": "SetStorageClass", "storageClass": "NEARLINE" },
        "condition": {
          "age": 30,
          "matchesStorageClass": ["STANDARD"]
        }
      },
      {
        "action": { "type": "SetStorageClass", "storageClass": "COLDLINE" },
        "condition": {
          "age": 90,
          "matchesStorageClass": ["NEARLINE"]
        }
      },
      {
        "action": { "type": "SetStorageClass", "storageClass": "ARCHIVE" },
        "condition": {
          "age": 365,
          "matchesStorageClass": ["COLDLINE"]
        }
      },
      {
        "action": { "type": "Delete" },
        "condition": {
          "age": 2555
        }
      }
    ]
  }
}
```

```bash
# Apply a lifecycle policy to a bucket
gsutil lifecycle set lifecycle.json gs://my-data-lake/

# Verify the policy is applied
gsutil lifecycle get gs://my-data-lake/
```

### BigQuery Table Expiration and Partition Expiration

```sql
-- Set expiration on a whole table (auto-deletes the table after 30 days)
CREATE TABLE my_dataset.temp_analysis
OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))
AS SELECT * FROM my_dataset.orders WHERE year = 2023;

-- Set expiration on individual partitions of an existing table
ALTER TABLE my_dataset.events
SET OPTIONS (partition_expiration_days = 365);
-- Each partition is automatically deleted 365 days after its partition date

-- Set dataset-level default expiration (applies to all new tables)
bq update --default_table_expiration 7776000 my_project:temp_workspace
-- 7776000 seconds = 90 days
```

### Data Retention vs Legal Hold

```
Normal lifecycle:   Data is deleted automatically per the schedule above.

Legal hold:         A legal or compliance requirement prevents deletion.
                    Apply a retention policy with LOCKED mode on GCS:

gsutil retention set 7y gs://legal-hold-bucket/
gsutil retention lock gs://legal-hold-bucket/
# Once locked, the policy cannot be shortened or removed
# Data in this bucket cannot be deleted before 7 years regardless of any rule
```

### Archival Pipeline Pattern

For data that must be kept but rarely accessed, automate archival from BigQuery to GCS:

```python
# Cloud Composer DAG: monthly archive of old BigQuery data to GCS Coldline
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.transfers.bigquery_to_gcs import BigQueryToGCSOperator
from datetime import datetime, timedelta

with DAG(
    dag_id="monthly_archive",
    schedule_interval="0 1 1 * *",   # 1 AM on the 1st of every month
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    # Export data older than 2 years to GCS (Coldline)
    export_old_data = BigQueryToGCSOperator(
        task_id="export_to_gcs",
        source_project_dataset_table="my_project.sales.orders",
        destination_cloud_storage_uris=[
            "gs://my-archive-bucket/orders/{{ macros.ds_format(ds, '%Y-%m-%d', '%Y') }}/part-*.parquet"
        ],
        export_format="PARQUET",
        compression="SNAPPY",
    )

    # Delete the exported rows from BigQuery to reduce active storage cost
    delete_old_rows = BigQueryInsertJobOperator(
        task_id="delete_archived_rows",
        configuration={
            "query": {
                "query": """
                    DELETE FROM `my_project.sales.orders`
                    WHERE order_date < DATE_SUB(CURRENT_DATE(), INTERVAL 2 YEAR)
                """,
                "useLegacySql": False,
            }
        },
    )

    export_old_data >> delete_old_rows
```

### Key Takeaway

Lifecycle management directly translates to cost savings. A common mistake is leaving all data in Standard storage forever because it's the default. Start with a lifecycle policy on day one — it costs nothing to configure and saves money every month automatically.

---

## 5. Planning for Using a Data Warehouse

### What Is It?

A data warehouse is a system optimized for analytical queries — aggregating, filtering, and joining large amounts of historical data. In GCP, BigQuery is the data warehouse. Planning for it means deciding how to model, partition, load, and govern data inside BigQuery.

### Data Warehouse vs Operational Database

```
Operational Database (OLTP):           Data Warehouse (OLAP):
  Purpose: Run the business             Purpose: Analyze the business
  Queries: Many small, fast queries     Queries: Few large, complex queries
  Data:    Current state                Data:    Historical (months/years)
  Schema:  Normalized (many tables)     Schema:  Denormalized (fewer, wider tables)
  Updates: Constant INSERT/UPDATE       Updates: Bulk loads, rarely updated
  Example: Cloud SQL (order system)     Example: BigQuery (order analytics)
```

### Schema Design: Star Schema in BigQuery

The star schema is the standard warehouse design pattern. One central fact table (events, transactions) surrounded by dimension tables (lookup data).

```sql
-- Fact table: one row per order line item (large, append-only)
CREATE TABLE my_dataset.fact_order_items (
  order_item_id  STRING     NOT NULL,
  order_id       STRING     NOT NULL,
  customer_key   INT64      NOT NULL,   -- FK to dim_customers
  product_key    INT64      NOT NULL,   -- FK to dim_products
  date_key       INT64      NOT NULL,   -- FK to dim_date (e.g., 20240115)
  quantity       INT64,
  unit_price     FLOAT64,
  discount_pct   FLOAT64,
  revenue        FLOAT64,
)
PARTITION BY RANGE_BUCKET(date_key, GENERATE_ARRAY(20200101, 20300101, 10000))
CLUSTER BY customer_key, product_key;

-- Dimension table: one row per customer (small, slowly changing)
CREATE TABLE my_dataset.dim_customers (
  customer_key   INT64    NOT NULL,
  customer_id    STRING,
  name           STRING,
  email          STRING,
  country        STRING,
  segment        STRING,       -- e.g., "Enterprise", "SMB", "Consumer"
  valid_from     DATE,
  valid_to       DATE,
  is_current     BOOL,
);

-- Analytical query joining fact + dimensions
SELECT
  c.country,
  c.segment,
  p.category,
  SUM(f.revenue)              AS total_revenue,
  COUNT(DISTINCT f.order_id)  AS total_orders,
  AVG(f.unit_price)           AS avg_unit_price
FROM my_dataset.fact_order_items f
JOIN my_dataset.dim_customers c ON f.customer_key = c.customer_key
JOIN my_dataset.dim_products  p ON f.product_key  = p.product_key
WHERE f.date_key BETWEEN 20240101 AND 20240131
  AND c.is_current = TRUE
GROUP BY c.country, c.segment, p.category
ORDER BY total_revenue DESC
LIMIT 50;
```

### Slowly Changing Dimensions (SCD)

A customer's segment or address changes over time. An SCD strategy tracks historical values.

```sql
-- SCD Type 2: keep history by adding valid_from / valid_to / is_current columns
-- When a customer's segment changes:

-- Step 1: Close the current record
UPDATE my_dataset.dim_customers
SET valid_to = CURRENT_DATE(), is_current = FALSE
WHERE customer_id = 'C001' AND is_current = TRUE;

-- Step 2: Insert the new record
INSERT INTO my_dataset.dim_customers
VALUES (
  GENERATE_UUID(), 'C001', 'Alice', 'alice@example.com',
  'India', 'Enterprise',   -- new segment
  CURRENT_DATE(), DATE '9999-12-31', TRUE
);
```

### Loading Data into BigQuery

```python
from google.cloud import bigquery

client = bigquery.Client(project="my-project")

# Batch load from GCS (preferred for bulk data — free, fast)
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.PARQUET,
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    schema_update_options=[
        bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
    ],
)
load_job = client.load_table_from_uri(
    source_uris="gs://my-bucket/clean/orders/2024-01-15/*.parquet",
    destination="my_project.sales.fact_order_items",
    job_config=job_config,
)
load_job.result()   # blocks until complete
print(f"Loaded {load_job.output_rows} rows")

# Streaming insert (for real-time, < 200MB/s — has a cost)
errors = client.insert_rows_json(
    "my_project.sales.events",
    [{"event_id": "E001", "user_id": "U1", "event_type": "purchase"}],
)
if errors:
    print(f"Streaming errors: {errors}")
```

### Key Takeaway

BigQuery rewards good schema design. Partitioned + clustered tables are not optional for production — they directly control cost and query speed. Design your schema with the most common query patterns in mind, and avoid over-normalizing (BigQuery prefers wide, denormalized tables over many small joined tables).

---

## 6. Using a Data Lake

### What Is It?

A data lake is a centralized repository that stores data in its raw, original format — structured, semi-structured, and unstructured — at any scale. Unlike a data warehouse (which requires data to be cleaned and modeled before loading), a data lake accepts everything first and transforms it later (ELT: Extract, Load, Transform).

### Data Lake vs Data Warehouse

```
Data Lake:                          Data Warehouse:
  Schema on read                      Schema on write
  Raw data stored as-is               Data cleaned before load
  Many data types (CSV, JSON,         Structured data only
  images, logs, Parquet, video)
  ELT (transform after load)          ETL (transform before load)
  GCS + Dataflow + BigQuery           BigQuery
  Cheap per GB                        More expensive per GB
  Data scientists explore raw data    Analysts run structured reports
```

### GCP Data Lake Architecture

```
                     ┌─────────────────┐
  External Sources   │  Ingestion Layer │
  ├── Databases  ──► │  Pub/Sub         │
  ├── APIs       ──► │  Dataflow        │
  ├── Files      ──► │  Transfer Service│
  └── Streams    ──► │  DMS / Datastream│
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │   Raw Zone       │  GCS: gs://lake/raw/
                     │   (Bronze)       │  Original files, no changes
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │   Clean Zone     │  GCS: gs://lake/clean/ (Parquet)
                     │   (Silver)       │  Validated, typed, deduplicated
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │  Serving Zone    │  BigQuery dataset
                     │  (Gold)          │  Aggregated, modelled, query-ready
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │   Consumers      │
                     ├── Looker/Datastudio (dashboards)
                     ├── Vertex AI (ML training)
                     └── APIs (data products)
```

### Querying a Data Lake with BigQuery External Tables

You don't have to load data into BigQuery to query it. BigQuery can query Parquet, CSV, JSON, or Avro files directly on GCS using external tables.

```sql
-- Create an external table pointing to Parquet files on GCS
CREATE OR REPLACE EXTERNAL TABLE my_dataset.raw_events
OPTIONS (
  format        = 'PARQUET',
  uris          = ['gs://my-data-lake/clean/events/date=2024-*/*.parquet'],
  hive_partition_uri_prefix = 'gs://my-data-lake/clean/events/',
);

-- Query the external table with Hive-style partition filtering
SELECT
  event_type,
  COUNT(*) AS count
FROM my_dataset.raw_events
WHERE date = '2024-01-15'
GROUP BY event_type;

-- Tip: External tables are great for exploration.
-- For production analytics, materialize to a native BigQuery table for speed.
CREATE TABLE my_dataset.events AS
SELECT * FROM my_dataset.raw_events
WHERE date BETWEEN '2024-01-01' AND '2024-01-31';
```

### Key Takeaway

The data lake's value comes from keeping raw data intact and accessible. Never overwrite raw files — always write transformations to a new zone. Raw data is your source of truth for reprocessing when business logic changes.

---

## 7. Designing for a Data Mesh

### What Is It?

A data mesh is an organizational and architectural pattern that decentralizes data ownership. Instead of a central data team that owns all data, each business domain (Sales, Marketing, Engineering, Finance) owns and operates its own data as a product.

### The Four Data Mesh Principles

```
1. Domain ownership
   Each domain team owns the full lifecycle of their data:
   ingestion → transformation → serving → quality → documentation.
   The central team provides platform infrastructure, not data ownership.

2. Data as a product
   Each domain publishes data products — well-defined, versioned, documented,
   SLA-backed datasets — that other domains can consume.
   Bad data quality is a product defect.

3. Self-serve data platform
   A central platform team provides reusable infrastructure:
   storage (GCS/BigQuery), orchestration (Composer), cataloging (Dataplex),
   so domain teams can build without reinventing the wheel.

4. Federated computational governance
   Global policies (security, privacy, compliance) are enforced centrally,
   but domain teams have autonomy within those guardrails.
```

### GCP Data Mesh Implementation with Dataplex

Dataplex is GCP's purpose-built service for data mesh. It organizes storage into Lakes → Zones → Assets across GCS and BigQuery.

```
Dataplex Lake: "Company Data Mesh"
  │
  ├── Domain: Sales
  │     ├── Zone: Raw   → gs://sales-raw/
  │     ├── Zone: Clean → gs://sales-clean/ (Parquet)
  │     └── Zone: Gold  → BigQuery dataset: sales_products
  │           └── Data Products:
  │                 orders_v1   (daily, SLA: available by 6 AM)
  │                 pipeline_v2 (streaming, SLA: < 5 min lag)
  │
  ├── Domain: Marketing
  │     ├── Zone: Raw   → gs://marketing-raw/
  │     └── Zone: Gold  → BigQuery dataset: marketing_products
  │           └── Data Products:
  │                 campaign_performance_v1
  │                 customer_segments_v3
  │
  └── Domain: Finance
        └── Zone: Gold  → BigQuery dataset: finance_products
              └── Data Products:
                    revenue_daily_v1
                    cost_center_v2
```

```bash
# Create a Dataplex Lake for a domain
gcloud dataplex lakes create sales-lake \
  --location=us-central1 \
  --display-name="Sales Domain Lake"

# Create zones within the lake
gcloud dataplex zones create sales-raw-zone \
  --lake=sales-lake \
  --location=us-central1 \
  --type=RAW \
  --resource-spec-type=STORAGE_BUCKET

gcloud dataplex zones create sales-curated-zone \
  --lake=sales-lake \
  --location=us-central1 \
  --type=CURATED \
  --resource-spec-type=BIGQUERY_DATASET

# Attach assets (GCS buckets / BigQuery datasets) to zones
gcloud dataplex assets create sales-raw-bucket \
  --lake=sales-lake \
  --zone=sales-raw-zone \
  --location=us-central1 \
  --resource-spec-type=STORAGE_BUCKET \
  --resource-spec-name=projects/my-project/buckets/sales-raw
```

### Data Product Contract Pattern

Each domain defines a contract for its data products — making expectations explicit and machine-readable.

```yaml
# data_product_contract.yaml — published by the Sales domain
name: orders_v1
domain: sales
owner: sales-data-team@company.com
version: "1.0"

description: >
  Daily snapshot of all confirmed orders. Refreshed at 2 AM UTC.
  Covers orders placed in the last 3 years.

sla:
  availability_by: "06:00 UTC"
  freshness_lag_minutes: 30
  uptime_percent: 99.5

schema:
  - name: order_id
    type: STRING
    nullable: false
    description: "Unique order identifier"
  - name: customer_id
    type: STRING
    nullable: false
    description: "Pseudonymized customer identifier (not raw PII)"
  - name: order_date
    type: DATE
    nullable: false
  - name: amount
    type: FLOAT64
    nullable: false
  - name: status
    type: STRING
    nullable: false
    allowed_values: [PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED]

quality_rules:
  - "amount >= 0"
  - "order_date <= CURRENT_DATE()"
  - "status IN ('PENDING','CONFIRMED','SHIPPED','DELIVERED','CANCELLED')"

access:
  readers:
    - group:finance-analysts@company.com
    - group:marketing-team@company.com
  requires_approval: false
```

### Data Mesh vs Data Warehouse vs Data Lake

```
Data Warehouse:   Centralized team, centralized data, central queries
Data Lake:        Centralized storage, decentralized analysis
Data Mesh:        Decentralized ownership AND storage AND governance
                  Each domain is responsible for their own data products
```

### Key Takeaway

Data mesh is an organizational pattern first, a technology pattern second. Dataplex provides the GCP tooling, but the harder work is defining domain boundaries, establishing data product contracts, and building a culture of ownership. Start small — pilot with one domain before rolling out mesh-wide.

---

# Part B — Preparing and Using Data for Analysis

---

## 8. Optimizing Resources

### What Is It?

Resource optimization means getting the most analytical throughput for the lowest cost — avoiding wasted compute, over-provisioned infrastructure, and inefficient query patterns.

### BigQuery Slot Management

BigQuery uses "slots" as its unit of compute. One slot is one virtual CPU used for query execution.

```
On-Demand pricing:
  You pay per TB scanned. GCP allocates slots dynamically.
  Best for: intermittent, unpredictable workloads.

Capacity pricing (reservations):
  You purchase a fixed number of slots (100-slot increments).
  Committed: 1-year or 3-year commitment, ~50% cheaper than on-demand.
  Flex Slots: by the minute — useful for short, predictable bursts.
  Best for: consistent, high-volume workloads.
```

```sql
-- View current slot utilization for your project
SELECT
  job_id,
  user_email,
  total_slot_ms / 1000 AS slot_seconds,
  total_bytes_processed,
  TIMESTAMP_DIFF(end_time, start_time, SECOND) AS duration_seconds
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) = CURRENT_DATE()
ORDER BY total_slot_ms DESC
LIMIT 20;
```

### Query Optimization Checklist

```sql
-- 1. Only read what you need
SELECT user_id, event_type FROM events   -- not SELECT *

-- 2. Filter on partitioned columns first
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31'

-- 3. Use clustering to narrow further
-- (If table is clustered on user_id, this eliminates most blocks)
AND user_id = 'U001'

-- 4. Avoid self-joins on large tables — use window functions instead
-- ❌ Expensive self-join to find previous event
SELECT a.user_id, a.event_time, b.event_time AS prev_event_time
FROM events a JOIN events b ON a.user_id = b.user_id
WHERE b.event_time < a.event_time

-- ✅ Window function (single pass over the data)
SELECT user_id, event_time,
       LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) AS prev_event_time
FROM events

-- 5. Pre-aggregate with materialized views for repeated dashboard queries
CREATE MATERIALIZED VIEW my_dataset.mv_daily_revenue AS
SELECT DATE(order_time) AS date, SUM(amount) AS revenue
FROM my_dataset.orders GROUP BY date;
```

### Dataflow Autoscaling and Worker Optimization

```python
from apache_beam.options.pipeline_options import PipelineOptions

options = PipelineOptions(
    runner="DataflowRunner",
    project="my-project",
    region="us-central1",

    # Autoscaling: Dataflow adds/removes workers based on backlog
    autoscaling_algorithm="THROUGHPUT_BASED",
    num_workers=2,           # start with 2
    max_num_workers=20,      # scale up to 20 if needed

    # Machine type: standard for CPU-bound, highmem for memory-heavy
    machine_type="n1-standard-4",    # 4 vCPU, 15 GB RAM

    # Use Streaming Engine for streaming jobs — reduces cost ~30%
    enable_streaming_engine=True,

    # Use Shuffle Service for batch jobs — reduces cost and improves speed
    experiments=["shuffle_mode=service"],

    # Disk size: reduce if your pipeline doesn't need much local storage
    disk_size_gb=50,   # default is 250 GB per worker
)
```

### Bigtable Node Sizing

```python
from google.cloud.bigtable import enums

# Scale Bigtable nodes up during peak load, down during off-peak
# (Bigtable takes ~20 minutes to fully rebalance after scaling)

instance.cluster("my-cluster").update(
    serve_nodes=10   # scale up to 10 nodes for peak
)

# Monitor utilization in Cloud Monitoring
# Target: keep CPU utilization < 70% for read-heavy, < 85% for write-heavy
# If consistently above: add nodes
# If consistently below 30%: remove nodes (min 1 node)
```

### Key Takeaway

The single highest-impact optimization for BigQuery is partitioning + clustering on all large tables. Everything else (slot reservations, query rewrites) is secondary. Profile your top 10 most expensive queries monthly and work through them systematically.

---

## 9. Preparing Data for Visualization

### What Is It?

Visualization tools (Looker, Looker Studio, Tableau, Power BI) work best when data is pre-aggregated, consistently named, and purpose-built for the questions analysts will ask. Raw normalized warehouse tables are rarely visualization-ready.

### The Serving Layer: Views and Aggregated Tables

```sql
-- Create a business-friendly view that hides complexity from analysts
-- Joins multiple tables, renames columns, applies business logic

CREATE OR REPLACE VIEW my_dataset.vw_sales_summary AS
SELECT
  DATE(o.order_time)                   AS order_date,
  EXTRACT(YEAR  FROM o.order_time)     AS year,
  EXTRACT(MONTH FROM o.order_time)     AS month,
  EXTRACT(WEEK  FROM o.order_time)     AS week_number,

  c.country                            AS customer_country,
  c.segment                            AS customer_segment,
  p.category                           AS product_category,
  p.brand                              AS product_brand,

  COUNT(DISTINCT o.order_id)           AS orders,
  COUNT(DISTINCT o.customer_id)        AS unique_customers,
  SUM(oi.quantity)                     AS units_sold,
  ROUND(SUM(oi.revenue), 2)           AS revenue,
  ROUND(AVG(oi.unit_price), 2)        AS avg_unit_price,
  ROUND(SUM(oi.revenue) /
        NULLIF(COUNT(DISTINCT o.order_id), 0), 2) AS avg_order_value

FROM my_dataset.fact_order_items oi
JOIN my_dataset.dim_orders    o ON oi.order_id    = o.order_id
JOIN my_dataset.dim_customers c ON oi.customer_key = c.customer_key
JOIN my_dataset.dim_products  p ON oi.product_key  = p.product_key
WHERE c.is_current = TRUE
GROUP BY 1,2,3,4,5,6,7,8;
```

### Looker Studio (formerly Data Studio)

Looker Studio connects directly to BigQuery and renders dashboards in a browser. Performance tips:

```sql
-- Use extract fields for date dimensions to avoid repeated EXTRACT() in every query
-- Looker Studio generates SQL like: WHERE EXTRACT(YEAR FROM order_date) = 2024
-- On a non-partitioned table this is a full scan

-- Instead: add pre-computed year/month columns to your serving view
SELECT
  *,
  EXTRACT(YEAR  FROM order_date) AS order_year,
  EXTRACT(MONTH FROM order_date) AS order_month,
  FORMAT_DATE('%Y-%m', order_date) AS year_month
FROM ...

-- This lets Looker Studio filter: WHERE order_year = 2024 AND order_month = 1
-- which is fast and cheap
```

### BI Engine: In-Memory Acceleration for BigQuery

BI Engine caches frequently queried BigQuery data in memory, reducing dashboard query latency from seconds to milliseconds.

```bash
# Reserve 10 GB of BI Engine memory for a project
bq update \
  --project_id=my-project \
  --reservation_size=10G \
  my-project:US
```

Once reserved, BigQuery automatically uses BI Engine for eligible queries (simple aggregations, filters, group-bys) without any code changes. BI Engine costs ~$5/GB/hour but can reduce dashboards from 5-second to sub-second load times.

### Preparing Data for ML vs BI

```
For BI dashboards:
  → Aggregated, denormalized, human-readable column names
  → Pre-computed KPIs and metrics
  → Filtered to relevant date ranges
  → Views (not tables) so analysts always see fresh data

For ML training:
  → Row-level (unaggregated) data
  → Features engineered as numeric/categorical
  → Balanced class distributions (for classification)
  → Train/validation/test splits already defined
  → Exported to GCS as Parquet or CSV for Vertex AI ingestion
```

### Feature Store with Vertex AI Feature Store

```python
from google.cloud.aiplatform import featurestore

# Vertex AI Feature Store manages ML features for online (real-time)
# and offline (batch training) serving from the same definition

# Define a feature group
featurestore.FeatureGroup.create(
    name="user_features",
    source=featurestore.utils.FeatureGroupBigQuerySource(
        uri=["bq://my-project.features.user_features_table"],
        entity_id_columns=["user_id"],
    ),
    project="my-project",
    location="us-central1",
)

# Online serving: get features for a single user in real time (< 5ms)
serving_client = featurestore.FeatureOnlineStoreAdminServiceClient()
# Returns: {"days_since_last_order": 12, "total_spend_90d": 349.5, ...}
```

### Key Takeaway

Build a dedicated serving layer (views or materialized tables) between your warehouse and your visualization tools. Never connect Looker Studio or Tableau directly to raw fact tables — it creates slow dashboards, unexpected results, and costly queries every time someone opens a report.

---

## 10. Sharing Data

### What Is It?

Data sharing is making datasets available to others — within your organization, across teams, or externally to partners and customers — in a controlled, governed way.

### Intra-Organization Sharing with BigQuery IAM

The simplest form of sharing is granting IAM roles on a BigQuery dataset.

```bash
# Share a dataset with an analytics team (read-only)
bq add-iam-policy-binding \
  --member="group:analytics-team@company.com" \
  --role="roles/bigquery.dataViewer" \
  my_project:sales_products

# Share with a service account used by Looker
bq add-iam-policy-binding \
  --member="serviceAccount:looker-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer" \
  my_project:sales_products

# Grant job execution rights so they can run queries
gcloud projects add-iam-policy-binding my-project \
  --member="group:analytics-team@company.com" \
  --role="roles/bigquery.jobUser"
```

### Row-Level Security with Row Access Policies

You may want different users to see different rows of the same table — e.g., each regional manager sees only their region's data.

```sql
-- Create a row access policy: users only see their own country's data
CREATE ROW ACCESS POLICY filter_by_country
ON my_dataset.orders
GRANT TO ("group:india-team@company.com")
FILTER USING (country = 'India');

CREATE ROW ACCESS POLICY filter_by_country
ON my_dataset.orders
GRANT TO ("group:us-team@company.com")
FILTER USING (country = 'US');

-- Users in india-team run: SELECT * FROM orders
-- They automatically see only rows where country = 'India'
-- The filter is invisible and cannot be bypassed
```

### Analytics Hub — Sharing Data Across Organizations

Analytics Hub is GCP's managed data marketplace. Publishers list datasets; subscribers query them directly in their own BigQuery project — no data copying, no file exports.

```bash
# Publisher: create a data exchange and listing
gcloud analytics-hub exchanges create partner-exchange \
  --location=us \
  --display-name="Partner Data Exchange" \
  --description="Curated datasets for verified partners"

gcloud analytics-hub listings create daily-orders-listing \
  --location=us \
  --exchange=partner-exchange \
  --display-name="Daily Orders Summary" \
  --source-bigquery-dataset=projects/my-project/datasets/sales_products

# Subscriber: subscribe to a listing (they get a linked dataset in their project)
gcloud analytics-hub listings subscribe \
  projects/my-project/locations/us/dataExchanges/partner-exchange/listings/daily-orders-listing \
  --destination-project=subscriber-project \
  --destination-dataset=partner_sales_data
```

The subscriber queries the linked dataset as if it were their own BigQuery table. The publisher retains full control — revoking the subscription immediately cuts off access.

### Authorized Views — Share Derived Data, Not Raw Data

An authorized view lets you share a query result (not the underlying table) so subscribers never see raw or sensitive columns.

```sql
-- Create a view that excludes PII
CREATE OR REPLACE VIEW my_dataset.shared_orders AS
SELECT
  order_id,
  country,          -- ✅ share country
  product_category,
  amount,
  order_date
  -- ❌ customer_email and customer_name are deliberately excluded
FROM my_dataset.fact_order_items;

-- Authorize the view to access the underlying table
-- (so subscribers don't need direct access to the base table)
-- Done in the BigQuery console under Dataset → Edit Details → Authorized Views
```

### Key Takeaway

Match the sharing mechanism to the trust level: IAM roles for internal teams, row access policies for regional segmentation, authorized views for curated external access, Analytics Hub for cross-organization data products.

---

## 11. Exploring and Analyzing Data

### What Is It?

Data exploration is the process of understanding a new dataset — its structure, distribution, quality, and relationships — before building pipelines or models on top of it.

### Exploratory Analysis in BigQuery

```sql
-- Profile a new table: understand what's in it
SELECT
  COUNT(*)                          AS total_rows,
  COUNT(DISTINCT customer_id)       AS unique_customers,
  COUNT(DISTINCT product_id)        AS unique_products,
  MIN(order_date)                   AS earliest_order,
  MAX(order_date)                   AS latest_order,
  ROUND(AVG(amount), 2)             AS avg_order_value,
  ROUND(STDDEV(amount), 2)          AS stddev_order_value,
  COUNTIF(amount IS NULL)           AS null_amounts,
  COUNTIF(amount < 0)               AS negative_amounts,
  APPROX_QUANTILES(amount, 4)       AS quartiles    -- [25th, 50th, 75th, 100th]
FROM my_dataset.orders;

-- Check for duplicates
SELECT order_id, COUNT(*) AS occurrences
FROM my_dataset.orders
GROUP BY order_id
HAVING occurrences > 1
ORDER BY occurrences DESC
LIMIT 20;

-- Distribution of a categorical field
SELECT
  status,
  COUNT(*)                                    AS count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct
FROM my_dataset.orders
GROUP BY status
ORDER BY count DESC;

-- Time-series trend: daily order count
SELECT
  order_date,
  COUNT(*) AS orders,
  SUM(amount) AS revenue
FROM my_dataset.orders
GROUP BY order_date
ORDER BY order_date;
```

### BigQuery ML for In-Database Analytics

BigQuery ML lets you train and evaluate ML models directly with SQL — no Python, no data export.

```sql
-- Train a linear regression model to predict order value
CREATE OR REPLACE MODEL my_dataset.order_value_model
OPTIONS (
  model_type     = 'LINEAR_REG',
  input_label_cols = ['amount'],
  data_split_method = 'AUTO_SPLIT'
) AS
SELECT
  amount,
  EXTRACT(DAYOFWEEK FROM order_date) AS day_of_week,
  EXTRACT(MONTH     FROM order_date) AS month,
  customer_segment,
  product_category,
  quantity
FROM my_dataset.orders
WHERE order_date BETWEEN '2022-01-01' AND '2024-01-01';

-- Evaluate the model
SELECT * FROM ML.EVALUATE(MODEL my_dataset.order_value_model);
-- Returns: mean_absolute_error, mean_squared_error, r2_score, etc.

-- Run predictions
SELECT
  order_id,
  predicted_amount,
  amount AS actual_amount,
  ABS(predicted_amount - amount) AS error
FROM ML.PREDICT(
  MODEL my_dataset.order_value_model,
  (SELECT * FROM my_dataset.orders WHERE order_date = '2024-02-01')
)
ORDER BY error DESC
LIMIT 20;

-- Available model types in BigQuery ML:
-- LINEAR_REG, LOGISTIC_REG, KMEANS, RANDOM_FOREST_CLASSIFIER,
-- RANDOM_FOREST_REGRESSOR, XGBOOST, DNN_CLASSIFIER, AUTOML_CLASSIFIER,
-- MATRIX_FACTORIZATION (recommendations), ARIMA_PLUS (time-series forecasting)
```

### Vertex AI Workbench for Notebook-Based Exploration

For Python-based exploration with pandas, matplotlib, and BigQuery:

```python
# In a Vertex AI Workbench notebook
from google.cloud import bigquery
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

client = bigquery.Client(project="my-project")

# Pull a sample into pandas for exploration
df = client.query("""
    SELECT
        order_date,
        country,
        product_category,
        amount,
        status
    FROM `my_project.sales.orders`
    WHERE order_date >= '2024-01-01'
    LIMIT 100000
""").to_dataframe()

# Basic profile
print(df.describe())
print(df.isnull().sum())

# Distribution of order values
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
df["amount"].hist(bins=50, ax=axes[0])
axes[0].set_title("Order Value Distribution")

df.groupby("country")["amount"].mean().sort_values().plot(kind="barh", ax=axes[1])
axes[1].set_title("Average Order Value by Country")
plt.tight_layout()
plt.show()

# Correlation matrix
numeric_cols = df.select_dtypes(include="number")
sns.heatmap(numeric_cols.corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Matrix")
plt.show()
```

### Key Takeaway

Start every new dataset with a profiling query — total rows, null counts, date ranges, distinct counts, value distributions. This takes 5 minutes and routinely reveals data quality issues that would otherwise surface as mysterious bugs downstream.

---

# Part C — Maintaining and Automating Data Workloads

---

## 12. Designing Automation and Repeatability

### What Is It?

A data workload that requires manual steps is fragile and expensive. Automation means pipeline runs trigger themselves, recover from failures without human intervention, and produce the same result every time they run.

### Principles of Repeatable Pipelines

```
Idempotency:
  Running a pipeline twice on the same input produces the same output.
  No duplicates, no partial states.

Determinism:
  Given the same input, the output is always identical.
  Avoid time-dependent logic (e.g., CURRENT_DATE()) inside transformation logic.
  Pass dates as parameters instead.

Immutability:
  Never overwrite raw data. Write to new locations.
  Use date-partitioned output paths: gs://bucket/output/date=2024-01-15/

Parameterization:
  No hardcoded dates, paths, or environment values in code.
  Pass them as pipeline arguments or Airflow variables.
```

### Parameterized Pipelines

```python
# pipeline_main.py — all configuration comes from arguments, not hardcoding
import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_date",      required=True, help="YYYY-MM-DD")
    parser.add_argument("--input_bucket",  required=True)
    parser.add_argument("--output_dataset",required=True)
    parser.add_argument("--env",           default="prod", choices=["dev","staging","prod"])

    known_args, pipeline_args = parser.parse_known_args(argv)

    input_path  = f"gs://{known_args.input_bucket}/raw/{known_args.run_date}/*.csv"
    output_table= f"my_project.{known_args.output_dataset}.events"

    options = PipelineOptions(pipeline_args)

    with beam.Pipeline(options=options) as p:
        (
            p
            | "Read"      >> beam.io.ReadFromText(input_path, skip_header_lines=1)
            | "Transform" >> beam.Map(transform_record)
            | "Write BQ"  >> beam.io.WriteToBigQuery(
                output_table,
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
            )
        )

if __name__ == "__main__":
    run()
```

```bash
# Run for a specific date — fully parameterized
python pipeline_main.py \
  --run_date=2024-01-15 \
  --input_bucket=my-ingestion-bucket \
  --output_dataset=sales_clean \
  --env=prod \
  --runner=DataflowRunner \
  --project=my-project \
  --region=us-central1
```

### Cloud Composer (Airflow) for Orchestration Automation

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.dataflow import DataflowCreatePythonJobOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta

default_args = {
    "owner":             "data-platform-team",
    "depends_on_past":   True,   # don't run if yesterday's run failed
    "retries":           2,
    "retry_delay":       timedelta(minutes=10),
    "retry_exponential_backoff": True,
    "email_on_failure":  True,
    "email_on_retry":    False,
    "email":             ["data-alerts@company.com"],
}

with DAG(
    dag_id="daily_sales_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 3 * * *",   # 3 AM daily
    catchup=True,                    # run historical dates if the DAG was paused
    max_active_runs=1,               # prevent concurrent runs
    tags=["sales", "daily", "production"],
) as dag:

    # 1. Wait for the upstream file to arrive
    wait_for_source = GCSObjectExistenceSensor(
        task_id="wait_for_source_file",
        bucket="ingestion-bucket",
        object="sales/{{ ds }}/sales.csv",   # ds = YYYY-MM-DD (the run date)
        poke_interval=300,   # check every 5 minutes
        timeout=7200,        # fail if file hasn't arrived in 2 hours
        mode="reschedule",   # release the worker slot while waiting
    )

    # 2. Run the Dataflow cleaning pipeline
    run_pipeline = DataflowCreatePythonJobOperator(
        task_id="run_cleaning_pipeline",
        py_file="gs://pipeline-code-bucket/pipeline_main.py",
        job_name="sales-clean-{{ ds_nodash }}",
        options={
            "run_date":       "{{ ds }}",
            "input_bucket":   "ingestion-bucket",
            "output_dataset": "sales_clean",
            "runner":         "DataflowRunner",
            "project":        "my-project",
            "region":         "us-central1",
        },
        location="us-central1",
    )

    # 3. Validate the output
    def validate_output(run_date, **context):
        from google.cloud import bigquery
        client = bigquery.Client()
        result = client.query(f"""
            SELECT COUNT(*) AS rows
            FROM `my_project.sales_clean.events`
            WHERE DATE(event_time) = '{run_date}'
        """).result()
        rows = list(result)[0]["rows"]
        if rows < 100:
            raise ValueError(f"Only {rows} rows loaded for {run_date} — expected > 100")
        print(f"Validation passed: {rows} rows for {run_date}")

    validate = PythonOperator(
        task_id="validate_output",
        python_callable=validate_output,
        op_kwargs={"run_date": "{{ ds }}"},
    )

    # 4. Send success notification
    def notify_success(**context):
        print(f"Pipeline completed for {context['ds']}")
        # In production: send Slack/Teams message

    notify = PythonOperator(
        task_id="notify_success",
        python_callable=notify_success,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    wait_for_source >> run_pipeline >> validate >> notify
```

### Infrastructure as Code with Terraform

```hcl
# main.tf — define GCP infrastructure declaratively
# Changes are version-controlled, reviewed, and applied consistently

resource "google_bigquery_dataset" "sales_clean" {
  dataset_id    = "sales_clean"
  friendly_name = "Sales Clean"
  location      = "US"

  default_table_expiration_ms = null  # no auto-expiry for production tables

  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }
  access {
    role          = "READER"
    group_by_email = "analytics-team@company.com"
  }
}

resource "google_storage_bucket" "ingestion" {
  name          = "my-ingestion-bucket"
  location      = "US-CENTRAL1"
  storage_class = "STANDARD"
  force_destroy = false

  lifecycle_rule {
    action { type = "SetStorageClass" storage_class = "NEARLINE" }
    condition { age = 30 }
  }
  lifecycle_rule {
    action { type = "Delete" }
    condition { age = 90 }
  }
}
```

```bash
terraform init
terraform plan    # preview changes
terraform apply   # apply changes
terraform destroy # tear down (useful for dev/test environments)
```

### Key Takeaway

Automation is built on two foundations: parameterized code (no hardcoded values) and idempotent operations (safe to re-run). Get those right, and orchestration tools like Composer handle the rest.

---

## 13. Maintaining Awareness of Failures and Mitigating Impact

### What Is It?

In production data systems, failures are inevitable. The goal is not to prevent all failures but to detect them fast, limit their blast radius, and recover without manual heroics.

### Categories of Failure in Data Pipelines

```
Infrastructure failures:
  Worker crashes, network partitions, disk full, quota exceeded

Data failures:
  Schema change in upstream data, unexpected nulls, duplicate records,
  volume spike or drop, encoding issues in source files

Logic failures:
  Bug in transformation code, division by zero, incorrect join key,
  off-by-one error in date windowing

Dependency failures:
  Upstream pipeline delayed, external API down, source file never arrived,
  BigQuery slot quota exceeded

Silent failures (the most dangerous):
  Pipeline completes successfully but produces wrong results
  No errors raised; downstream dashboards show incorrect data
```

### Detecting Silent Failures with Data Quality Assertions

```python
# Add assertions inside your Dataflow pipeline
import apache_beam as beam

class AssertMinimumRecords(beam.DoFn):
    """Fail the pipeline if too few records are processed."""
    def __init__(self, min_expected: int, context_label: str):
        self.min_expected = min_expected
        self.context_label = context_label

    def process(self, element, record_count):
        actual = list(record_count)[0]
        if actual < self.min_expected:
            raise ValueError(
                f"[{self.context_label}] Expected >= {self.min_expected} records, "
                f"got {actual}. Possible upstream data issue."
            )
        yield element

# Count records and assert minimum before writing to sink
with beam.Pipeline() as p:
    records = (
        p
        | "Read"    >> beam.io.ReadFromText("gs://bucket/input/*.csv")
        | "Process" >> beam.Map(transform)
    )

    count = records | "Count" >> beam.combiners.Count.Globally()

    (
        records
        | "Assert Count" >> beam.ParDo(
            AssertMinimumRecords(min_expected=1000, context_label="daily-sales"),
            record_count=beam.pvalue.AsSingleton(count),
        )
        | "Write" >> beam.io.WriteToBigQuery("my_project.dataset.table")
    )
```

### Dead Letter Queues

A dead letter queue (DLQ) captures records that fail processing so they can be inspected and reprocessed — rather than silently dropped or causing the whole pipeline to fail.

```python
class ProcessWithDLQ(beam.DoFn):
    GOOD_TAG = "good"
    BAD_TAG  = "bad"

    def process(self, element):
        try:
            result = risky_transform(element)
            yield beam.pvalue.TaggedOutput(self.GOOD_TAG, result)
        except Exception as e:
            # Route to DLQ with error context
            yield beam.pvalue.TaggedOutput(self.BAD_TAG, {
                "original_record": str(element),
                "error":           str(e),
                "error_type":      type(e).__name__,
                "timestamp":       str(__import__("datetime").datetime.utcnow()),
            })

with beam.Pipeline() as p:
    tagged = (
        p
        | "Read"    >> beam.io.ReadFromText("input.jsonl")
        | "Process" >> beam.ParDo(ProcessWithDLQ()).with_outputs(
            ProcessWithDLQ.GOOD_TAG,
            ProcessWithDLQ.BAD_TAG,
        )
    )

    tagged.good | "Write Good" >> beam.io.WriteToBigQuery("project.dataset.events")
    tagged.bad  | "Write DLQ"  >> beam.io.WriteToBigQuery("project.dataset.events_dlq")
    # Alert and inspect events_dlq table; reprocess once the root cause is fixed
```

### Circuit Breaker Pattern

Stop a pipeline automatically if the error rate exceeds a threshold — preventing a bad run from filling your sink with garbage.

```python
class CircuitBreaker(beam.DoFn):
    def __init__(self, max_error_rate: float = 0.05):
        self.max_error_rate = max_error_rate
        self.error_counter   = beam.metrics.Metrics.counter("pipeline", "errors")
        self.total_counter   = beam.metrics.Metrics.counter("pipeline", "total")

    def process(self, element, error_count, total_count):
        total  = list(total_count)[0]
        errors = list(error_count)[0]

        if total > 1000 and errors / total > self.max_error_rate:
            raise RuntimeError(
                f"Circuit breaker tripped: {errors}/{total} records failed "
                f"({100*errors/total:.1f}% > {100*self.max_error_rate:.1f}% threshold)"
            )
        yield element
```

### Alerting on Pipeline Failures

```python
# Cloud Monitoring alert: trigger if a Composer DAG fails
# Set up in Terraform:

resource "google_monitoring_alert_policy" "dag_failure" {
  display_name = "Airflow DAG Failure"
  combiner     = "OR"

  conditions {
    display_name = "DAG run failed"
    condition_threshold {
      filter     = "resource.type=\"cloud_composer_environment\" AND metric.type=\"composer.googleapis.com/environment/dag_processing/total_parse_time\""
      comparison = "COMPARISON_GT"
      threshold_value = 0
      duration   = "60s"
    }
  }

  notification_channels = [google_monitoring_notification_channel.slack.id]
}
```

### Key Takeaway

The most damaging failure mode is a pipeline that silently produces wrong data — because it may go undetected for days or weeks. Add count assertions, value range checks, and DLQ routing to every production pipeline. Treat an empty quarantine table as part of your definition of success.

---

## 14. Monitoring and Troubleshooting Processes

### What Is It?

Monitoring is the continuous observation of pipeline health. Troubleshooting is the systematic investigation of what went wrong when something fails. Both require good observability — metrics, logs, and traces.

### The Three Pillars of Observability

```
Metrics:   Numeric measurements over time
           (rows processed/sec, error rate, latency p99, slot utilization)
           Tool: Cloud Monitoring

Logs:      Timestamped records of events
           (pipeline started, row failed validation, job completed)
           Tool: Cloud Logging

Traces:    End-to-end timing of a request or record through the system
           (how long did row X spend in each stage?)
           Tool: Cloud Trace (less common for batch pipelines)
```

### Custom Metrics in Dataflow with Beam Metrics

```python
import apache_beam as beam

class TransformWithMetrics(beam.DoFn):
    def __init__(self):
        # Define counters and distributions — visible in Dataflow UI and Cloud Monitoring
        self.records_processed  = beam.metrics.Metrics.counter("my_pipeline", "records_processed")
        self.records_skipped    = beam.metrics.Metrics.counter("my_pipeline", "records_skipped")
        self.validation_errors  = beam.metrics.Metrics.counter("my_pipeline", "validation_errors")
        self.amount_distribution= beam.metrics.Metrics.distribution("my_pipeline", "order_amount")

    def process(self, record):
        self.records_processed.inc()

        if record.get("amount") is None:
            self.records_skipped.inc()
            self.validation_errors.inc()
            return

        amount = float(record["amount"])
        self.amount_distribution.update(int(amount))    # track min/max/mean/count

        yield record
```

Metrics appear in the Dataflow job UI (Metrics tab) and are also exported to Cloud Monitoring automatically.

### Structured Logging

```python
import logging
import json

class StructuredLogger:
    """Emits JSON-structured logs readable by Cloud Logging."""
    def __init__(self, pipeline_name: str, run_date: str):
        self.pipeline_name = pipeline_name
        self.run_date      = run_date

    def info(self, event: str, **kwargs):
        entry = {
            "severity":     "INFO",
            "pipeline":     self.pipeline_name,
            "run_date":     self.run_date,
            "event":        event,
            **kwargs,
        }
        print(json.dumps(entry))   # Cloud Logging captures stdout from Dataflow workers

    def error(self, event: str, error: Exception, **kwargs):
        entry = {
            "severity":   "ERROR",
            "pipeline":   self.pipeline_name,
            "run_date":   self.run_date,
            "event":      event,
            "error_type": type(error).__name__,
            "error_msg":  str(error),
            **kwargs,
        }
        print(json.dumps(entry))

# Usage inside a DoFn
logger = StructuredLogger("sales-pipeline", "2024-01-15")
logger.info("record_processed", record_id="R001", amount=99.5)
logger.error("validation_failed", error=ValueError("negative amount"), record_id="R002")
```

Query structured logs in BigQuery (after enabling log export to BigQuery sink):

```sql
SELECT
  JSON_VALUE(jsonPayload, "$.run_date")   AS run_date,
  JSON_VALUE(jsonPayload, "$.event")      AS event,
  JSON_VALUE(jsonPayload, "$.error_msg")  AS error,
  COUNT(*)                                AS occurrences
FROM `my_project.log_dataset.dataflow_logs`
WHERE DATE(timestamp) = CURRENT_DATE()
  AND JSON_VALUE(jsonPayload, "$.severity") = "ERROR"
GROUP BY run_date, event, error
ORDER BY occurrences DESC;
```

### Troubleshooting Runbook Template

A runbook documents the steps to investigate and resolve specific failure scenarios. Every production pipeline should have one.

```markdown
## Runbook: daily_sales_pipeline failure

### Symptoms
- Airflow DAG shows red (failed) for run_date X
- Slack alert fired: "daily_sales_pipeline failed"
- Downstream dashboard shows no data for date X

### Step 1 — Identify where it failed (5 min)
1. Open Cloud Composer → DAGs → daily_sales_pipeline → failed run
2. Click the failed task → View Log
3. Note the task name (e.g., run_cleaning_pipeline) and error message

### Step 2 — Common causes and fixes

| Error | Likely cause | Fix |
|---|---|---|
| GCSObjectExistenceSensor timed out | Source file never arrived | Contact upstream team; manually trigger when file lands |
| DataflowJobFailedError | Beam pipeline bug or quota issue | Check Dataflow job logs in Cloud Logging |
| Validation assertion failed | Low row count in output | Check if input file was empty or truncated |
| BigQuery quota exceeded | Too many concurrent queries | Wait 1 hour; retry; consider slot reservation |

### Step 3 — Manual backfill (if needed)
# Trigger a specific date manually in Airflow
airflow dags trigger daily_sales_pipeline --conf '{"run_date": "2024-01-15"}'

### Step 4 — Verify recovery
SELECT COUNT(*) FROM `my_project.sales_clean.events`
WHERE DATE(event_time) = '2024-01-15';
-- Expected: > 50,000 rows

### Escalation
If unresolved in 30 minutes: page the on-call data engineer via PagerDuty.
```

### SLA Monitoring Dashboard Query

```sql
-- Track pipeline SLA compliance over the past 30 days
SELECT
  DATE(start_time)                         AS run_date,
  job_id,
  TIMESTAMP_DIFF(end_time, start_time, MINUTE) AS duration_minutes,
  state,
  CASE
    WHEN EXTRACT(HOUR FROM end_time) < 6 THEN '✅ Met SLA (before 6 AM)'
    ELSE '❌ Missed SLA'
  END AS sla_status
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE job_type = 'LOAD'
  AND DATE(start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND destination_table LIKE '%sales_clean%'
ORDER BY run_date DESC;
```

### Key Takeaway

You cannot troubleshoot what you cannot observe. Add structured logging and custom metrics to every pipeline from the start. A 2-hour investigation that could have been a 10-minute log query is the cost of skipping observability.

---

## 15. Organizing Workloads Based on Business Requirements

### What Is It?

As data platforms grow, they accumulate dozens of pipelines, datasets, and jobs. Without intentional organization, they become hard to understand, maintain, and cost-manage. This section covers how to structure workloads around business requirements rather than technical convenience.

### Organizing by Domain and Criticality

```
Domain-based organization:
  Every pipeline, dataset, and GCS bucket is tagged with its owning domain.

  Domain: sales
    Pipelines:  sales_daily_etl, sales_streaming_events, sales_archive
    Datasets:   bq://my_project/sales_raw, bq://my_project/sales_products
    Buckets:    gs://sales-raw/, gs://sales-clean/

  Domain: marketing
    Pipelines:  campaign_attribution, customer_segmentation
    Datasets:   bq://my_project/marketing_raw, bq://my_project/marketing_products

Criticality tiers:
  Tier 1 (Critical):   Revenue-impacting. SLA: data available by 6 AM.
                        Alert on call immediately if late.
                        Examples: daily order summary, payment reconciliation

  Tier 2 (Important):  Business decision support. SLA: by noon.
                        Alert team Slack channel if late.
                        Examples: marketing campaign performance, inventory levels

  Tier 3 (Best-effort):No hard SLA. Alert next business day.
                        Examples: historical analysis, ML experiment data
```

### Labeling GCP Resources

GCP labels are key-value pairs attached to resources. They enable cost attribution and workload filtering.

```bash
# Label a BigQuery dataset
bq update \
  --set_label domain:sales \
  --set_label tier:1 \
  --set_label environment:production \
  --set_label owner:sales-data-team \
  my_project:sales_products

# Label a Dataflow job at submission time
python pipeline.py \
  --labels=domain=sales,tier=1,environment=production,owner=sales-data-team

# Label a GCS bucket
gsutil label ch -l domain:sales gs://sales-raw-bucket/
```

### Cost Attribution with Labels

```sql
-- In Cloud Billing export to BigQuery, filter by label to see per-domain costs
SELECT
  label.value                       AS domain,
  SUM(cost)                         AS total_cost_usd,
  SUM(usage.amount)                 AS usage_amount,
  usage.unit
FROM `my_project.billing_export.gcp_billing_export_v1_XXXXX`
LEFT JOIN UNNEST(labels) AS label ON label.key = "domain"
WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY domain, usage.unit
ORDER BY total_cost_usd DESC;
```

### GCP Projects as Isolation Boundaries

For strict separation between environments or business units:

```
Single project (small teams):
  my-project
    ├── dev resources (labelled env:dev)
    └── prod resources (labelled env:prod)

Separate projects per environment (recommended for production):
  my-project-dev
  my-project-staging
  my-project-prod

Separate projects per domain (data mesh):
  sales-data-prod
  marketing-data-prod
  finance-data-prod
  data-platform-prod    ← shared infrastructure (Composer, Dataplex, shared buckets)
```

Using separate projects gives you independent IAM policies, billing, quota limits, and VPC networks per domain — reducing the blast radius of any incident.

### Workload Scheduling Strategy

```
Avoid scheduling everything at midnight — spread workloads:

00:00–02:00  Archive / cold storage moves (low priority, non-urgent)
02:00–04:00  ETL pipelines for Tier 1 data (must complete before 6 AM)
04:00–06:00  Aggregation and serving layer jobs
06:00        Business day starts — Tier 1 data must be available
06:00–12:00  Tier 2 pipeline runs
12:00–18:00  Ad-hoc batch jobs, ML training pipelines
18:00–24:00  Reporting exports, data sharing sync jobs

Stagger pipelines by 15–30 minutes to avoid slot contention.
Use depends_on_past=True in Airflow for sequential dependencies.
Use max_active_runs=1 to prevent concurrent runs of the same DAG.
```

### Workload Identity and Environment Isolation

```bash
# Use separate service accounts per domain and environment
# so a bug in the Sales pipeline can't accidentally touch Finance data

# Sales production pipeline service account
gcloud iam service-accounts create sales-pipeline-prod \
  --display-name="Sales Pipeline (Production)"

# Grant it access only to sales resources
gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:sales-pipeline-prod@my-project.iam.gserviceaccount.com" \
  --role="roles/dataflow.worker"

bq add-iam-policy-binding \
  --member="serviceAccount:sales-pipeline-prod@my-project.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor" \
  my_project:sales_clean

# Finance dataset is NOT accessible to this service account
# Any accidental access attempt will fail with a permission error
```

### Key Takeaway

Organize early and organize intentionally. Labels, domain separation, criticality tiers, and dedicated service accounts are cheap to set up at the start and expensive to retrofit onto a platform with 50 pipelines running in production. The goal is that anyone on the team can look at any resource and immediately answer: "Who owns this? Is it critical? What environment is it in? What does it cost?"

---

## Quick Reference: Full Service and Tool Summary

### Storage

| Need | Service |
|---|---|
| Files, blobs, data lake raw zone | Cloud Storage (GCS) |
| SQL analytics, data warehouse | BigQuery |
| Time-series, high-throughput NoSQL | Bigtable |
| Global ACID relational | Cloud Spanner |
| App database (MySQL/PostgreSQL) | Cloud SQL / AlloyDB |
| Flexible schema, mobile/web backend | Firestore |
| Sub-ms cache, sessions | Memorystore |

### Pipelines and Processing

| Need | Service |
|---|---|
| Batch and streaming transforms | Dataflow (Apache Beam) |
| Visual ETL, multi-source integration | Cloud Data Fusion |
| Visual data wrangling (no code) | Dataprep |
| Orchestration and scheduling | Cloud Composer (Airflow) |
| In-database ML | BigQuery ML |
| Notebook-based exploration | Vertex AI Workbench |
| Event ingestion and streaming | Pub/Sub |

### Governance and Operations

| Need | Service |
|---|---|
| Metadata, tagging, lineage | Data Catalog |
| Data mesh, lake organization | Dataplex |
| PII detection and redaction | Cloud DLP |
| Encryption key management | Cloud KMS |
| Cost and billing visibility | Cloud Billing Export → BigQuery |
| Metrics and alerting | Cloud Monitoring |
| Logs, audit trails | Cloud Logging |
| Cross-org data sharing | Analytics Hub |

---

*End of GCP Data Engineering Review — Storing Data · Preparing for Analysis · Maintaining and Automating Workloads*
