from django.shortcuts import render
from django.http import HttpResponse
import datetime
from calendar import Calendar

# def yearly_report(request):
#     if request.method == "POST":
#         mockdata = [
#             {
#                 "date": "1 january",
#                 "amount": "loads"
#             },
#             {
#                 "date": "2 january",
#                 "amount": "maybe less"
#             },
#             {
#                 "date": "1 april",
#                 "amount": "incredible quantity"
#             }
#         ]
#         context = {
#             "method": request.method,
#             "year": request.POST.get("year"),
#             "yearlydata": mockdata
#         }
#         return render(request, "reports/yearly.html", context)
#     return render(request, "reports/yearly.html")

def years(request):
    placeholder_years = [y for y in range(2000, 2020 + 1)]
    context = { "years": placeholder_years }
    return render(request, "reports/years.html", context)

def months(request, year: int):
    # Check for year validity
    now = datetime.datetime.now()
    if year > now.year:
        html = f"<html><body>The year {year} is in the future. There are no trades listed.</body></html>"
        return HttpResponse(html)
    elif year < 1970:
        html = f"<html><body>The year {year} is too far in the past. There are no trades listed.</body></html>"
        return HttpResponse(html)
    else:

        # Get way to transform int months into month strings
        month_names = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }

        # Get valid lists of months (as integers)
        if year == now.year:
            months = [m for m in range(1, min(12, now.month) + 1)]
        else:
            months = [m for m in range(1, 12 + 1)]

        context = {
            "month_names": month_names,
            "months": months,
            "year": year
        }
        return render(request, "reports/months.html", context)

def days(request, year: int, month: int):
    # Check for year validity
    now = datetime.datetime.now()
    if year > now.year:
        html = f"<html><body>The year {year} is in the future. There are no trades listed.</body></html>"
        return HttpResponse(html)
    elif year < 1970:
        html = f"<html><body>The year {year} is too far in the past. There are no trades listed.</body></html>"
        return HttpResponse(html)
    else:

        # Check for month validity
        if month < 1 or month > 12:
            html = f"<html><body>Month values are from 1 to 12. The given month, {month}, is invalid."
            return HttpResponse(html)
        else:

            # Get list of valid days for that month
            c = Calendar()
            if month == now.month:
                days = [d for d in c.itermonthdays(year, month) if d != 0 and d <= now.day]
            else:
                days = [d for d in c.itermonthdays(year, month) if d != 0]
            
            context = {
                "days": days,
                "year": year,
                "month": month
            }
            return render(request, "reports/days.html", context)

def report(request, year: int, month: int, day: int):
    # Check for year validity
    now = datetime.datetime.now()
    if year > now.year:
        html = f"<html><body>The year {year} is in the future. There are no trades listed.</body></html>"
    elif year < 1970:
        html = f"<html><body>The year {year} is too far in the past. There are no trades listed.</body></html>"
    else:

        # Check for month validity
        if month < 1 or month > 12:
            html = f"<html><body>Month values are from 1 to 12. The given month, {month}, is invalid."
        else:

            # Check for day validity
            c = Calendar()
            # Get list of valid days for that month
            days = [d for d in c.itermonthdays(year, month) if d != 0]
            if day not in days:
                html = f"<html><body>{day} in not a valid day in month {month} of the year {year}.</body></html>"
            else:

                #for d in range(1, max(day, days[-1]) + 1):
                html = f"<html><body>This is the <em>report</em> page. The given year is {year}, month is {month}, day is {day}.</body></html>"
    return HttpResponse(html)
