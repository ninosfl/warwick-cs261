from datetime import datetime
from django.test import TestCase
from django.utils import timezone
from trades.models import (Company, CurrencyValue, DerivativeTrade,
                           TradeProduct, generate_trade_id, generate_company_id,
                           convert_currency, get_currency_values)


class TestModels(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Quality Shells Ltd")
        self.product = self.company.product_set.create(name="Blue Shells")
        self.tradedatetime = timezone.now()
        self.cv1 = CurrencyValue.objects.create(
            date=self.tradedatetime.date(), currency="GBP", value=3)
        self.cv2 = CurrencyValue.objects.create(
            date=self.tradedatetime.date(), currency="EUR", value=2)
        self.trade = DerivativeTrade.objects.create(
            date_of_trade=self.tradedatetime,
            product_type='P', 
            buying_party=self.company,
            selling_party=self.company,
            notional_currency=self.cv2.currency,
            underlying_currency=self.cv1.currency,
            underlying_price=20,
            quantity=2,
            maturity_date=datetime(2020, 1, 1),
            strike_price=21
            )
        TradeProduct.objects.create(trade=self.trade, product=self.product)
    def test_id_generating(self):
        company_id = generate_company_id()
        self.assertRaises(Company.DoesNotExist, Company.objects.get, id=company_id)
        trade_id = generate_trade_id()
        self.assertRaises(
            DerivativeTrade.DoesNotExist, DerivativeTrade.objects.get, trade_id=trade_id)
    def test_notional_amount_calc(self):
        # Initial conditions should result in a known value
        self.assertEquals(self.trade.notional_amount, 60)
        # doubling quantity should double notional amount
        self.trade.quantity = 4
        self.assertEquals(self.trade.notional_amount, 120)
        # doubling quantity should double notional amount
        self.trade.underlying_price = 40
        self.assertEquals(self.trade.notional_amount, 240)



 
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
