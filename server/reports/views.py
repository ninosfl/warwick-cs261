from calendar import Calendar
from django.utils import timezone
from django.shortcuts import render

from trades.models import DerivativeTrade


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


def report(request, year: int, month: int, day: int):
    """ Fetch the report for the given day in the given month of the given year. """

    result, err = is_day_valid(year, month, day)

    if not result:
        context = {"error_message": err}
        return render(request, "errors/errorpage.html", context)

    # select_related() effectively performs a JOIN on the TradeProduct table to fetch the full product name.
    # filter() is similar to a WHERE clause in SQL, obtaining trades only for the chosen day.
    reports = DerivativeTrade.objects.select_related('traded_product').filter(
        date_of_trade__date=f"{year}-{month}-{day}").order_by("date_of_trade")

    context = {
        "year": year,
        "month": month,
        "day": day,
        "reports": reports,  # Returns the queryset.
    }

    return render(request, "reports/report.html", context)


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
