import csv, os

DATASET_DIR = r"C:\dev02\datasets\Uber Dataset"
files = [
    "rides_dataset1.csv",
    "driver_dataset3.csv",
    "city_dataset2.csv",
    "payment_dataset 4.csv",
]

for f in files:
    print(f"\n{'='*60}")
    print(f)
    with open(os.path.join(DATASET_DIR, f), newline='', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        for i, row in enumerate(reader):
            if i >= 3: break  # header + 2 data rows
            print(row)