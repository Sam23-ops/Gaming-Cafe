from django.urls import path
from . import views

app_name = 'pricing'

urlpatterns = [
    path('packages/', views.packages_view, name='packages'),
    path('offers/', views.offers_view, name='offers'),
    path('api/calculate/', views.api_calculate_price, name='api_calculate'),
]
