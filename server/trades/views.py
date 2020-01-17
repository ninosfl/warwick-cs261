from django.shortcuts import render

def enter(request):
    if request.method == "POST":
        # proccess entered data contained in request.POST
        return NotImplemented
    return render(request, "trades/new.html")
