import os
import csv
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATASET_DIR = r"C:\dev02\datasets\Uber Dataset"

cnx = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD
)
cur = cnx.cursor()

cur.execute("CREATE DATABASE IF NOT EXISTS uber")
cur.execute("USE uber")

# ── 1. rides ─────────────────────────────────────────────────────────────────
cur.execute("DROP TABLE IF EXISTS rides")
cur.execute("""
CREATE TABLE rides (
    ride_id          VARCHAR(50)  PRIMARY KEY,
    start_city       VARCHAR(100),
    end_city         VARCHAR(100),
    ride_date        DATE,
    start_time       TIME,
    end_time         TIME,
    distance_km      FLOAT,
    fare             FLOAT,
    dynamic_pricing  VARCHAR(10),
    driver_id        VARCHAR(50),
    passenger_id     VARCHAR(50),
    rating           TINYINT,
    payment_method   VARCHAR(30),
    ride_status      VARCHAR(30)
)
""")

# ── 2. drivers ────────────────────────────────────────────────────────────────
cur.execute("DROP TABLE IF EXISTS drivers")
cur.execute("""
CREATE TABLE drivers (
    driver_id            VARCHAR(50)  PRIMARY KEY,
    driver_name          VARCHAR(100),
    age                  TINYINT,
    gender               VARCHAR(10),
    city_id              VARCHAR(50),
    vehicle_type         VARCHAR(30),
    avg_driver_rating    FLOAT,
    total_rides          INT,
    total_earnings       FLOAT,
    driver_status        VARCHAR(20),
    employment_type      VARCHAR(20),
    years_of_experience  TINYINT,
    ride_acceptance_rate FLOAT
)
""")

# ── 3. cities ─────────────────────────────────────────────────────────────────
cur.execute("DROP TABLE IF EXISTS cities")
cur.execute("""
CREATE TABLE cities (
    city_id             VARCHAR(50)  PRIMARY KEY,
    city_name           VARCHAR(100),
    country             VARCHAR(100),
    continent           VARCHAR(50),
    population          BIGINT,
    regulatory_status   VARCHAR(30),
    market_competition  VARCHAR(20),
    number_of_drivers   INT,
    number_of_rides     INT,
    avg_fare            FLOAT,
    avg_wait_time_min   FLOAT,
    uber_services       VARCHAR(50),
    major_competitors   VARCHAR(100)
)
""")

# ── 4. payments ───────────────────────────────────────────────────────────────
cur.execute("DROP TABLE IF EXISTS payments")
cur.execute("""
CREATE TABLE payments (
    payment_id          VARCHAR(50)  PRIMARY KEY,
    ride_id             VARCHAR(50),
    driver_id           VARCHAR(50),
    passenger_id        VARCHAR(50),
    fare                FLOAT,
    surge_multiplier    FLOAT,
    payment_method      VARCHAR(30),
    driver_earnings     FLOAT,
    uber_commission     FLOAT,
    transaction_status  VARCHAR(20),
    payment_date        DATE
)
""")


def load_csv(filepath, table_name):
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [tuple(row.values()) for row in reader]

    if not rows:
        print(f"[{table_name}] No data found.")
        return

    placeholders = ", ".join(["%s"] * len(rows[0]))
    sql = f"INSERT IGNORE INTO {table_name} VALUES ({placeholders})"
    cur.executemany(sql, rows)
    cnx.commit()
    print(f"[{table_name}] {cur.rowcount} rows loaded from {os.path.basename(filepath)}")


files = {
    "rides_dataset1.csv":    "rides",
    "driver_dataset3.csv":   "drivers",
    "city_dataset2.csv":     "cities",
    "payment_dataset 4.csv": "payments",
}

for filename, table in files.items():
    load_csv(os.path.join(DATASET_DIR, filename), table)

# Sanity check
print("\n── Row counts ──────────────────────────")
for table in ["rides", "drivers", "cities", "payments"]:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table}: {cur.fetchone()[0]} rows")

cur.close()
cnx.close()
print("\nDone ✓")