from django.urls import path, include
from .views import enter

urlpatterns = [
    path("", enter, name='trades-new')
]