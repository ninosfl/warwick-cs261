import csv
from pathlib import Path
from datetime import datetime
from decimal import Decimal

from django.utils import timezone
from trades.models import (Product, Company, CurrencyValue, DerivativeTrade,
                           ProductPrice, StockPrice, TradeProduct)

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
    Company.objects.all().delete()
    Product.objects.all().delete()
    DerivativeTrade.objects.all().delete()
    ProductPrice.objects.all().delete()
    StockPrice.objects.all().delete()
    print("Cleared data from all tables.")
    return True

def load_all(years_to_load, months_to_load):
    # load Company
    Company.objects.bulk_create([
        Company(name=name, id=id)
        for name, id in get_csv(DATA_DIR/'companyCodes.csv')
    ])
    print(DATA_DIR/'companyCodes.csv')

    # load ProductSeller
    # FORMAT: name,company
    Product.objects.bulk_create([
        Product(name=l[0], seller_company_id=l[1])
        for l in get_csv(DATA_DIR/'productSellers.csv')
    ])
    print(DATA_DIR/'productSellers.csv')

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
    """
    load Derivative Trades 
        0. dateOfTrade
        1. tradeID
        2. product
        3. buyingParty
        4. sellingParty
        5. notionalAmount
        6. notionalCurrency
        7. quantity
        8. maturityDate
        9. underlyingPrice
        10. underlyingCurrency
        11. strikePrice
    """

    current_tz = timezone.get_current_timezone()
    for yeardir in (DATA_DIR/'derivativeTrades').iterdir():
        if years_to_load != "all" and yeardir.name not in years_to_load:
            continue
        for monthdir in yeardir.iterdir():
            if months_to_load != "all" and monthdir.name not in months_to_load:
                continue
            for f in monthdir.iterdir(): 
                trades = []
                tradeproducts = []
                for l in get_csv(f):
                    trades.append(DerivativeTrade(
                        date_of_trade=current_tz.localize(
                            datetime.strptime(l[0], "%d/%m/%Y %H:%M")),
                        trade_id=l[1],
                        product_type=('S' if l[2] == "Stocks" else 'P'),
                        buying_party_id=l[3],
                        selling_party_id=l[4],
                        # notional_amount=Decimal(l[5]),
                        notional_currency=l[6],
                        quantity=int(l[7]),
                        maturity_date=datetime.strptime(l[8], "%d/%m/%Y"),
                        underlying_price=Decimal(l[9]),
                        underlying_currency=l[10],
                        strike_price=Decimal(l[11])))
                    if l[2] != "Stocks":
                        tradeproducts.append(TradeProduct(
                            trade=trades[-1], product_id=l[2]))
                DerivativeTrade.objects.bulk_create(trades)
                TradeProduct.objects.bulk_create(tradeproducts)
            print(monthdir)

    """
    Load Product Prices
    0. date
    1. product
    2. marketPrice
    """
    for yeardir in (DATA_DIR/'productPrices').iterdir():
        if years_to_load != "all" and yeardir.name not in years_to_load:
            continue
        for monthdir in yeardir.iterdir():
            if months_to_load != "all" and monthdir.name not in months_to_load:
                continue
            for f in monthdir.iterdir():
                ProductPrice.objects.bulk_create([
                    ProductPrice(
                        date=datetime.strptime(l[0], "%d/%m/%Y").date(),
                        product_id=l[1],
                        price=Decimal(l[2]))
                    for l in get_csv(f)
                ])
            print(monthdir)

    """
    Load Stock Prices
    0. date
    1. companyID
    2. stockPrice
    """
    for yeardir in (DATA_DIR/'stockPrices').iterdir():
        if years_to_load != "all" and yeardir.name not in years_to_load:
            continue
        for monthdir in yeardir.iterdir():
            if months_to_load != "all" and monthdir.name not in months_to_load:
                continue
            for f in monthdir.iterdir():
                StockPrice.objects.bulk_create([
                    StockPrice(
                        date=datetime.strptime(l[0], "%d/%m/%Y").date(),
                        company_id=l[1],
                        price=Decimal(l[2]))
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
