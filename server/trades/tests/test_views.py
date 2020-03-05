from django.test import TestCase, Client
from django.urls import reverse

class TestTradeViews(TestCase):
    def setUp(self):
        self.client = Client()
    def test_home_page(self):
        response = self.client.get(reverse("home-page"))
        self.assertTemplateUsed(response, "trades/home.html")
