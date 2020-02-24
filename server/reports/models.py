from django.db import models

class Report(models.Model):
	date_of_trade = models.DateField()
	trade_ID = models.IntegerField()
	product = models.CharField(max_length=50)