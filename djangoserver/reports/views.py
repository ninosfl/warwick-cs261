from django.shortcuts import render

def yearly_report(request):
    if request.method == "POST":
        mockdata = [
            {
                "date": "1 january",
                "amount": "loads"
            },
            {
                "date": "2 january",
                "amount": "maybe less"
            },
            {
                "date": "1 april",
                "amount": "incredible quantity"
            }
        ]
        context = {
            "method": request.method,
            "year": request.POST.get("year"),
            "yearlydata": mockdata
        }
        return render(request, "reports/yearly.html", context)
    return render(request, "reports/yearly.html")
