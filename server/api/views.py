import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from trades.models import Company

# Create your views here.
@csrf_exempt
def api_main(request, func):
    """API main view. Takes a request and a function which performs back-end
    processing on request data."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error_message": "Invalid method"})
    try:
        json_dict = json.loads(request.body.decode("utf-8"))
    except json.decoder.JSONDecodeError:
        return JsonResponse({"success": False, "error_message": "Malformed JSON"})
    return JsonResponse(func(json_dict))

def validate_company(data):
    if "name" not in data:
        return {"success": False, "error_message": "No name provided"}
    # result = {}
    try:
        Company.objects.get(name=data["name"])
        result = {
            "success": True,
            "name": data["name"]
        }
    except Company.DoesNotExist:
        result = {
            "success": False,
            "name": [c.name for c in Company.objects.filter(name__startswith=data["name"])[:5]]
        }
    return result

def validate_product(data):
    return {}

def ai_magic(data):
    return {}

def validate_maturity_date(data):
    return {}
