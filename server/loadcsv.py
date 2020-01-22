import csv
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from itertools import islice

from django.utils import timezone
from trades.models import (Product, Company, CurrencyValue, DerivativeTrade,
                           ProductPrice, StockPrice, DerivativeTradeProduct)

DATA_DIR = Path("../data")

def getCSV(file_path, skip_header=True, delimiter=','):
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file, delimiter=delimiter)
        if skip_header:
            next(reader)
        return [line for line in reader]

def clear_data():
    """WARNING: CLEARS ALL DATA FROM ALL TABLES"""
    print("WARNING: ABOUT TO CLEAR ALL DATA FROM ALL TRADES TABLES")
    print("continue? (type yes to continue)\n>", end=' ')
    if input().lower() == "yes":
        CurrencyValue.objects.all().delete()
        Company.objects.all().delete()
        Product.objects.all().delete()
        DerivativeTrade.objects.all().delete()
        ProductPrice.objects.all().delete()
        StockPrice.objects.all().delete()
        print("Cleared data from all tables.")
    else:
        print("No data was altered")

def load_all():
    # load Company
    Company.objects.bulk_create([
        Company(name=name, id=id)
        for name, id in getCSV(DATA_DIR/'companyCodes.csv')
    ])

    # load ProductSeller
    # FORMAT: name,company
    Product.objects.bulk_create([
        Product(name=l[0], seller_company_id=l[1])
        for l in getCSV('../data/productSellers.csv')
    ])

    # load currency values:
    # date,currency,valueInUSD
    for yeardir in islice((DATA_DIR/'currencyValues').iterdir(), 0, 1):
        for monthdir in yeardir.iterdir():
            for f in monthdir.iterdir():
                CurrencyValue.objects.bulk_create([
                    CurrencyValue(

                        date=datetime.strptime(l[0], "%d/%m/%Y").date(),
                        currency=l[1],
                        value=Decimal(l[2]))
                    for l in getCSV(f)
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
    for yeardir in islice((DATA_DIR/'derivativeTrades').iterdir(), 0, 1):
        for monthdir in yeardir.iterdir():
            for f in monthdir.iterdir():
                # DerivativeTrade.objects.bulk_create([
                #     DerivativeTrade(
                #         date_of_trade=datetime.strptime(l[0], "%d/%m/%Y %H:%M"),
                #         trade_id=l[1],
                #         product=Product.objects.get(name=l[2]),
                #         buying_party=Company.objects.get(id=l[3]),
                #         selling_party=Company.objects.get(id=l[4]),
                #         notional_amount=Decimal(l[5]),
                #         notional_currency=l[6],
                #         quantity=int(l[7]),
                #         maturity_date=datetime.strptime(l[8], "%d/%m/%Y"),
                #         underlying_price=Decimal(l[9]),
                #         underlying_currency=l[10],
                #         strike_price=Decimal(l[11]))
                #     for l in getCSV(f)
                # ]) 
                trades = []
                tradeproducts = []
                for l in getCSV(f):
                    trades.append(DerivativeTrade(
                        date_of_trade=current_tz.localize(
                            datetime.strptime(l[0], "%d/%m/%Y %H:%M")),
                        trade_id=l[1],
                        product_type=('S' if l[2] == "Stocks" else 'P'),
                        buying_party_id=l[3],
                        selling_party_id=l[4],
                        notional_amount=Decimal(l[5]),
                        notional_currency=l[6],
                        quantity=int(l[7]),
                        maturity_date=datetime.strptime(l[8], "%d/%m/%Y"),
                        underlying_price=Decimal(l[9]),
                        underlying_currency=l[10],
                        strike_price=Decimal(l[11])))
                    if l[2] != "Stocks":
                        tradeproducts.append(DerivativeTradeProduct(
                            trade=trades[-1], product_id=l[2]))
                DerivativeTrade.objects.bulk_create(trades)
                DerivativeTradeProduct.objects.bulk_create(tradeproducts)
            print(monthdir)

    """
    Load Product Prices
    0. date
    1. product
    2. marketPrice
    """
    for yeardir in islice((DATA_DIR/'productPrices').iterdir(), 0,1):
        for monthdir in yeardir.iterdir():
            for f in monthdir.iterdir():
                ProductPrice.objects.bulk_create([
                    ProductPrice(
                        date=datetime.strptime(l[0], "%d/%m/%Y").date(),
                        product_id=l[1],
                        price=Decimal(l[2]))
                    for l in getCSV(f)
                ])
            print(monthdir)

    """
    Load Stock Prices
    0. date
    1. companyID
    2. stockPrice
    """
    for yeardir in islice((DATA_DIR/'stockPrices').iterdir(), 0,1):
        for monthdir in yeardir.iterdir():
            for f in monthdir.iterdir():
                StockPrice.objects.bulk_create([
                    StockPrice(
                        date=datetime.strptime(l[0], "%d/%m/%Y").date(),
                        company_id=l[1],
                        price=Decimal(l[2]))
                    for l in getCSV(f)
                ])
            print(monthdir)

def main():
    clear_data()
    load_all()

if __name__ == "__main__":
    main()
