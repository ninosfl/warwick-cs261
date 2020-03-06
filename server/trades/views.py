from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from trades.models import DerivativeTrade

def enter(request):
    if request.method == "POST":
        # proccess entered data contained in request.POST
        return NotImplemented
    return render(request, "trades/new.html", {"stuff": "Stuff can simply be passed in a dictionary"})

def form(request):
    return render(request, "newtrades/form.html")

def view_trade(request):
    return render(request, "trades/home.html")

def edit_trade(request, trade_id):
    trade = get_object_or_404(DerivativeTrade, trade_id=trade_id)
    trade_data = {
        "dateOfTrade": trade.date_of_trade,
        "tradeID": trade.trade_id,
        "product": trade.product_or_stocks,
        "buyingParty": trade.buying_party.name,
        "sellingParty": trade.selling_party.name,
        "notionalAmount": trade.notional_amount,
        "notionalCurrency": trade.notional_currency,
        "quantity": trade.quantity,
        "maturityDate": trade.maturity_date,
        "underlyingPrice": trade.underlying_price
    }
    return render(request, "newtrades/form.html", {"form_data": trade_data})


def home(request):
    return render(request, "trades/home.html")

def list_years(request):
    """ List all years available. """
    placeholder_years = [y for y in range(2020, 2000 - 1, -1)]
    context = {"years": placeholder_years}
    return render(request, "reports/years.html", context)


def list_months(request, year: int):
    """ List all months available in the given year. """

    now = timezone.now()

    result, err = is_year_valid(year, now)
    if not result:
        context = {"error_message": err}
        return render(request, "errors/errorpage.html", context)

    # Year is valid - so get list of months (as integers)
    months = get_months(year, now)
    context = {
        "months": months,
        "year": year
    }
    return render(request, "reports/months.html", context)


def list_all_of_day(request):
    pass # TODO

def list_days(request, year: int, month: int):
    """ List all days available in the given month. """
    now = timezone.now()

    result, err = is_month_valid(year, month, now)
    if not result:
        context = {"error_message": err}
        return render(request, "errors/errorpage.html", context)

    # Get list of valid days for that month
    days = get_days(year, month, now)

    context = {
        "days": days,
        "year": year,
        "month": month
    }
    return render(request, "reports/days.html", context)
