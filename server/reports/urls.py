from django.urls import path, include
from .views import years, months, days, report

urlpatterns = [
    path("", years, name="report-list-years"),
    path("<int:year>/", months, name="report-list-months"),
    path("<int:year>/<int:month>/", days, name="report-list-days"),
    path("<int:year>/<int:month>/<int:day>/", report, name="report-get")
]
