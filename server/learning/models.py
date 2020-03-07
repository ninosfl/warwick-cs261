from django.db import models


class Correction(models.Model):
    class Meta:
        unique_together = (('old_val', 'field','new_val'),)
    old_val = models.CharField(max_length=50)
    field = models.CharField(max_length=50)
    new_val = models.CharField(max_length=50)
    times_corrected = models.IntegerField()

class TrainData(models.Model):
    val1 = models.FloatField()
    val2 = models.FloatField()
    val3 = models.FloatField()
    val4 = models.FloatField()
    val5 = models.FloatField()
    val6 = models.FloatField()
    val7 = models.FloatField()
    val8 = models.FloatField()

class MetaData(models.Model):
    key = models.CharField(max_length=50,primary_key=True)
    runningAvgClosePrice = models.FloatField()
    runningAvgTradePrice = models.FloatField()
    runningAvgQuantity = models.FloatField()
    totalEntries = models.IntegerField()
    totalQuantity = models.BigIntegerField()
    trades = models.IntegerField()
