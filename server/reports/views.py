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
    html = "<html><body>This is the <em>years</em> page.</body></html>"
    return HttpResponse(html)

def months(request, year: int):
    # Check for year validity
    now = datetime.datetime.now()
    if year > now.year:
        html = f"<html><body>The year {year} is in the future. There are no trades listed.</body></html>"
    elif year < 1970:
        html = f"<html><body>The year {year} is too far in the past. There are no trades listed.</body></html>"
    else:
        html = f"<html><body>This is the <em>months</em> page. The given year is {year}.</body></html>"
    
    return HttpResponse(html)

def days(request, year: int, month: int):
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
            # for m in range (1, max(month, now.month) + 1):
            html = f"<html><body>This is the <em>days</em> page. The given year is {year}, month is {month}.</body></html>"
    return HttpResponse(html)

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
