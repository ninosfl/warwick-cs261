from django.urls import path
from .views import (form, list_months, list_days, list_years, delete_trade,
                    list_all_of_day, view_trade, edit_trade)

urlpatterns = [
    path("", list_years, name="trades-list-years"), 
    path("<int:year>/", list_months, name="trades-list-months"),
    path("<int:year>/<int:month>/", list_days, name="trades-list-days"),
    path("<int:year>/<int:month>/<int:day>/", list_all_of_day, name="trades-list-all"),
    path("<int:year>/<int:month>/<int:day>/<str:trade_id>/", view_trade, name="trades-view-trade"),
    path("form/", form, name='enter-new-trade'),
    path("edit/<str:trade_id>/", edit_trade, name='trades-edit'),
    path("delete/<str:trade_id>/", delete_trade, name="trades-delete")
]