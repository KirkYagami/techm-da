import os
import mysql.connector
from dotenv import load_dotenv


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Connect to server
cnx = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD
)

# Get a cursor
cur = cnx.cursor()

cur.execute("CREATE DATABASE IF NOT EXISTS nickk_org")
cur.execute("USE nickk_org")

cur.execute("DROP TABLE employees")




# Create employees table
cur.execute("""
CREATE TABLE IF NOT EXISTS employees (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    salary INT,
    hire_date DATE
)
""")

employees_data = [
    ("Alice", "HR", 50000, "2020-01-15"),
    ("Bob", "Engineering", 80000, "2019-03-10"),
    ("Charlie", "Sales", 60000, "2021-06-01"),
    ("David", "Engineering", 90000, "2018-07-23"),
    ("Eva", "HR", 55000, "2022-02-11"),
    ("Frank", "Marketing", 65000, "2020-09-30"),
    ("Grace", "Engineering", 85000, "2017-11-05"),
    ("Hannah", "Sales", 62000, "2021-12-19"),
    ("Ian", "Marketing", 70000, "2019-08-14"),
    ("Jack", "HR", 52000, "2023-01-01"),
]

cur.executemany("""
INSERT INTO employees (name, department, salary, hire_date)
VALUES (%s, %s, %s, %s)
""", employees_data)

cnx.commit()

cur.execute("SELECT * FROM employees")
for row in cur.fetchall():
    print(row)

cur.close()
# Close connection
cnx.close()