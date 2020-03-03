from django.db import models


class Correction(models.Model):
    class Meta:
        unique_together = (('old_val', 'field','new_val'),)
    old_val = models.CharField(max_length=50)
    field = models.CharField(max_length=50)
    new_val = models.CharField(max_length=50)
    times_corrected = models.IntegerField()
