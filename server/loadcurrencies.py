import csv
from pathlib import Path
from datetime import datetime
from decimal import Decimal

from trades.models import CurrencyValue

DATA_DIR = Path("../data")

def get_csv(file_path, skip_header=True, delimiter=','):
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file, delimiter=delimiter)
        if skip_header:
            next(reader)
        return [line for line in reader]

def clear_data():
    """WARNING: CLEARS ALL DATA FROM ALL TABLES"""
    print("WARNING: ABOUT TO CLEAR ALL DATA FROM ALL TRADES TABLES")
    print("Continue? (type yes)")
    if input("> ").lower() != "yes":
        print("No data was altered")
        return False
    CurrencyValue.objects.all().delete()
    print("Cleared data from all tables.")
    return True

def load_all(years_to_load, months_to_load):
    # load currency values:
    # date,currency,valueInUSD
    for yeardir in (DATA_DIR/'currencyValues').iterdir():
        if years_to_load != "all" and yeardir.name not in years_to_load:
            continue
        for monthdir in yeardir.iterdir():
            if months_to_load != "all" and monthdir.name not in months_to_load:
                continue
            for f in monthdir.iterdir():
                CurrencyValue.objects.bulk_create([
                    CurrencyValue(

                        date=datetime.strptime(l[0], "%d/%m/%Y").date(),
                        currency=l[1],
                        value=Decimal(l[2]))
                    for l in get_csv(f)
                ])
            print(monthdir)

def main():
    if not clear_data():
        print("WARNING: You did not clear data previously in the db. (THIS COULD BE PROBLEMATIC)")
        print("Continue? (type yes)")
        if input("> ").lower() != "yes":
            print("EXITING")
            return
    print("Give comma separated list of years to load (type all for all years)")
    print("WARNING: Loading all years will take a WHILE. last warning")
    s = input("> ").strip()
    if s.lower() != "all":
        years = [y.strip() for y in s.split(',')]
    else:
        years = "all"
    print("Give comma separated list of months (of specified years) to load (type all for all months)")
    print("NOTE: Months names are case sensitive")
    s = input("> ").strip()
    if s.lower() != "all":
        months = [m.strip() for m in s.split(',')]
    else:
        months = "all"
    load_all(years, months)
if __name__ == "__main__":
    main()
