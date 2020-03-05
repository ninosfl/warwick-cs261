from django.test import TestCase
from trades.utils import convert_currency, get_currency_values
from trades.models import CurrencyValue
 
class TestCurrencyConversion(TestCase):
    """ Tests specifically for currency conversion from one currency to another """
    def setUp(self):
        self.test_date = "2020-01-01"
        CurrencyValue.objects.bulk_create([
            CurrencyValue(date=self.test_date, currency="USD", value="1"),
            CurrencyValue(date=self.test_date, currency="GBP", value="2"),
            CurrencyValue(date=self.test_date, currency="EUR", value="3"),
        ])
    def test_convert_currency_same(self):
        """ Conversion to the same currency should return the same value """
        self.assertEqual(convert_currency(self.test_date, 1, "USD", "USD"), 1)
        self.assertEqual(convert_currency(self.test_date, 1, "GBP", "GBP"), 1)
        self.assertEqual(convert_currency(self.test_date, 1, "EUR", "EUR"), 1)
        self.assertEqual(convert_currency(self.test_date, 2, "USD", "USD"), 2)
        self.assertEqual(convert_currency(self.test_date, 2, "GBP", "GBP"), 2)
        self.assertEqual(convert_currency(self.test_date, 2, "EUR", "EUR"), 2)
        self.assertEqual(convert_currency(self.test_date, 3, "USD", "USD"), 3)
        self.assertEqual(convert_currency(self.test_date, 3, "GBP", "GBP"), 3)
        self.assertEqual(convert_currency(self.test_date, 3, "EUR", "EUR"), 3)
        self.assertEqual(convert_currency(self.test_date, 1.5, "USD", "USD"), 1.5)
        self.assertEqual(convert_currency(self.test_date, 1.5, "GBP", "GBP"), 1.5)
        self.assertEqual(convert_currency(self.test_date, 1.5, "EUR", "EUR"), 1.5)
    def test_convert_currency_to_usd(self):
        """ Conversion to USD """
        self.assertEqual(convert_currency(self.test_date, 1, "GBP", "USD"), 2)
        self.assertEqual(convert_currency(self.test_date, 1, "EUR", "USD"), 3)
        self.assertEqual(convert_currency(self.test_date, 2, "GBP", "USD"), 4)
        self.assertEqual(convert_currency(self.test_date, 2, "EUR", "USD"), 6)
        self.assertEqual(convert_currency(self.test_date, 1.5, "GBP", "USD"), 3)
        self.assertEqual(convert_currency(self.test_date, 1.5, "EUR", "USD"), 4.5)
    def test_convert_currency_from_usd(self):
        """ Conversion from USD """
        self.assertEqual(convert_currency(self.test_date, 2, "USD", "GBP"), 1)
        self.assertEqual(convert_currency(self.test_date, 3, "USD", "EUR"), 1)
        self.assertEqual(convert_currency(self.test_date, 4, "USD", "GBP"), 2)
        self.assertEqual(convert_currency(self.test_date, 6, "USD", "EUR"), 2)
        self.assertEqual(convert_currency(self.test_date, 3, "USD", "GBP"), 1.5)
        self.assertEqual(convert_currency(self.test_date, 4.5, "USD", "EUR"), 1.5)

class TestUtils(TestCase):
    def setUp(self):
        self.test_date = "2020-01-01"
        CurrencyValue.objects.bulk_create([
            CurrencyValue(date=self.test_date, currency="HAF", value="0.5"),
            CurrencyValue(date=self.test_date, currency="USD", value="1"),
            CurrencyValue(date=self.test_date, currency="GBP", value="2"),
            CurrencyValue(date=self.test_date, currency="EUR", value="3"),
        ])
        self.other_date = "2020-02-02"
    def test_get_currency_values_retrieves_existing(self):
        """ CurrencyValue's that exist are retrieved """
        values = get_currency_values(self.test_date)
        self.assertEqual(values["HAF"], 0.5)
        self.assertEqual(values["USD"], 1)
        self.assertEqual(values["GBP"], 2)
        self.assertEqual(values["EUR"], 3)
    def test_get_currency_values_adds_values(self):
        self.assertFalse(CurrencyValue.objects.filter(date=self.other_date))
        get_currency_values(self.other_date)
        self.assertTrue(CurrencyValue.objects.filter(date=self.other_date))
