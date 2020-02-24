from django.db import models

class Report(models.Model):
	date_of_trade = models.DateField()
	trade_id = models.IntegerField()
	product = models.CharField(max_length=50)
    buying_party = models.IntegerField() # Company ID
    selling_party = models.IntegerField()
    notional_amount = models.FloatField() # TODO: Specify to two decimal places?
    quantity = models.Integer()