from django.shortcuts import render
from django.http import HttpResponse

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
    html = f"<html><body>This is the <em>months</em> page. The given year is {year}.</body></html>"
    return HttpResponse(html)

def days(request, year: int, month: int):
    html = f"<html><body>This is the <em>days</em> page. The given year is {year}, month is {month}.</body></html>"
    return HttpResponse(html)

def report(request, year: int, month: int, day: int):
    html = f"<html><body>This is the <em>report</em> page. The given year is {year}, month is {month}, day is {day}.</body></html>"
    return HttpResponse(html)
