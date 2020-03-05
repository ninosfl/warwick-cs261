from django.shortcuts import render

def enter(request):
    if request.method == "POST":
        # proccess entered data contained in request.POST
        return NotImplemented
    return render(request, "trades/new.html", {"stuff": "Stuff can simply be passed in a dictionary"})


def form(request):
    return render(request, "newtrades/form.html")


def home(request):
    return render(request, "trades/home.html")
