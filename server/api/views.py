from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
import json
import re

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from jellyfish import damerau_levenshtein_distance as edit_dist
from keras.models import load_model
import tensorflow.compat.v1 as tf
import tensorflow.compat.v1.keras as k
import  tensorflow.python.keras.backend as kb
import numpy as np
import pytz

from djangoserver.settings import TIME_ZONE
from learning.models import Correction, TrainData, MetaData
from trades.models import (Company, Product, CurrencyValue, DerivativeTrade,
                           StockPrice, ProductPrice, TradeProduct, 
                           convert_currency, get_currencies)

tf.disable_v2_behavior()
graph = tf.get_default_graph()
t_session = tf.Session(graph=tf.Graph())

DATETIME_REGEX = re.compile("(?P<hours>[0-9]+):(?P<minutes>[0-9]{2,2})(:(?P<seconds>[0-9]{2,2}))?"
                            +" (?P<day>[0-9]+)/(?P<month>[0-9]+)"
                            +"/(?P<year>(?P<year2>[0-9]{2,2})|(?P<year4>[0-9]{4,4}))")

def load_model_from_path(path):
    global model
    with t_session.graph.as_default():
        try:
            k.set_session(t_session)
        except AttributeError:
            kb.set_session(t_session)
        model = load_model(path)
        return model
autoencoder = load_model_from_path('api/mlModels/AutoEncoder/2217570.h5')

date_format_parse = "%d/%m/%Y"  # Was "%Y-%m-%d"

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

      
def closest_matches(x, ws, commonCorrectionField="", correction_function=min):
    """
    Given a string and an iterable of strings returns the 5 with the smallest
    edit distance in order of the closest string first. All strings with edit
    distance > 5 are filtered out.
    """
    times_corrected = {}

    if commonCorrectionField:
        for q in Correction.objects.filter(old_val=x, field=commonCorrectionField):
            times_corrected[q.new_val] = q.times_corrected
    distances = {
        w: correction_function(edit_dist(x, w), 6 - times_corrected.get(w, 0)) if commonCorrectionField else edit_dist(
            x,
            w)
        for w in ws}
    
    filtered_distances = ((w,d) for w, d in distances.items() if d <= 5)
    sorted_distances = sorted(filtered_distances, key=lambda x:x[1])
    print(sorted_distances)

    return [x[0] for x in sorted_distances[:5]], sorted_distances[0][1] < 0 if sorted_distances else False

  
def get_prices_traded(n_last, today_date, key, is_stock, adjusted_underlying=None):
    """ n_last: number of days to look back on, today_date: as datetime latest date, key: name (company or product name)"""
    prices = {}
    if adjusted_underlying is not None:
        prices[today_date] = adjusted_underlying
    if is_stock:
        for q in StockPrice.objects.filter(company__name=key, date__range=[
                (today_date - timedelta(days=n_last + 10)).strftime('%Y-%m-%d'),
                today_date.strftime('%Y-%m-%d')]):
            prices[q.date] = q.price
    else:
        for q in ProductPrice.objects.filter(product__name=key, date__range=[
                (today_date - timedelta(days=n_last + 10)).strftime('%Y-%m-%d'),
                today_date.strftime('%Y-%m-%d')]):
            prices[q.date] = q.price
    prices_list = prices.keys()
    interpolated = []
    for day in range(n_last):
        day = today_date - timedelta(days=day)
        if day not in prices_list:
            days_after = [x for x in prices_list if x > day]
            days_before = [x for x in prices_list if x < day]
            if days_after and days_before:
                earliest_after = min(days_after)
                lastest_before = max(days_before)
                interpolated_price = float(prices[lastest_before]) + ((day - lastest_before).days / (earliest_after - lastest_before).days) * float(
                        prices[earliest_after] - prices[lastest_before])
                interpolated.append((day, interpolated_price))
    for day, price in interpolated:
        prices[day] = price
    prices = [float(d[1]) for d in sorted(prices.items(), key=lambda x: x[0]) if (today_date - d[0]).days < n_last][:-1]
    return prices


def normalize_trade(quantity, key, today_date, maturity_date, adjusted_strike, adjusted_underlying, is_stock):
    """ ML only """
    md = MetaData.objects.get(key=key)
    hp = get_prices_traded(31, today_date, key, is_stock, adjusted_underlying)
    smaPeriod = 20
    tp = 20
    if len(hp) < 20:
        return False
    day_meta_data = {'20DaySD': np.std(hp),
                     'SMA': np.mean(hp[-smaPeriod:]),
                     'UP': {'dayDifference': hp[-1] - hp[-2],
                            'periodHigh': max(
                                hp[-tp:]),
                            'periodLow': min(
                                hp[-tp:])
                            }}

    d = (
        (maturity_date - today_date).days,
        quantity,
        adjusted_underlying,
        float(adjusted_strike) / float(day_meta_data['SMA']),
        md.runningAvgClosePrice,
        md.runningAvgQuantity,
        md.runningAvgTradePrice,
        day_meta_data['20DaySD'],
        day_meta_data['SMA'],
        day_meta_data['UP']['dayDifference'],
        day_meta_data['UP']['periodHigh'],
        day_meta_data['UP']['periodLow'])
    # print(str(d))
    d = [float(x) for x in d]

    min_day = 2191.0
    max_strike_price = 1.4
    '''
    0: Day distance
    1: Quantity mean deviation
    2: Underlying Price Deviation from SMA
    3: Strike / SMA
    4: Volatility (SD/SMA)
    5: Day Change In Price vs recent mean
    6: Recent max / mean
    7: Recent min / mean
    '''
    normalized_data = (d[0] / min_day,
                       d[1] / d[5],
                       (d[2] / d[8] - 1) * 15,
                       d[3] / max_strike_price,
                       (d[7] / d[8] * 40) - 1,
                       (d[9] / d[8]) * 10,
                       (d[10] / d[8] - 1) * 15,
                       (d[11] / d[8] - 1) * 15)
    return normalized_data

def record_learning_trade(trade):
    isStock = trade.product_type == 'S'
    todayDate = trade.date_of_trade.date()
    maturityDate = trade.maturity_date
    key = trade.selling_party if isStock else trade.traded_product.product
    md = MetaData.objects.get_or_create(key=key, defaults={"runningAvgClosePrice": 0, "runningAvgTradePrice": 0,
                                                           "runningAvgQuantity": 0, "totalEntries": 0,
                                                           "totalQuantity": 0, "trades": 0})[0]
    adjusted_underlying = convert_currency(todayDate,trade.underlying_price,trade.underlying_currency,'USD')
    if isStock:
        p = StockPrice.objects.get_or_create(date=todayDate, company=key, defaults={'price': adjusted_underlying})
    else:
        p = ProductPrice.objects.get_or_create(date=todayDate, product=key, defaults={'price': adjusted_underlying})
    if p[1]:
        p = float(md.runningAvgClosePrice)
        q = float(md.totalEntries)
        md.runningAvgClosePrice = ((p * q) + float(adjusted_underlying)) / (q + 1)
        md.totalEntries = q + 1
    # Reminder: retrain with adjusted TP system
    p = float(md.runningAvgTradePrice)
    n = float(md.totalQuantity)
    md.totalQuantity = Decimal(n) + trade.quantity
    md.runningAvgTradePrice = ((p * n) + float(adjusted_underlying) * float(trade.quantity)) / (n + trade.quantity)
    q = float(md.runningAvgQuantity)
    n = float(md.trades)
    md.runningAvgQuantity = ((q * n) + float(trade.quantity)) / (n + 1)
    md.trades = md.trades + 1
    md.save()
    adjustedStrike = convert_currency(todayDate,trade.strike_price,trade.notional_currency,'USD')
    normalizedData = normalize_trade(trade, key, todayDate, maturityDate, adjustedStrike, adjusted_underlying,
                                     isStock)
    if normalizedData:
        TrainData(val1=normalizedData[0], val2=normalizedData[1], val3=normalizedData[2], val4=normalizedData[3],
                  val5=normalizedData[4], val6=normalizedData[5], val7=normalizedData[6], val8=normalizedData[7]).save()
    return True
  
  
def currency_exists(currency_code):
    """ Checks for if the given currency exists in today's currencies """
    currencies_today = [c.currency for c in CurrencyValue.objects.get(date=timezone.now().date())]
    return currency_code in currencies_today

def submit_trade(data):
    return modify_trade(data) if "tradeID" in data else create_trade(data)

def modify_trade(data):
    trade = DerivativeTrade.objects.get(trade_id=data["tradeID"])
    # Set product and product type
    old_is_stocks = trade.product_type
    new_is_stocks = data["product"] == "Stocks"
    if new_is_stocks:
        trade.product_type = 'S'
        if not old_is_stocks:
            trade.traded_product.delete()
    else: # Not stocks
        trade.product_type = 'P'
        trade.traded_product = TradeProduct(trade=trade, product=get_product(data["product"]))
        trade.traded_product.save()
    trade.maturity_date = str_to_date(data["maturityDate"])
    trade.strike_price = Decimal(data["strikePrice"])
    trade.underlying_price = Decimal(data["underlyingPrice"])
    trade.underlying_currency = data["underlyingCurrency"]
    trade.notional_currency = data["notionalCurrency"]
    trade.buying_party = get_company(data["buyingParty"])
    trade.selling_party = get_company(data["sellingParty"])
    trade.quantity = int(data["quantity"])
    trade.date_of_trade = str_to_datetime(data["dateOfTrade"])
    trade.save()
    return {"success": True}

def create_trade(data):
    # Verify all data keys exist
    required_data = {
        "product", "sellingParty", "buyingParty",
        "quantity", "underlyingCurrency", "underlyingPrice",
        "maturityDate", "notionalCurrency", "strikePrice"
    }
    not_specified = required_data.difference(data)
    if not_specified:
        return {"success": False, "error": f"Did not specify {', '.join(not_specified)}"}
    # Convert values to their appropriate types
    try:
        data["maturityDate"] = datetime.strptime(data["maturityDate"], date_format_parse).date()
    except ValueError:
        split_date = data['maturityDate'].split("/")
        data["maturityDate"] = "/".join(split_date[:2] + ["20" + split_date[2]])
        data["maturityDate"] = datetime.strptime(data["maturityDate"], date_format_parse).date()
    data["underlyingPrice"] = Decimal(data["underlyingPrice"])
    data["strikePrice"] = Decimal(data["strikePrice"])
    data["quantity"] = int(data["quantity"])
    # Create the trade object and (possibly) the associated product
    selling_company = get_company(data["sellingParty"])
    buying_company = get_company(data["buyingParty"])
    new_trade = DerivativeTrade(
        product_type='S' if data["product"] == "Stocks" else 'P',
        selling_party_id=selling_company.id,
        buying_party_id=buying_company.id,
        quantity=data["quantity"],
        underlying_currency=data["underlyingCurrency"],
        underlying_price=data["underlyingPrice"],
        maturity_date=data["maturityDate"],
        notional_currency=data["notionalCurrency"],
        strike_price=data["strikePrice"],
    )
    new_trade.save()
    if new_trade.product_type == 'P':
        traded_product = get_product(data["product"])
        TradeProduct.objects.create(trade=new_trade, product_id=traded_product.name)
    record_learning_trade(new_trade)
    # Add generated fields
    data["tradeID"] = new_trade.trade_id
    data["dateOfTrade"] = new_trade.date_of_trade
    data["notionalAmount"] = new_trade.notional_amount
    # Return success and the created object
    return {"success": True, "trade": data}


def squared_errors(x, y):
    return [(x - y) ** 2 for x, y in zip(x, y)]


def mean_squared_error(x,y):
    return np.average(squared_errors(x,y))


def determine_error(x, y):
    mse = squared_errors(x, y)
    return max(range(len(mse)), key=lambda x: mse[x])

def mse_error_causes(squared_error, error_ratio):
    entry_errors = [(error_message_and_field(x)[1], squared_error[x]) for x in range(len(squared_error))]
    entry_errors = sorted(entry_errors,key=lambda x:x[1],reverse=True)
    seen = set()
    return_errors = []
    for entry,error in entry_errors:
        if not return_errors or (entry not in seen and error > 0.07 / min(0.8,error_ratio)):
            return_errors.append(entry)
            seen.add(entry)
    return return_errors

def mse_error_message(squared_error):
    return error_message_and_field(max(range(len(squared_error)), key=lambda x:squared_error[x]))[0]

def error_message_and_field(index):
    return [("Check maturity date","maturityDate"),
            ("Check quantity","quantity"),
             ("Check underlying price","underlyingPrice"),
              ("Check Strike Price","strikePrice"),
               ("Stock volatility inconsistency, check underlying price","underlyingPrice"),
                ("Check underlying price change in last day","underlyingPrice"),
                 ("Check proximity to recent max/min price","underlyingPrice"),
                  ("Check proximity to recent max/min price","underlyingPrice")
            ][index]



def estimate_error_ratio(errorValue):
    values = {0.95: 0.03775,
              0.8: 0.02520,
              0.6: 0.01780}
    if errorValue > values[0.6] and errorValue < values[0.8]:
        return 0.6 + (0.2 * ((errorValue - values[0.6]) / (values[0.8] - values[0.6])))
    if errorValue > values[0.8] and errorValue < values[0.95]:
        return 0.8 + (0.15 * ((errorValue - values[0.8]) / (values[0.95] - values[0.8])))
    if errorValue > values[0.95]:
        return 1
    if errorValue < values[0.6]:
        return ((errorValue) / values[0.6]) * 0.6

def str_to_date(date_str):
    """
    Parses a date string that is either in format DD/MM/YYYY or DD/MM/YY. Any
    two digit years YY are taken to be after the millenium i.e. 20YY.
    """
    try:
        return datetime.strptime(date_str, date_format_parse).date()
    except ValueError:
        split_date = date_str.split("/")
        if len(split_date) == 3:
            date_str = '/'.join(split_date[:2] + ["20" + split_date[2]])
            try:
                return datetime.strptime(date_str, date_format_parse).date()
            except ValueError:
                pass
    raise ValueError("Date given not in format DD/MM/YYYY or DD/MM/YY")

def str_to_datetime(datetime_str):
    """
    Parses a date string that is either in format HH:MM:SS DD/MM/YYYY or
    HH:mm:ss DD/MM/YY. Any two digit years YY are taken to be after the
    millenium i.e. 20YY.
    """
    global DATETIME_REGEX # pylint: disable=global-statement
    matcher = DATETIME_REGEX.match(datetime_str)
    print(datetime_str)
    if not matcher:
        raise ValueError("datetime not given in format 'HH:mm:ss DD/MM/YY' or"
                         +"'HH:mm DD/MM/YY'. Year can be either 2 or 4 digits")
    return datetime(
        int("20" + matcher["year2"] if matcher["year2"] else matcher["year4"]),
        int(matcher["month"]),
        int(matcher["day"]),
        int(matcher["hours"]),
        int(matcher["minutes"]),
        int(matcher["seconds"]) if matcher["seconds"] else 0,
        0,
        pytz.timezone(TIME_ZONE)
    )

def ai_magic(data):
    error_threshold = 0.8

    # Split date for dd/mm/yyy
    if 'tradeID' in data:
        d = DerivativeTrade.objects.get(trade_id=data['tradeID']).date_of_trade
    elif isinstance(data["date"], str):
        d = datetime.strptime(data["date"], date_format_parse).date()
    else:
        d = timezone.now().date()
    data['date'] = d
    data['maturityDate'] = str_to_date(data["maturityDate"])

    isStock = (data['product'] == 'Stocks')
    key = data['sellingParty'] if isStock else data['product']
    adjustedStrikePrice = convert_currency(d, data['strikePrice'],data['notionalCurrency'],'USD')
    adjustedUnderlyingPrice = convert_currency(d, data['underlyingPrice'],'USD',data['underlyingCurrency'])
    normalizedData = normalize_trade(data['quantity'], key, d, data["maturityDate"], adjustedStrikePrice,
                                     adjustedUnderlyingPrice, isStock)
    if normalizedData is not False:
        with t_session.graph.as_default():
            k.backend.set_session(t_session)
            predict = autoencoder.predict(np.array([normalizedData]))[0]
        squared_error = squared_errors(predict, normalizedData)
        mse = mean_squared_error(predict, normalizedData)
        error_ratio = estimate_error_ratio(mse)
        error_msg = mse_error_message(squared_error)
        possible_causes = list(mse_error_causes(squared_error, error_ratio))
        if len(possible_causes) >= 3 and mse > 3:
            key_mse = []
            for key in (Company.objects.all() if isStock else Product.objects.all()):
                key = key.name
                normalizedData = normalize_trade(data['quantity'], key, d, data["maturityDate"], adjustedStrikePrice,
                             adjustedUnderlyingPrice, isStock)
                with t_session.graph.as_default():
                    k.backend.set_session(t_session)
                    predict = autoencoder.predict(np.array([normalizedData]))[0]
                new_mse = mean_squared_error(predict, normalizedData)
                if new_mse < 0.0252:
                    mutual_seller = True
                    try:

                        Product.objects.get(name=key,seller_company=Company.objects.get(name=data['sellingParty']))
                    except Product.DoesNotExist:
                        mutual_seller = False
                    key_mse.append((key, new_mse, 0 if mutual_seller else 1))
            if key_mse:
                likely = sorted(key_mse, key=lambda x: (x[2],x[1]))[:3]
                probability = estimate_error_ratio(likely[0][1])
                return {
                    'success': True,
                    'possibleCauses': ['sellingParty' if isStock else 'product'],
                    'probability': probability,
                    'correction': [l[0] for l in likely],
                    'errorThreshold': bool(probability > error_threshold),
                    'errorMessage':'All fields erroneous, correction necessary'
                }
        return {'success': True,
                'possibleCauses':possible_causes,
                'probability': error_ratio,
                'errorMessage': error_msg,
                'errorThreshold': bool(error_ratio > error_threshold)
                }
    return {'success': False, 'errorMessage': 'Not enough historic data', 'probability': 0}

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
    if 'fieldType' not in data:
        data['fieldType'] = None
    # possibly a performance bottleneck
    result["names"], autocorrect = closest_matches(data["name"], [c.name for c in Company.objects.all()],commonCorrectionField=data["fieldType"])

    # Blah blah correction is good
    result["autoCorrect"] = autocorrect  # Automatically change to top value
    return result


def validate_product(data):
    """ Validate single product. Expected data: product, buyingParty, sellingParty"""
                
    result = {"success": False, "sellingParty": data["sellingParty"], "product": True}

    # Shape of request is as expected (all necessary data is given)
    not_specified = {"product", "sellingParty", "buyingParty"}.difference(data)
    if not_specified:
        result["error"] = f"Values not specified: {', '.join(not_specified)}"
        return result

    # Validate buyer existence
    if not get_company(data["buyingParty"]):
        result["error"] = "Buying company does not exist"
        result["buyingParty"] = False

    # Get closest distance matches 
    result["products"], _ = closest_matches(
        data["product"], [p.name for p in Product.objects.all()], commonCorrectionField='product')

    # Validate product existence
    prod = get_product(data["product"])
    if not prod:
        result["error"] = "Product does not exist"
        result["product"] = False
        return result

    # Validate seller existence
    seller = get_company(data["sellingParty"])
    if not seller:
        result["error"] = "Selling company does not exist"
        result["sellingParty"] = prod.seller_company.name
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
    result["sellingParty"] = data["sellingParty"]
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
        if int(data["quantity"]) <= 0:
            result["error"] = "Quantity must be positive"
            return result
    except ValueError:
        result["error"] = "Quantity given must be an integer"
        return result

    # Validate prices
    try:
        if Decimal(data["underlyingPrice"]) <= 0:
            result["error"] = "Underlying price must be positive"
            return result
    except InvalidOperation:
        result["error"] = "Underlying price must be a decimal number"
        return result
    try:
        if Decimal(data["strikePrice"]) <= 0:
            result["error"] = "Strike price must be positive"
            return result
    except InvalidOperation:
        result["error"] = "Strike price must be a decimal number"
        return result

    product_validation_result = validate_product(data)
    if not product_validation_result["success"]:
        return product_validation_result

    result["probabilityErroneous"] = ai_magic(data)
    result["success"] = True
    return result


def correction(data):
    try:
        corr = Correction.objects.get(old_val=data['oldValue'], new_val=data['newValue'], field=data['field'])
        corr.times_corrected += 1
        corr.save()
    except Correction.DoesNotExist:
        Correction.objects.create(old_val=data['oldValue'], new_val=data['newValue'], field=data['field'],
                                  times_corrected=1)
    return {'success': 'true'}

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
        test_date = str_to_date(data["date"])
    except ValueError:
        result["error"] = "Invalid date string given. Expected format DD/MM/YYYY"
        return result

    # Validate date.
    if test_date < today:
        result["error"] = f"Date cannot be in the past. Server date is {today.strftime('%d/%m/%Y')}"
        return result

    result["success"] = True
    return result

@csrf_exempt
def currencies(_, date_str=None):
    """
    Returns currencies for a specific date. If no date is specified the current
    server date is used. Date str must be in DD/MM/YYYY format.
    """
    request_date = str_to_date(date_str) if date_str else timezone.now().date()
    return JsonResponse({
        "currencies": get_currencies(request_date)
    })
                
### Additional stuff below ###

def company(_, company_name):
    """ View of a single company at path 'company/<company_name>/'' """
    comp = get_company(company_name)
    suggestions, _ = closest_matches(
            company_name, [c.name for c in Company.objects.all()], commonCorrectionField='companyName'
    )
    result = {
        "success": comp is not None,
        "suggestions": suggestions
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
    result["suggestions"], _ = closest_matches(product_name, [p.name for p in Product.objects.all()],commonCorrectionField='product')
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
        result["product_suggestions"], _ = closest_matches(
            product_name, [p.name for p in comp.product_set.all()], commonCorrectionField='sellingParty'
        )
    return JsonResponse(result)
