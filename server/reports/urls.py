from django.urls import path
from .views import list_years, list_months, list_days, report

urlpatterns = [
    path("", list_years, name="report-list-years"),
    path("<int:year>/", list_months, name="report-list-months"),
    path("<int:year>/<int:month>/", list_days, name="report-list-days"),
    path("<int:year>/<int:month>/<int:day>/", report, name="report-get")
]
