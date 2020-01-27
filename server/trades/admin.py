from django.contrib import admin
from .models import (Company, Product, CurrencyValue,
                     DerivativeTrade, ProductPrice, StockPrice)

# Register your models here.
admin.site.register(Company)
admin.site.register(Product)
admin.site.register(CurrencyValue)
admin.site.register(DerivativeTrade)
admin.site.register(ProductPrice)
admin.site.register(StockPrice)
