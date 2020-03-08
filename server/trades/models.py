import random
import string
from decimal import Decimal
from pathlib import Path
from datetime import datetime

from django.utils import timezone
from django.db import models

DATA_DIR = Path("../data")

SAMPLE_CURRENCY_VALUES_CACHE = None

"""
Permanent-ish data found in main data directory
companyCodes.csv
    companyName
    companyTradeID
productSellers.csv
    product
    companyID

The following are daily data, accessed at name/YYYY/MMM/DDMMYYYY.csv
for any particular day of the year
currencyValues
    date
    currency
    valueInUSD
derivativeTrades 
    dateOfTrade
    tradeID
    product
    buyingParty
    sellingParty
    notionalAmount
    notionalCurrency
    quantity
    maturityDate
    underlyingPrice
    underlyingCurrency
    strikePrice
productPrices 
    date
    product
    marketPrice
stockPrices
    date
    companyID
    stockPrice
"""

def generate_company_id():
    """
    Generates a unique company id which consists of 4 capital letters followed
    by 2 numbers. Sample id: ZXVX98
    """
    while True:
        new_id = ''.join(
            [random.choice(string.ascii_uppercase) for _ in range(4)]
            + [str(random.choice(string.digits)) for _ in range(2)]
        )
        try:
            Company.objects.get(id=new_id)
        except Company.DoesNotExist:
            return new_id

def generate_trade_id():
    """
    Generates a unique trade id which consists of 8 capital letters followed
    by 8 numbers. Sample id: ACZCWXGS73862601
    """
    while True:
        new_id = ''.join(
            [random.choice(string.ascii_uppercase) for _ in range(8)]
            + [random.choice(string.digits) for _ in range(8)]
        )
        try:
            DerivativeTrade.objects.get(trade_id=new_id)
        except DerivativeTrade.DoesNotExist:
            return new_id


class Company(models.Model):
    id = models.CharField(primary_key=True, max_length=6, default=generate_company_id)
    # 36 max name length found in data
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    # 39 max name length found in data, and unique
    name = models.CharField(primary_key=True, max_length=50)
    # one company may sell multiple products.
    seller_company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class CurrencyValue(models.Model):
    date = models.DateField()
    # 3 letter code
    currency = models.CharField(max_length=3)
    # max 4 decimal places found in data
    value = models.DecimalField(max_digits=16, decimal_places=6)
    class Meta:
        unique_together = ("date", "currency")

class DerivativeTrade(models.Model):
    class ProductTypes(models.TextChoices):
        STOCKS = 'S', 'Stocks'
        PRODUCT = 'P', 'Product'

    trade_id = models.CharField(primary_key=True, max_length=16, default=generate_trade_id)
    date_of_trade = models.DateTimeField(default=timezone.now)
    product_type = models.CharField(max_length=1,
                                    choices=ProductTypes.choices,
                                    default=ProductTypes.STOCKS)
    buying_party = models.ForeignKey(Company, on_delete=models.CASCADE,
                                     related_name="trades_buying")
    selling_party = models.ForeignKey(Company, on_delete=models.CASCADE,
                                      related_name="trades_selling")
    notional_currency = models.CharField(max_length=3)
    quantity = models.IntegerField()
    maturity_date = models.DateField()
    underlying_price = models.DecimalField(max_digits=16, decimal_places=4)
    underlying_currency = models.CharField(max_length=3)
    strike_price = models.DecimalField(max_digits=16, decimal_places=4)

    @property
    def product_or_stocks(self):
        """ Returns the name of the traded product (if one exists) or otherwise 'Stocks' """
        if self.product_type == "P":
            return self.traded_product.product.name
        return "Stocks"

    @property
    def notional_amount(self):
        """
        Notional amount is a calculated field based on quantity and underlying
        price. Must then be converted to notional currency.
        """
        return round(convert_currency(
            self.date_of_trade.date(),
            self.quantity * self.underlying_price,
            self.underlying_currency, self.notional_currency), 4)

    def __str__(self):
        return ', '.join([
            self.date_of_trade.strftime("%H:%M"),
            self.buying_party.name,
            self.selling_party.name,
            'Stocks' if self.product_type == 'S' else self.traded_product.product.name
        ])

class ProductPrice(models.Model):
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("date", "product")

class StockPrice(models.Model):
    date = models.DateField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("date", "company")

class TradeProduct(models.Model):
    trade = models.OneToOneField(DerivativeTrade, primary_key=True, 
                                 on_delete=models.CASCADE, related_name="traded_product")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


def _get_sample_currency_values():
    """
    Loads the default list of currencies and their values from 
    DATA_DIR/sample_currencies.csv. This file is only accessed once when the
    function is first called and subsequent executions return a cached version.
    This function should not be called directly but through the
    get_currency_values below.
    """
    global SAMPLE_CURRENCY_VALUES_CACHE # pylint: disable=global-statement
    if SAMPLE_CURRENCY_VALUES_CACHE is None:
        with (DATA_DIR / "sample_currencies.csv").open("r") as file_obj:
            SAMPLE_CURRENCY_VALUES_CACHE = {
                c:Decimal(v) for c, v in (l.split(',') for l in file_obj)}
    return SAMPLE_CURRENCY_VALUES_CACHE

def remove_currencies_on_date(date):
    """ Delete all currency-values for a specific date. Only for testing purposes! """
    CurrencyValue.objects.filter(date=date).delete()

def get_currency_values(date):
    """
    date must be a date object or a string in the format %Y-%m-%d
    Returns a mapping (dict) of currency-value. If no currencies exist for that
    day a list of sample currencies is loaded and then each value is transformed
    +/-10% and stored as that date's currency-values. This resulting mapping is
    then returned.
    """
    retrieved_currencies = CurrencyValue.objects.filter(date=date)
    if any(retrieved_currencies):
        return {cv.currency:cv.value for cv in retrieved_currencies}
    generated_values = {
        c: round(Decimal(random.uniform(0.998, 1.002)) * v, 6) # max 6 decimal places
        for c, v in _get_sample_currency_values().items()
    }
    generated_values["USD"] = 1
    CurrencyValue.objects.bulk_create([
        CurrencyValue(currency=c, value=v, date=date)
        for c, v in generated_values.items()
    ])
    return generated_values

def get_currencies(date):
    """
    date must be a date object or a string in the format %Y-%m-%d
    Returns all currencies that exist on a specified day, if none exist 
    currencies for that date they will be generated as per get_currency_values
    """
    return list(get_currency_values(date).keys())

def convert_currency(date, value, currency1, currency2):
    """
    date must be a date object or a string in the format %Y-%m-%d
    Convert a value from currency1 to currency2 based on specified date's rate.
    What is stored in CurrencyValue table is valueInUSD hence value is USD/currency
    To convert value V from currency C1 to currency C2:

                  C1              C1      USD              USD     USD    
    V * C1 = V * ---- * C2 = V * ----- * ----- * C2 = V * ----- : ----- * C2 
                  C2              USD     C2               C2      C1     
    
    Ignoring final C2 which is the units (i.e. the resulting currency) and
    with USD/C2 and USD/C1 being what's stored in CurrencyValues it is a simple
    matter of multiplication and to perform the conversion. Result is a Decimal
    """
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")
    currencyvals = get_currency_values(date)
    return Decimal(value) * currencyvals[currency1] / currencyvals[currency2]
