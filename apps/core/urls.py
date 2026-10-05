from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faqs/', views.faqs_view, name='faqs'),
    path('rules/', views.rules_view, name='rules'),
    path('api/live-availability/', views.live_availability_api, name='api_live_availability'),
]
