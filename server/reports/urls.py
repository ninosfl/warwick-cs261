from django.urls import path, include
from .views import yearly_report

urlpatterns = [
    path("", yearly_report, name="reports-yearly")
]
