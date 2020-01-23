"""
Measure maximum string length for all csv files 

(All files in directories grouped by directory and maximum
is throughout all years)

Results after running:
companyCodes.csv: {'companyName': 36, ' companyTradeID': 6}
productSellers.csv: {'product': 39, 'companyID': 6}

currencyValues: {'date': 10, 'currency': 3, 'valueInUSD': 8}
derivativeTrades: {'dateOfTrade': 16, 'tradeID': 16, 'product': 39, 'buyingParty': 6, 'sellingParty': 6, 'notionalAmount': 14, 'notionalCurrency': 3, 'quantity': 5, 'maturityDate': 10, 'underlyingPrice': 10, 'underlyingCurrency': 3, 'strikePrice': 10}
productPrices: {'date': 10, 'product': 39, 'marketPrice': 7}
stockPrices: {'date': 10, 'companyID': 6, 'stockPrice': 7}
[Finished in 96.6s]
"""

import csv
from pathlib import Path

DATA_DIR = Path('.')

def main():
    max_field_lengths = {}
    files = ("companyCodes.csv", "productSellers.csv")
    for f in files:
        with open(f, 'r', newline='') as file_obj:
            reader = csv.reader(file_obj)
            headers = next(reader)
            max_lengths = None
            lengths = ([len(field) for field in line] for line in reader)
            for line in lengths:
                max_lengths = [max(pair) for pair in zip(max_lengths, line)] if max_lengths else line
        max_field_lengths[f] = dict(zip(headers, max_lengths))
        print(f"{f}: {max_field_lengths[f]}")
    dirs = ("currencyValues", "derivativeTrades", "productPrices", "stockPrices")
    for d in dirs:
        max_lengths = None
        for yeardir in (DATA_DIR/d).iterdir():
            for monthdir in yeardir.iterdir():
                for f in monthdir.iterdir():
                    with f.open('r', newline='') as file_obj:
                        reader = csv.reader(file_obj, delimiter=',')
                        headers = next(reader) # skip header
                        lengths = ((len(field) for field in line) for line in reader)
                        for line in lengths:
                            max_lengths = [max(pair) for pair in zip(line, max_lengths)] if max_lengths else list(next(lengths))
            print(yeardir)
        max_field_lengths[d] = dict(zip(headers, max_lengths))
        print(f"{d}: {max_field_lengths[d]}")

if __name__ == "__main__":
    main()
