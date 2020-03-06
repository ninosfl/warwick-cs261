from django.urls import path, include
from .views import enter, form, edit_trade

urlpatterns = [
    path("", enter, name='trades-new'),
    path("form/", form, name='enter-new-trade'),
    path("edit/<int:id>/", edit_trade, name='enter-new-trade')
]