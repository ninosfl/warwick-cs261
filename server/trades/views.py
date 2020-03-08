from datetime import date
from calendar import Calendar

from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.utils import timezone
from trades.models import DerivativeTrade

def enter(request):
    if request.method == "POST":
        # proccess entered data contained in request.POST
        return NotImplemented
    return render(request, "trades/new.html", {"stuff": "Stuff can simply be passed in a dictionary"})

def delete_trade(_, trade_id):
    trade = get_object_or_404(DerivativeTrade, trade_id=trade_id)
    trade.delete()
    return redirect(reverse("home-page"))

def form(request):
    return render(request, "newtrades/form.html")

def view_trade(request):
    return render(request, "trades/home.html")

def edit_trade(request, trade_id):
    trade = get_object_or_404(DerivativeTrade, trade_id=trade_id)
    trade_data = {
        "dateOfTrade": trade.date_of_trade.strftime("%H:%M %d/%m/%Y"),
        "tradeID": trade.trade_id,
        "product": trade.product_or_stocks,
        "buyingParty": trade.buying_party.name,
        "sellingParty": trade.selling_party.name,
        "notionalAmount": trade.notional_amount,
        "notionalCurrency": trade.notional_currency,
        "quantity": trade.quantity,
        "maturityDate": trade.maturity_date.strftime("%d/%m/%Y"),
        "underlyingPrice": trade.underlying_price,
        "strikePrice": trade.strike_price,
        "underlyingCurrency": trade.underlying_currency,
    }
    return render(request, "newtrades/form.html", {"form_data": trade_data})


def home(request):
    return render(request, "trades/home.html")

def list_years(request):
    """ List all years available. """
    placeholder_years = [y for y in range(2020, 2000 - 1, -1)]
    context = {"years": placeholder_years}
    return render(request, "trades/years.html", context)

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
    return render(request, "trades/months.html", context)

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
    return render(request, "trades/days.html", context)

def list_all_of_day(request, year, month, day):
    context = {
        "trades": DerivativeTrade.objects.filter(date_of_trade__date=date(year, month, day)),
        "day": day,
        "month": month,
        "year": year,
        "editable": (timezone.now().date() - date(year, month, day)).days < 8
    }
    return render(request, "trades/trades_list.html", context)

def is_year_valid(year: int, now=timezone.now()):
    """ Checks if a given year is valid. """

    if year > now.year:
        error_message = f"The year {year} is in the future. There are no trades listed."
        return False, error_message

    if year < 1970:
        error_message = f"The year {year} is too far in the past. There are no trades listed."
        return False, error_message

    return True, None


def is_month_valid(year: int, month: int, now=timezone.now()):
    """ Checks if a given year and month pair are valid. """

    result, err = is_year_valid(year, now)
    if not result:
        return result, err

    if month < 1 or month > 12:
        error_message = f"Month values are from 1 to 12. The given month, {month}, is invalid."
        return False, error_message

    if year == now.year and month > now.month:
        error_message = f"The month {month} is in the future. There are no trades listed."
        return False, error_message

    return True, None


def is_day_valid(year: int, month: int, day: int, now=timezone.now()):
    """ Checks if a given year, month, and day are valid. """

    result, err = is_month_valid(year, month, now)
    if not result:
        return result, err

    if day not in get_days(year, month, now):
        error_message = f"There are no trades listed for {day}/{month}/{year}."
        return False, error_message

    return True, None


def get_months(year: int, now=timezone.now()):
    """ Given a year, get all the valid months within it. """

    if year == now.year:
        return list(range(1, min(12, now.month) + 1))

    return list(range(1, 12 + 1))


def get_days(year: int, month: int,
             now=timezone.now(), calendar=Calendar()):
    """ Given a year and a month, get all the valid days of that month of that year. """

    if year == now.year and month == now.month:
        return [d for d in calendar.itermonthdays(year, month)
                if d != 0 and d <= now.day]

    return [d for d in calendar.itermonthdays(year, month) if d != 0]
