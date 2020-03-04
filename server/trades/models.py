import random
import string
from django.utils import timezone
from django.db import models
from .utils import convert_currency

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
        return f"{self.name} Company"


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
    def notional_amount(self):
        """
        Notional amount is a calculated field based on quantity and underlying
        price. Must then be converted to notional currency.
        """
        return convert_currency(
            self.date_of_trade.date(),
            self.quantity * self.underlying_price,
            self.underlying_currency, self.notional_currency)

    def __str__(self):
        return ', '.join([
            str(self.date_of_trade.time()),
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
