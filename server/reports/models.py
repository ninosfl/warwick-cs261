from django.db import models

# FIXME remove: we want to query the database for all the reports on a certain day and get
# these printed as basic html.
# FIXME remove: if we're still using 'product_type', do a natural join on Product.seller_company
# and Report.selling_party


# class Report(models.Model):
#     date_of_trade = models.DateField()
#     trade_id = models.IntegerField()
#     product = models.CharField(max_length=50)
#     buying_party = models.IntegerField()  # A Company ID
#     selling_party = models.IntegerField()  # A Company ID
#     notional_amount = models.DecimalField(max_digits=20, decimal_places=4)
#     quantity = models.IntegerField()
#     notional_currency = models.CharField(max_length=3)
#     maturity_date = models.DateField()
#     underlying_price = models.DecimalField(max_digits=20, decimal_places=4)
#     underlying_currency = models.CharField(max_length=3)
#     strike_price = models.DecimalField(max_digits=20, decimal_places=4)
