from django.urls import path
from .views import (enter, form, list_months, list_days, list_years,
                    list_all_of_day, view_trade, edit_trade)

urlpatterns = [
    path("", enter, name='trades-new'),
    path("form/", form, name='enter-new-trade'),
    path("edit/<str:trade_id>/", edit_trade, name='trades-edit'),
    path("list/", list_years, name="trades-list-years"), 
    path("list/<int:year>/", list_months, name="trades-list-months"),
    path("list/<int:year>/<int:month>/", list_days, name="trades-list-days"),
    path("list/<int:year>/<int:month>/<int:day>/", list_all_of_day, name="trades-list-all"),
    path("list/<int:year>/<int:month>/<int:day>/<str:trade_id>/", view_trade, name="trades-view-trade"),
]