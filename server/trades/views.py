from django.shortcuts import render
from django.db import models
from learning.models import (TrainData, MetaData)
from trades.models import DerivativeTrade,CurrencyValue
import datetime



def enter(request):
    if request.method == "POST":
        # proccess entered data contained in request.POST
        return NotImplemented
    return render(request, "trades/new.html", {"stuff": "Stuff can simply be passed in a dictionary"})


def home(request):
    return render(request, "trades/home.html")
