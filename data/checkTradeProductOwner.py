"""
Program that checks that "selling party" in derivativeTrades is in 
fact the identified product seller in productSellers.csv across all years.

If it is in fact the case it allows for eliminating selling party in derivativeTrades
"""

import csv
from pathlib import Path

with open("productSellers.csv", 'r', newline='') as f:
    r = csv.reader(f, delimiter=',')
    next(r)
    productSellers = dict(r)

def all_correct_sellers():
    for yeardir in Path("derivativeTrades").iterdir():
        for monthdir in yeardir.iterdir():
            for f in monthdir.iterdir():
                with f.open("r", newline='') as fp:
                    reader = csv.reader(fp, delimiter=',')
                    next(reader) # skip header
                    for line in reader:
                        product = line[2]
                        seller = line[4]
                        if product != "Stocks" and seller != productSellers[product]:
                            print(f"Found product {product} to be sold by {seller} which is not the productSeller")
                            return False
        print(yeardir)
    return True

if all_correct_sellers():
    print("All product sold by their corresponding productSeller")
