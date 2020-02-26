import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from trades.models import Company
from django.utils import timezone

from jellyfish import damerau_levenshtein_distance as dist


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
    try:
        Company.objects.get(name=data["name"])
        result = {"success": True}
    except Company.DoesNotExist:
        result = {"success": False}
        # do not add too many companies, or this dies (all companies must fit in memory)
        # also this levenshtein distance calculation on all available company names kills
        # perfomance.
    distances = {
        c.name: dist(data["name"], c.name)
        for c in Company.objects.all()
    }
    filtered_distances = {w: d for w, d in distances.items() if d <= 5}
    sorted_distances = sorted(filtered_distances, key=distances.get)
    result["names"] = sorted_distances[:5]
    return result

def validate_product(data):
    return {}

def validate_trade(data):
    ai_magic()
    data
    return {"success": True}

def ai_magic():
    pass

def validate_maturity_date(data):
    today = timezone.now().date()

    # Attempt to parse given date string
    try:
        date = datetime.strptime(data["date"], "%d/%m/%Y").date()
    except ValueError:
        return {
            "success":False,
            "error_message": "Invalid date string given. Expected format DD/MM/YYYY"
        }

    # Validate date.
    if date <= today:
        return {
            "success": False,
            "error_message": f"Date must be in the future. Today is {today.strftime('%d/%m/%Y')}"
        }

    return {"success": True}
