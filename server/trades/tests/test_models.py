from datetime import datetime
from django.test import TestCase
from django.utils import timezone
from trades.models import (Company, CurrencyValue, DerivativeTrade,
                           TradeProduct, generate_trade_id, generate_company_id)

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
            notional_currency=self.cv1.currency,
            underlying_currency=self.cv2.currency,
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
