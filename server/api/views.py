from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def api_main(request):
    return JsonResponse({"implemented": False})
