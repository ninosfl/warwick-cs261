from django.contrib import admin
from .models import (Company, Product, CurrencyValues, Currency,
                     DerivativeTrades, ProductPrices, StockPrices)

# Register your models here.
admin.register(Company)
admin.register(Product)
admin.register(CurrencyValues)
admin.register(Currency)
admin.register(DerivativeTrades)
admin.register(ProductPrices)
admin.register(StockPrices)
