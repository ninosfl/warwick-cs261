from django.db import models

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

class Company(models.Model):
    # primary_key=True implies null=False and unique=True
    id = models.CharField(primary_key=True, max_length=6, blank=False)
    # 36 max name length found in data
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return f"Company {self.name}"

class Product(models.Model):
    # 39 max name length found in data, and unique
    name = models.CharField(primary_key=True, max_length=50, blank=False)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)

class CurrencyValues(models.Model):
    date = models.DateField()
    # max 4 decimal places found in data
    value = models.DecimalField(max_digits=12, decimal_places=6)

class Currency(models.Model):
    currency_code = models.CharField(primary_key=True, max_length=3)
    values = models.ManyToManyField(CurrencyValues)

class DerivativeTrades(models.Model):
    date_of_trade = models.DateTimeField()
    trade_id = models.CharField(primary_key=True, max_length=16)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buying_party = models.ForeignKey(Company, on_delete=models.CASCADE,
                                     related_name="buying_company")
    selling_party = models.ForeignKey(Company, on_delete=models.CASCADE,
                                      related_name="selling_company")
    notional_amount = models.DecimalField(max_digits=12, decimal_places=2)
    notional_currency = models.ForeignKey(Currency, on_delete=models.CASCADE,
                                          related_name="notional_currency")
    quantity = models.IntegerField()
    maturity_date = models.DateField()
    underlying_price = models.DecimalField(max_digits=12, decimal_places=2)
    underlying_currency = models.ForeignKey(Currency, on_delete=models.CASCADE,
                                            related_name="underlying_currency")
    strike_price = models.DecimalField(max_digits=12, decimal_places=2)

class ProductPrices(models.Model):
    date = models.DateField(null=False, blank=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class StockPrices(models.Model):
    date = models.DateField()
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
