"""
Program that checks accross all years every trade id is unique
"""

import csv
from pathlib import Path

ids = []

for yeardir in Path("derivativeTrades").iterdir():
    for monthdir in yeardir.iterdir():
        for f in monthdir.iterdir():
            with f.open("r", newline='') as fp:
                reader = csv.reader(fp, delimiter=',')
                next(reader) # skip header
                ids += [line[1] for line in reader]
        print(monthdir)

print(f"all: {len(ids)}")
print(f"unique: {len(set(ids))}")
