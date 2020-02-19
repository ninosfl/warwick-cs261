from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
@csrf_exempt
def api_main(request, func):
    """API main view. Takes a request and a function which performs back-end
    processing on request data."""
    json_dict = json.loads(request.body.decode("utf-8"))
    json_dict['implemented'] = func(10)
    return JsonResponse(json_dict)
