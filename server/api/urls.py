from django.urls import path

from . import views

urlpatterns = [
    path('', views.api_main, name='api_main'),
]
