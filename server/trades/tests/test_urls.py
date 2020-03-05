from django.test import SimpleTestCase
from django.urls import resolve, reverse
from trades.views import home

class TestUrls(SimpleTestCase):
    def test_home_page_url(self):
        self.assertEquals(resolve(reverse("home-page")).func, home)
