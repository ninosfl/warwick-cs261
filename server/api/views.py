import json
from datetime import datetime
from math import floor
import datetime
import json
import logging
import os
import pickle

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from jellyfish import damerau_levenshtein_distance as edit_dist
from keras import backend as K
from keras.models import load_model
from trades.models import Company, Product, CurrencyValue,DerivativeTrade,StockPrice,ProductPrice
from learning.models import Correction,TrainData, MetaData
from currency_converter import CurrencyConverter
from keras.models import load_model
import tensorflow as tf
import datetime
from math import floor
import numpy as np
import pickle
import logging
from jellyfish import damerau_levenshtein_distance as edit_dist
c = CurrencyConverter(fallback_on_missing_rate=True)

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

def funcOrNone(x, func):
    try:
        return func(x)
    except:
        return None
def getPricesTraded(product,n_last,todayDate,key,isStock,adjustedUnderlying):
    prices = {
        todayDate:adjustedUnderlying
    }
    earliestDate = todayDate - datetime.timedelta(days=n_last)
    #lastTraded = DatesTraded.filter(key=key,date__lt=earliestDate.strftime('%Y-%m-%d')).order_by('-date')
    if isStock:
        for q in StockPrice.objects.filter(company__name=key, date__range=[
            (todayDate - datetime.timedelta(days=n_last+10)).strftime('%Y-%m-%d'),
            todayDate.strftime('%Y-%m-%d')]):
            prices[q.date] = q.price
    else:
        a = ProductPrice.objects.all()
        for q in ProductPrice.objects.filter(product__name=key, date__range=[
            (todayDate - datetime.timedelta(days=n_last+10)).strftime('%Y-%m-%d'),
            todayDate.strftime('%Y-%m-%d')]):
            prices[q.date] = q.price
    pricesList = prices.items()
    interpolated = []
    for day in range(n_last):
        day = todayDate - datetime.timedelta(days=day)
        if day not in prices:
            try:
                earliestAfter = min([x for x in pricesList if x[0] >= todayDate],key=lambda x:x[0])
                lastestBefore = max([x for x in pricesList if x[0] <= todayDate],key=lambda x:x[0])
                interpolated.append((day, (
                            (day - lastestBefore[0]).days / (earliestAfter[0] - lastestBefore[0]).days) * (
                                                 lastestBefore[1] - earliestAfter[1])))
            except:
                pass
                #print("Couldn't interpolate")
    for day,price in interpolated:
        prices[day] = price
    prices = [d[1] for d in sorted(prices.items(),key=lambda x:x[0]) if (todayDate - d[0]).days < n_last][:-1]
    return prices

def normalizeTrade(md,quantity,key,todayDate,maturityDate,adjustedStrike,adjustedUnderlying,isStock):
    hp = getPricesTraded(key, 31,todayDate,key,isStock,adjustedUnderlying)
    smaPeriod = 20
    tp = 20
    if len(hp) < 20:
        return False
    dayMetaData = {'20DaySD': np.std(hp),
                   'SMA': np.mean(hp[-smaPeriod:]),
                   'UP': {'dayDifference': hp[-1] - hp[-2],
                          'periodHigh': funcOrNone(
                              hp[-tp:],
                              max),
                          'periodLow': funcOrNone(
                              hp[-tp:],
                              min)
                          }}
    d = (
        (maturityDate - todayDate).days,
        quantity,
        adjustedUnderlying,
        float(adjustedStrike) / float(dayMetaData['SMA']),
        md.runningAvgClosePrice,
        md.runningAvgQuantity,
        md.runningAvgTradePrice,
        dayMetaData['20DaySD'],
        dayMetaData['SMA'],
        dayMetaData['UP']['dayDifference'],
        dayMetaData['UP']['periodHigh'],
        dayMetaData['UP']['periodLow'])
    d = [float(x) for x in d]
    minDay = 2191.0
    maxStrikePrice = 1.4
    normalizedData = (d[0] / minDay,
                      d[1] / d[5],
                      (d[2] / d[8] - 1) * 15,
                      d[3] / maxStrikePrice,
                      (d[7] / d[8] * 40) - 1,
                      (d[9] / d[8]) * 10,
                      (d[10] / d[8] - 1) * 15,
                      (d[11] / d[8] - 1) * 15)
    return normalizedData
def getCurrencyValue(x,todayDate): # Will get currency, will enter the currency in currencies table if not existent yet for future reference
    try:
        return CurrencyValue.objects.get(
        date=todayDate,
        currency=x).value
    except CurrencyValue.DoesNotExist:
        print(f"CurrencyDidNotExist {x}")
        c = CurrencyValue(date=todayDate,currency=x,value=c.convert(1,x,'USD',date=todayDate))
        c.save()
        return c.value
def recordLearningTrade(trade):
    isStock = trade.product_type == 'S'
    todayDate = datetime.date(trade.date_of_trade.year, trade.date_of_trade.month, trade.date_of_trade.day)
    maturityDate = datetime.date(trade.maturity_date.year, trade.maturity_date.month, trade.maturity_date.day)
    key = trade.selling_party if isStock else trade.traded_product.product
    md = MetaData.objects.get_or_create(key=key,defaults={"runningAvgClosePrice": 0,"runningAvgTradePrice":0,"runningAvgQuantity":0,"totalEntries":0,"totalQuantity":0, "trades":0})[0]
    adjustedUnderlying = trade.underlying_price / getCurrencyValue(trade.underlying_currency,todayDate)
    if isStock:
        p = StockPrice.objects.get_or_create(date=todayDate, company=key, defaults={'price':adjustedUnderlying})
    else:
        p = ProductPrice.objects.get_or_create(date=todayDate, product=key, defaults={'price':adjustedUnderlying})
    if p[1]:
        p = float(md.runningAvgClosePrice)
        q = float(md.totalEntries)
        md.runningAvgClosePrice = ((p * q) + float(adjustedUnderlying)) / (q + 1)
        md.totalEntries = q + 1
    day = (datetime.date.today() - datetime.date(2010,1,1)).days
    hp = getPricesTraded(key,31)
    #Reminder: retrain with adjusted TP system
    p = float(md.runningAvgTradePrice)
    n = float(md.totalQuantity)
    md.totalQuantity = Decimal(n) + trade.quantity
    md.runningAvgTradePrice =  ((p * n) + float(adjustedUnderlying) * float(trade.quantity)) / (n + trade.quantity)
    q = float(md.runningAvgQuantity)
    n = float(md.trades)
    md.runningAvgQuantity = ((q * n) + float(trade.quantity)) / (n + 1)
    md.trades = md.trades + 1
    md.save()
    cv2=float(getCurrencyValue(trade.notional_currency,todayDate))
    adjustedStrike = float(trade.strike_price) / cv2
    normalizedData = normalizeTrade(trade,md,key,todayDate,maturityDate,adjustedStrike,adjustedUnderlying,isStock)
    TrainData(val1=normalizedData[0],val2=normalizedData[1],val3=normalizedData[2],val4=normalizedData[3],val5=normalizedData[4],val6=normalizedData[5],val7=normalizedData[6],val8=normalizedData[7]).save()
    return True

def enterDummyTrade():
    recordLearningTrade(DerivativeTrade(
        date_of_trade=datetime.date(2010,1,18),
        trade_id='IDQYGGFS26417970',
        product_type='P',
        buying_party_id='VVXA11',
        selling_party_id='QBAP68',
        notional_currency='MXN',
        quantity=4000,
        maturity_date=datetime.date(2013,1,3),
        underlying_price=615,
        underlying_currency='CRC',
        strike_price=1882))
    return {"a":True}

def enterTrade(x):
    return enterDummyTrade()

def currency_exists(currency_code):
    """ Checks for if the given currency exists in today's currencies """
    currencies_today = [c.currency for c in CurrencyValue.objects.get(date=timezone.now().date())]
    return currency_code in currencies_today

def create_trade(data):
    required_data = {
        "product", "sellingParty", "buyingParty",
        "quantity", "underlyingCurrency", "underlyingPrice",
        "maturityDate", "notionalCurrency", "strikePrice"
    }
    not_specified = required_data.difference(data)
    if not_specified:
        return {"success": False, "error": f"Did not specify {', '.join(not_specified)}"}
    # Create the trade object and (possibly) the associated product
    new_trade = DerivativeTrade(
        product_type='S' if data["product"] == "Stocks" else 'P',
        selling_party__name=data["sellingParty"],
        buying_party__name=data["buyingParty"],
        quantity=data["quantity"],
        underlying_currency=data["underlyingCurrency"],
        underlying_price=data["underlyingPrice"],
        maturity_date=data["maturityDate"],
        notional_currency=data["notionalCurrency"],
        strike_price=data["strikePrice"],
    )
    new_trade.save()
    if new_trade.product_type == 'P':
        TradeProduct(trade=new_trade, product__name=data["product"])
    # Add generated fields
    data["tradeID"] = new_trade.id
    data["dateOfTrade"] = new_trade.date_of_trade
    data["notionalAmount"] = new_trade.notional_amount
    # Return success and the created object
    return {"success": True, "trade": data}

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
    graph, autoencoder = _load_model_from_path(r'api\mlModels\AutoEncoder\1176207.h5')
    d = [int(x) for x in data['date'].split(',')]
    d = datetime.date(d[2],d[1],d[0])
    maturityDate = [int(x) for x in data['maturityDate'].split(',')]
    maturityDate = datetime.date(maturityDate[2],maturityDate[1],maturityDate[0])
    data['date'] = d
    data['maturityDate'] = maturityDate
    isStock = (data['product'] == 'Stocks')
    key = data['sellingParty'] if isStock else data['product']
    adjustedStrikePrice = data['strikePrice'] / float(getCurrencyValue(data['notionalCurrency'],d))
    adjustedUnderlyingPrice = data['underlyingPrice'] / float(getCurrencyValue(data['underlyingCurrency'],d))
    md = MetaData.objects.get(key=key)
    normalizedData = normalizeTrade(md,data['quantity'],key,d,maturityDate,adjustedStrikePrice,adjustedUnderlyingPrice,isStock)
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
