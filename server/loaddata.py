from django.forms.models import model_to_dict
from trades.models import DerivativeTrade

reports = DerivativeTrade.objects.select_related('traded_product')

dictl = []

for report in reports:
    reportDict = model_to_dict(report)
    if reportDict['product_type'] == 'P':
        reportDict.update({'product': report.traded_product.product})
    dictl.append(reportDict)
