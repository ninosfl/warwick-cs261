from decimal import Decimal
from pathlib import Path
import random
from .models import CurrencyValue

DATA_DIR = Path("../data")

SAMPLE_CURRENCY_VALUES_CACHE = None

def get_sample_currency_values():
    """
    Loads the default list of currencies and their values from 
    DATA_DIR/sample_currencies.csv. This file is only accessed once when the
    function is first called and subsequent executions return a cached version.
    """
    global SAMPLE_CURRENCY_VALUES_CACHE # pylint: disable=global-statement
    if SAMPLE_CURRENCY_VALUES_CACHE is None:
        with (DATA_DIR / "sample_currencies.csv").open("r") as file_obj:
            SAMPLE_CURRENCY_VALUES_CACHE = {
                c:Decimal(v) for c, v in (l.split(',') for l in file_obj)}
    return SAMPLE_CURRENCY_VALUES_CACHE

def remove_currencies_on_date(date):
    """ Delete all currency-values for a specific date. Only for testing purposes! """
    CurrencyValue.objects.filter(date=date).delete()

def get_currency_values(date):
    """
    Returns a mapping (dict) of currency-value. If no currencies exist for that
    day a list of sample currencies is loaded and then each value is transformed
    +/-10% and stored as that date's currency-values. This resulting mapping is
    then returned.
    """
    retrieved_currencies = CurrencyValue.objects.filter(date=date)
    if any(retrieved_currencies):
        return {cv.currency:cv.value for cv in retrieved_currencies}
    generated_values = {
        c: round(Decimal(random.uniform(0.9, 1.1)) * v, 6) # max 6 decimal places
        for c, v in get_sample_currency_values().items()
    }
    CurrencyValue.objects.bulk_create([
        CurrencyValue(currency=c, value=v, date=date)
        for c, v in generated_values.items()
    ])
    return generated_values

def get_currencies(date):
    """
    Returns all currencies that exist on a specified day, if none exist 
    currencies for that date they will be generated as per get_currency_values
    """
    return list(get_currency_values(date).keys())

def convert_currency(date, val, currency1, currency2):
    """ Convert val from currency1 to currency2 based on specified date's rate """
    currencyvals = get_currency_values(date)
    return val * currencyvals[currency1] / currencyvals[currency2]
