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