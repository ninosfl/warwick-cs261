from django.shortcuts import render

def enter(request):
    if request.method == "POST":
        # proccess entered data contained in request.POST
        return NotImplemented
    return render(request, "trades/new.html", {"stuff": "Stuff can simply be passed in a dictionary"})


def form(request):
    return render(request, "newtrades/form.html")

def edit_trade(request):
    # TODO: Fetch trade data into Python dict
    return render(request, "newtrades/form.html", {"form_data": trade_data})


def home(request):
    return render(request, "trades/home.html")
