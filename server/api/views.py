import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from trades.models import Company, Product, CurrencyValue
from learning.models import Correction
from sklearn.metrics import mean_squared_error
from keras.models import load_model
import tensorflow as tf
from keras import backend as K
import datetime
from math import floor
import numpy as np
import pickle
import logging

from jellyfish import damerau_levenshtein_distance as edit_dist
import os
try:
    print(os.getcwd())
except KeyError:
    print("failed")
    user_paths = []
runningMetaData = pickle.load(open(r'api/runningMetaData.p','rb'))
@csrf_exempt
def api_main(request, func):
    """
    API main view. Takes a request and a function which performs back-end
    processing on request data.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"})
    try:
        json_dict = json.loads(request.body.decode("utf-8"))
    except json.decoder.JSONDecodeError:
        print(request.body.decode("utf-8"))
        return JsonResponse({"success": False, "error": "Malformed JSON"})
    return JsonResponse(func(json_dict))

def get_company(name):
    """ Returns the Company with that exact name or None if it does not exist """
    try:
        return Company.objects.get(name=name)
    except Company.DoesNotExist:
        return None

def get_product(name):
    """ Returns the Product with that exact name or None if it does not exist """
    try:
        return Product.objects.get(name=name)
    except Product.DoesNotExist:
        return None

def closest_matches(x, ws,commonCorrectionField="",correction_function=min):
    """
    Given a string and an iterable of strings returns the 5 with the smallest
    edit distance in order of the closest string first. All strings with edit
    distance > 5 are filtered out.
    """
    timesCorrected = {}
    if commonCorrectionField:
        for q in Correction.objects.filter(old_val=x,field=commonCorrectionField):
            timesCorrected[q.new_val] = q.times_corrected
    distances = {w: correction_function(edit_dist(x,w),  6-timesCorrected.get(w,0)) if commonCorrectionField else edit_dist(x, w)  for w in ws}
    filtered_distances = {w: d for w, d in distances.items() if d <= 5}
    sorted_distances = sorted(filtered_distances, key=filtered_distances.get)
    return sorted_distances[:5]

# TODO Optimisation when insertion of new CurrencyValues is sorted out
# @functools.lru_cache
# def get_currencies(date_param=timezone.now().date()):
#     return {c.currency for c in CurrencyValue.objects.get(date=date_param)}
# def currency_exists(currency_code):
#     currencies_today = get_currencies(timezone.now().date())
#     return currency_code in currencies_today

def currency_exists(currency_code):
    """ Checks for if the given currency exists in today's currencies """
    currencies_today = [c.currency for c in CurrencyValue.objects.get(date=timezone.now().date())]
    return currency_code in currencies_today

def mean_squared_error(x,y):
    return np.mean([(x-y)**2 for x,y in zip(x,y)])
def _load_model_from_path(path):
    graph = tf.get_default_graph()
    model = load_model(path)  # keras function
    return graph, model
def estimateErrorRatio(errorValue):
    values = {0.95:0.037751311451393696,
    0.8:0.02520727266310019,
    0.6:0.01780338673080255}
    if errorValue > values[0.6] and errorValue < values[0.8]:
        return 0.6 + (0.2*((errorValue - values[0.6])/(values[0.8]-values[0.6])))
    if errorValue > values[0.8] and errorValue < values[0.95]:
        return 0.8 + (0.15*((errorValue - values[0.8])/(values[0.95]-values[0.8])))
    if errorValue > values[0.95]:
        return 1
    if errorValue < values[0.6]:
        return 0
def ai_magic(data):
    graph, autoencoder = _load_model_from_path(r'api/mlModels/AutoEncoder/1176207.h5')
    def funcOrNone(x, func):
        try:
            return func(x)
        except:
            return None
    d = [int(x) for x in data['date'].split(',')]
    d = datetime.date(d[2],d[1],d[0])
    maturityDate = [int(x) for x in data['maturityDate'].split(',')]
    maturityDate = datetime.date(maturityDate[2],maturityDate[1],maturityDate[0])
    data['date'] = d
    data['maturityDate'] = maturityDate
    isStock = (data['product'] == 'Stocks')
    key = data['sellingParty'] if isStock else data['product']
    md = runningMetaData[key]
    hp = runningMetaData[key]['historicalPrice']
    smaPeriod = 20 # Time period for SMA calculations
    tp = 20 # Time period to calculate max and min price for price for
    day = runningMetaData['INFO_DAY'] # Running counter of which day for use in time period
    dmd = {'20DaySD': np.std(hp[-smaPeriod:]),'SMA': np.mean(hp[-smaPeriod:]),'UP': {'dayDifference': hp[-1] - hp[-2],'periodHigh': funcOrNone(hp[floor(day / tp) * tp:], max),'periodLow': funcOrNone(hp[floor(day / tp) * tp:], min)}}
    #print(dmd)
    #print(md)
    d = (
        (data['date'] - data['maturityDate']).days,
        data['quantity'],
        data['underLyingPrice'],
        data['strikePrice'] / dmd['SMA'],
        md['runningAvgClosePrice'],
        md['runningAvgQuantity'],
        md['runningAvgTradePrice'],
        dmd['20DaySD'],
        dmd['SMA'],
        dmd['UP']['dayDifference'],
        dmd['UP']['periodHigh'],
        dmd['UP']['periodLow'])
    minDay =-2191.0
    maxStrikePrice = 1.4
    normalizedData = (d[0] / minDay,
             d[1] / d[5],
             (d[2] / d[8] - 1) * 15,
             d[3] / maxStrikePrice,
             (d[7] / d[8] * 40) - 1,
             # (d[8] / d[6]) / maxSmaSD,
             (d[9] / d[8]) * 10,
             (d[10] / d[8] - 1) * 15,
             (d[11] / d[8] - 1) * 15)
    with graph.as_default():
        return {'success':True,'probability':estimateErrorRatio(mean_squared_error(autoencoder.predict(np.array([normalizedData]))[0],normalizedData))}

def validate_company(data):
    """ Validate single company. Expected data: name """
    result = {"success": False}
    if "name" not in data:
        result["error"] = "No name provided"
        return result

    if get_company(data["name"]) is None:
        result["error"] = "Company does not exist"
        result["success"] = False
    else:
        result["success"] = True

    # possibly a performance bottleneck
    result["names"] = closest_matches(data["name"], [c.name for c in Company.objects.all()])
    return result

def validate_product(data):
    """ Validate single product. Expected data: product, buyingParty, sellingParty"""
    result = {"success": False}

    result["sellingParty"] = data["sellingParty"]

    # Shape of request is as expected (all necessary data is given)
    not_specified = {"product", "sellingParty", "buyingParty"}.difference(data)
    if not_specified:
        result["error"] = f"Values not specified: {', '.join(not_specified)}"
        return result

    # Validate buyer existence
    if not get_company(data["buyingParty"]):
        result["error"] = "Buying company does not exist"
        return result

    # Validate seller existence
    seller = get_company(data["sellingParty"])
    if not seller:
        result["error"] = "Selling company does not exist"
        return result

    # Get closest distance matches 
    result["products"] = closest_matches(
        data["product"], [p.name for p in Product.objects.all()])

    # Validate product existence
    prod = get_product(data["product"])
    if not prod:
        result["error"] = "Product does not exist"
        return result

    # Validate product sold by given company
    if prod.seller_company != seller:
        result["error"] = "Selling party does not match product selling company."
        if prod.seller_company.name == data["buyingParty"]:
            result["error"] += " Buying and selling parties can be swapped around"
            result["canSwap"] = True
        else:
            result["canSwap"] = False
            result["sellingParty"] = prod.seller_company.name
        return result

    result["success"] = True
    return result

def validate_trade(data):
    """
    Validate a whole trade. Expected data: product, sellingParty, buyingParty,
    quantity, underlyingPrice, underlyingCurrency, strikePrice.
    """
    result = {"success": False}
    expected_keys = {"product", "sellingParty", "buyingParty", "quantity",
                     "underlyingPrice", "underlyingCurrency", "strikePrice"}
    not_specified = expected_keys.difference(data)
    if not_specified:
        result["error"] = f"Values not specified: {', '.join(not_specified)}"
        return result

    # Fields that should definitely be valid
    prod = get_product(data["product"])
    if not prod:
        result["error"] = "Product does not exist"
        return result
    seller = get_company(data["sellingParty"])
    if not seller:
        result["error"] = "Selling company does not exist"
        return result
    buyer = get_company(data["buyingParty"])
    if not buyer:
        result["error"] = "Buying party does not exist"
        return result

    # Validate quantity
    try: 
        if data["quantity"] <= 0:
            result["error"] = "Quantity must be positive"
            return result
    except ValueError:
        result["error"] = "Quantity given must be an integer"
        return result

    product_validation_result = validate_product(data)
    if not product_validation_result["success"]:
        return product_validation_result

    result["probabilityErroneous"] = ai_magic(data)
    result["success"] = True
    return result
@csrf_exempt
def correction(data):
    print(data)
    try:
        corr = Correction.objects.get(old_val=data['oldValue'],new_val=data['newValue'],field=data['field'])
        corr.times_corrected += 1
        corr.save()
    except Correction.DoesNotExist:
        Correction.objects.create(old_val=data['oldValue'],new_val=data['newValue'],field=data['field'],times_corrected=1)
    return {
        'success':'true'
    }


def validate_maturity_date(data):
    """
    Validate maturity date based on server's current time.
    Expected data: date
    """
    result = {"success": False}

    # Validate shape of data
    if "date" not in data:
        result["error"] = "No date specified."
        return result

    today = timezone.now().date()

    # Attempt to parse given date string
    try:
        date = datetime.strptime(data["date"], "%d/%m/%Y").date()
    except ValueError:
        result["error"] = "Invalid date string given. Expected format DD/MM/YYYY"
        return result

    # Validate date.
    if date < today:
        result["error"] = f"Date cannot be in the past. Server date is {today.strftime('%d/%m/%Y')}"
        return result

    result["success"] = True
    return result

def currencies(_, date_str=None):
    """
    Returns currencies for a specific date. If no date is specified the current
    server date is used. Date str must be in YYYY-MM-DD format.
    """
    if not date_str:
        date = timezone.now().date()
    else:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    return JsonResponse({
        "currencies": [c.currency for c in CurrencyValue.objects.filter(date=date)]
    })

### Additional stuff below ###

def company(_, company_name):
    """ View of a single company at path 'company/<company_name>/'' """
    comp = get_company(company_name)
    result = {
        "success": comp is not None,
        "suggestions": closest_matches(
            company_name, [c.name for c in Company.objects.all()],commonCorrectionField='companyName'
        ),
    }
    if comp:
        result["company"] = {
            "name": comp.name,
            "id": comp.id
        }
    return JsonResponse(result)

def product(_, product_name):
    """ View of a single product at path 'product/<product_name>' """
    prod = get_product(product_name)
    result = {"success": prod is not None}
    if prod:
        result["product"] = {
            "name": prod.name,
            "seller_company": prod.seller_company.name
        }
    result["suggestions"] = closest_matches(product_name, [p.name for p in Product.objects.all()])
    return JsonResponse(result)

def company_product(_, company_name, product_name):
    """
    View of a single product of a company at path
    'company/<company_name>/product/<product_name>'
    """
    result = {}
    comp = get_company(company_name)
    result["company_exists"] = bool(comp)
    if comp:
        result["product_suggestions"] = closest_matches(
            product_name, [p.name for p in comp.product_set.all()]
        )
    return JsonResponse(result)
