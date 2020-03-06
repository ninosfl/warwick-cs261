from django.urls import path, include
from .views import enter, form

urlpatterns = [
    path("", enter, name='trades-new'),
    path("form/", form, name='enter-new-trade'),
]