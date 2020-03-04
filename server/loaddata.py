from django.forms.models import model_to_dict
from trades.models import DerivativeTrade

reports = DerivativeTrade.objects.all()

dictl = []

for report in reports:
    dictl.append(model_to_dict(report))