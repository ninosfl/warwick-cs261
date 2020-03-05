from datetime import datetime, date, timedelta
from decimal import Decimal, InvalidOperation
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from jellyfish import damerau_levenshtein_distance as edit_dist

from currency_converter import CurrencyConverter

from keras.models import load_model
import keras as k
from tensorflow.python.keras.backend import set_session
import tensorflow as tf
import numpy as np

from learning.models import Correction, TrainData, MetaData
from trades.models import (Company, Product, CurrencyValue, DerivativeTrade,
                           StockPrice, ProductPrice, TradeProduct, get_currencies)

graph = tf.get_default_graph()
t_session = tf.Session(graph=tf.Graph())


def load_model_from_path(path):
    global model
    with t_session.graph.as_default():
        k.backend.set_session(t_session)
        model = load_model(path)
        return model


c = CurrencyConverter(fallback_on_missing_rate=True)
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
    filtered_distances = {w: d for w, d in distances.items() if d <= 5}
    sorted_distances = sorted(filtered_distances, key=filtered_distances.get)
    return sorted_distances[:5]


def get_prices_traded(n_last, today_date, key, is_stock, adjusted_underlying=None):
    """ n_last: number of days to look back on, today_date: as datetime latest date """
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
    prices_list = prices.items()
    interpolated = []
    for day in range(n_last):
        day = today_date - timedelta(days=day)
        if day not in prices:
            days_after = [x for x in prices_list if x[0] >= today_date]
            days_before = [x for x in prices_list if x[0] <= today_date]
            if days_after and days_before:
                earliest_after = min(days_after, key=lambda x: x[0])
                lastest_before = max(days_before, key=lambda x: x[0])
                interpolated_price = ((day - lastest_before[0]).days / (earliest_after[0] - lastest_before[0]).days) * (
                        lastest_before[1] - earliest_after[1])
                interpolated.append((day, interpolated_price))
    for day, price in interpolated:
        prices[day] = price
    prices = [d[1] for d in sorted(prices.items(), key=lambda x: x[0]) if (today_date - d[0]).days < n_last][:-1]
    return prices


def normalize_trade(md, quantity, key, today_date, maturity_date, adjusted_strike, adjusted_underlying, is_stock):
    """ ML only """
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


def get_currency_value(x,
                       todayDate):  # Will get currency, will enter the currency in currencies table if not existent yet for future reference
    try:
        return CurrencyValue.objects.get(
            date=todayDate,
            currency=x).value
    except CurrencyValue.DoesNotExist:
        print(f"CurrencyDidNotExist {x}")
        try:
            newCurrency = CurrencyValue(date=todayDate, currency=x, value=c.convert(1, x, 'USD', date=todayDate))
            newCurrency.save()
        except:  # Doesn't have that recent data, need a new module or better yet, live currency conversion
            return 1
        return newCurrency.value


def record_learning_trade(trade):
    isStock = trade.product_type == 'S'
    todayDate = date(trade.date_of_trade.year, trade.date_of_trade.month, trade.date_of_trade.day)
    maturityDate = date(trade.maturity_date.year, trade.maturity_date.month, trade.maturity_date.day)
    key = trade.selling_party if isStock else trade.traded_product.product
    md = MetaData.objects.get_or_create(key=key, defaults={"runningAvgClosePrice": 0, "runningAvgTradePrice": 0,
                                                           "runningAvgQuantity": 0, "totalEntries": 0,
                                                           "totalQuantity": 0, "trades": 0})[0]
    adjusted_underlying = trade.underlying_price / get_currency_value(trade.underlying_currency, todayDate)
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
    cv2 = float(get_currency_value(trade.notional_currency, todayDate))
    adjustedStrike = float(trade.strike_price) / cv2
    normalizedData = normalize_trade(trade, md, key, todayDate, maturityDate, adjustedStrike, adjusted_underlying,
                                     isStock)
    if normalizedData:
        TrainData(val1=normalizedData[0], val2=normalizedData[1], val3=normalizedData[2], val4=normalizedData[3],
                  val5=normalizedData[4], val6=normalizedData[5], val7=normalizedData[6], val8=normalizedData[7]).save()
    return True


def currency_exists(currency_code):
    """ Checks for if the given currency exists in today's currencies """
    currencies_today = [c.currency for c in CurrencyValue.objects.get(date=timezone.now().date())]
    return currency_code in currencies_today


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
    # Convert values to their appropriate type
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


def error_message(index):
    return ["Check maturity date distance",
            "Check quantity",
            "Check underlying price",
            "Check Strike Price",
            "Stock volatility inconsistency, check underlying price",
            "Check underlying price change in last day",
            "Check proximity to recent max price",
            "Check proximity to recent minimum price"
            ][index]



def estimate_error_ratio(errorValue):
    values = {0.95: 0.037751311451393696,
              0.8: 0.02520727266310019,
              0.6: 0.01780338673080255}
    if errorValue > values[0.6] and errorValue < values[0.8]:
        return 0.6 + (0.2 * ((errorValue - values[0.6]) / (values[0.8] - values[0.6])))
    if errorValue > values[0.8] and errorValue < values[0.95]:
        return 0.8 + (0.15 * ((errorValue - values[0.8]) / (values[0.95] - values[0.8])))
    if errorValue > values[0.95]:
        return 1
    if errorValue < values[0.6]:
        return ((values[0.6] - errorValue) / values[0.6]) * 0.6


def ai_magic(data):
    d = [int(x) for x in data['date'].split('-')]
    d = date(d[0], d[1], d[2])
    maturityDate = [int(x) for x in data['maturityDate'].split('-')]
    maturityDate = date(maturityDate[0], maturityDate[1], maturityDate[2])
    data['date'] = d
    data['maturityDate'] = maturityDate
    isStock = (data['product'] == 'Stocks')
    key = data['sellingParty'] if isStock else data['product']
    adjustedStrikePrice = data['strikePrice'] / float(get_currency_value(data['notionalCurrency'], d))
    adjustedUnderlyingPrice = data['underlyingPrice'] / float(get_currency_value(data['underlyingCurrency'], d))
    md = MetaData.objects.get(key=key)
    normalizedData = normalize_trade(md, data['quantity'], key, d, maturityDate, adjustedStrikePrice,
                                     adjustedUnderlyingPrice, isStock)
    with t_session.graph.as_default():
        k.backend.set_session(t_session)
        predict = autoencoder.predict(np.array([normalizedData]))[0]
        error_msg = error_message(determine_error(predict, normalizedData))
        return {'success': True, 'possible_cause':error_msg,'probability': estimate_error_ratio(
            mean_squared_error(predict, normalizedData))}


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
        # return result

    # Get closest distance matches 
    result["products"] = closest_matches(
        data["product"], [p.name for p in Product.objects.all()])

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
    print(data)
    try:
        corr = Correction.objects.get(old_val=data['oldValue'], new_val=data['newValue'], field=data['field'])
        corr.times_corrected += 1
        corr.save()
    except Correction.DoesNotExist:
        Correction.objects.create(old_val=data['oldValue'], new_val=data['newValue'], field=data['field'],
                                  times_corrected=1)
    return {
        'success': 'true'
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
        test_date = datetime.strptime(data["date"], "%d/%m/%Y").date()
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
    if not date_str:
        request_date = timezone.now().date()
    else:
        request_date = datetime.strptime(date_str, date_format_parse).date()
    return JsonResponse({
        "currencies": get_currencies(request_date)
    })


### Additional stuff below ###

def company(_, company_name):
    """ View of a single company at path 'company/<company_name>/'' """
    comp = get_company(company_name)
    result = {
        "success": comp is not None,
        "suggestions": closest_matches(
            company_name, [c.name for c in Company.objects.all()], commonCorrectionField='companyName'
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
