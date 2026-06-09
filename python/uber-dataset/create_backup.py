import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME     = "uber"
OUTPUT_FILE = "uber_backup.sql"


MYSQLDUMP = r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe"


command = [
    MYSQLDUMP,
    f"-h{DB_HOST}",
    f"-P{DB_PORT}",
    f"-u{DB_USER}",
    f"-p{DB_PASSWORD}",      # no space between -p and password
    "--databases", 
    DB_NAME
]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    result = subprocess.run(command, stdout=f, stderr=subprocess.PIPE, text=True)

if result.returncode == 0:
    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"Backup created: {OUTPUT_FILE} ({size_kb:.1f} KB)")
else:
    print(f"Error: {result.stderr}")