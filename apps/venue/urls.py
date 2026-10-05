from django.urls import path
from . import views

app_name = 'venue'

urlpatterns = [
    path('', views.zones_list_view, name='zones_list'),
    path('zone/<slug:slug>/', views.zone_detail_view, name='zone_detail'),
    path('api/seat-layout/', views.api_seat_layout, name='api_seat_layout'),
]
