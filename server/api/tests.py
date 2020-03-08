from datetime import datetime, timedelta, date
from decimal import Decimal
import re

from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from trades.models import Company, CurrencyValue, DerivativeTrade, Product
from api.views import submit_trade, validate_maturity_date, validate_company

DATE_REGEX = "^(?P<day>[0-9]+)/(?P<month>[0-9]+)/(?P<year>[0-9]{2,2})$"

class TestSubmit(TestCase):
    def test_url_correct(self):
        self.assertEqual(reverse("api-submit"), "/api/submit/")
    def test_correct_function_chosen(self):
        self.assertEqual(resolve("/api/submit/").kwargs["func"], submit_trade)
    def test_trade_created_yyyy(self):
        test_date = timezone.now().date()
        CurrencyValue.objects.create(date=test_date, currency="USD", value="1")
        CurrencyValue.objects.create(date=test_date, currency="AAA", value="1")
        CurrencyValue.objects.create(date=test_date, currency="BBB", value="1")
        selling_company = Company.objects.create(name="X")
        Company.objects.create(name="Y")
        Product.objects.create(name="x", seller_company=selling_company)
        trade_data = {
            "buyingParty": "Y",
            "sellingParty": "X",
            "product": "x",
            "quantity": "10",
            "underlyingCurrency": "AAA",
            "underlyingPrice": "1",
            "maturityDate": "01/01/2020",
            "notionalCurrency": "BBB",
            "strikePrice": "1"
        }
        response = submit_trade(trade_data.copy()) # copy because passed data is modified
        self.assertTrue(response["success"])
        new_trade = response["trade"]
        self.assertTrue(DerivativeTrade.objects.all())
        self.assertEqual(new_trade["buyingParty"], trade_data["buyingParty"])
        self.assertEqual(new_trade["sellingParty"], trade_data["sellingParty"])
        self.assertEqual(new_trade["product"], trade_data["product"])
        self.assertEqual(new_trade["quantity"], int(trade_data["quantity"]))
        self.assertEqual(new_trade["underlyingCurrency"], trade_data["underlyingCurrency"])
        self.assertEqual(new_trade["underlyingPrice"], Decimal(trade_data["underlyingPrice"]))
        self.assertEqual(new_trade["maturityDate"], datetime.strptime(trade_data["maturityDate"], "%d/%m/%Y").date())
        self.assertEqual(new_trade["notionalCurrency"], trade_data["notionalCurrency"])
        self.assertEqual(new_trade["strikePrice"], Decimal(trade_data["strikePrice"]))
    def test_trade_created_yy(self):
        test_date = timezone.now().date()
        CurrencyValue.objects.create(date=test_date, currency="USD", value="1")
        CurrencyValue.objects.create(date=test_date, currency="AAA", value="1")
        CurrencyValue.objects.create(date=test_date, currency="BBB", value="1")
        selling_company = Company.objects.create(name="X")
        Company.objects.create(name="Y")
        Product.objects.create(name="x", seller_company=selling_company)
        trade_data = {
            "buyingParty": "Y",
            "sellingParty": "X",
            "product": "x",
            "quantity": "10",
            "underlyingCurrency": "AAA",
            "underlyingPrice": "1",
            "maturityDate": "01/01/20",
            "notionalCurrency": "BBB",
            "strikePrice": "1"
        }
        response = submit_trade(trade_data.copy()) # copy because passed data is modified
        self.assertTrue(response["success"])
        new_trade = response["trade"]
        matcher = re.match(DATE_REGEX, trade_data["maturityDate"])
        maturity_date = date(int("20" + matcher[3]), int(matcher[2]), int(matcher[1]))
        self.assertTrue(DerivativeTrade.objects.all())
        self.assertEqual(new_trade["buyingParty"], trade_data["buyingParty"])
        self.assertEqual(new_trade["sellingParty"], trade_data["sellingParty"])
        self.assertEqual(new_trade["product"], trade_data["product"])
        self.assertEqual(new_trade["quantity"], int(trade_data["quantity"]))
        self.assertEqual(new_trade["underlyingCurrency"], trade_data["underlyingCurrency"])
        self.assertEqual(new_trade["underlyingPrice"], Decimal(trade_data["underlyingPrice"]))
        self.assertEqual(new_trade["maturityDate"], maturity_date)
        self.assertEqual(new_trade["notionalCurrency"], trade_data["notionalCurrency"])
        self.assertEqual(new_trade["strikePrice"], Decimal(trade_data["strikePrice"]))

class TestMaturityDateValidation(TestCase):
    def setUp(self):
        self.format_str = "%d/%m/%Y"
    def test_url_correct(self):
        self.assertEqual(reverse("api-validate-maturitydate"), "/api/validate/maturitydate/")
    def test_correct_function_chosen(self):
        self.assertEqual(resolve("/api/validate/maturitydate/").kwargs["func"], validate_maturity_date)
    def test_past(self):
        """ Yesterday and any dates in the past should not be valid maturity dates """
        test_date = (timezone.now().date() - timedelta(days=1)).strftime(self.format_str)
        self.assertFalse(validate_maturity_date({"date":test_date})["success"])
        test_date = (timezone.now().date() - timedelta(days=10)).strftime(self.format_str)
        self.assertFalse(validate_maturity_date({"date":test_date})["success"])
        test_date = (timezone.now().date() - timedelta(days=100)).strftime(self.format_str)
        self.assertFalse(validate_maturity_date({"date":test_date})["success"])
        test_date = (timezone.now().date() - timedelta(days=1000)).strftime(self.format_str)
        self.assertFalse(validate_maturity_date({"date":test_date})["success"])
    def test_today(self):
        """ Today should be a valid maturity date """
        test_date = timezone.now().date().strftime(self.format_str)
        self.assertTrue(validate_maturity_date({"date":test_date})["success"])
    def test_future(self):
        """ Tomorrow and all dates in the future should be valid maturity date """
        test_date = (timezone.now().date() + timedelta(days=1)).strftime(self.format_str)
        self.assertTrue(validate_maturity_date({"date":test_date})["success"])
        test_date = (timezone.now().date() + timedelta(days=10)).strftime(self.format_str)
        self.assertTrue(validate_maturity_date({"date":test_date})["success"])
        test_date = (timezone.now().date() + timedelta(days=100)).strftime(self.format_str)
        self.assertTrue(validate_maturity_date({"date":test_date})["success"])
        test_date = (timezone.now().date() + timedelta(days=1000)).strftime(self.format_str)
        self.assertTrue(validate_maturity_date({"date":test_date})["success"])

class TestCompanyValidation(TestCase):
    def setUp(self):
        companies = ["A", "B", "ABC", "ZZZZZZ"]
        for company_name in companies:
            Company.objects.create(name=company_name)
    def test_url_correct(self):
        self.assertEqual(reverse("api-validate-company"), "/api/validate/company/")
    def test_correct_function_chosen(self):
        self.assertEqual(resolve("/api/validate/company/").kwargs["func"], validate_company)
    def test_existing(self):
        self.assertTrue(validate_company({"name":"A"})["success"])
        self.assertTrue(validate_company({"name":"B"})["success"])
        self.assertTrue(validate_company({"name":"ABC"})["success"])
        self.assertTrue(validate_company({"name":"ZZZZZZ"})["success"])
    def test_non_existing(self):
        self.assertFalse(validate_company({"name":"AA"})["success"])
        self.assertFalse(validate_company({"name":"C"})["success"])
        self.assertFalse(validate_company({"name":"ADD"})["success"])
        self.assertFalse(validate_company({"name":"ZZZZZZEEEEE"})["success"])
