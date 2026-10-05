from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('wizard/', views.booking_wizard_view, name='wizard'),
    path('api/check-availability/', views.api_check_availability, name='api_check_availability'),
    path('confirmation/<str:booking_reference>/', views.booking_confirmation_view, name='confirmation'),
    path('ticket/<str:booking_reference>/', views.booking_ticket_view, name='ticket'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('detail/<str:booking_reference>/', views.booking_detail_view, name='booking_detail'),
    path('reschedule/<str:booking_reference>/', views.reschedule_booking_view, name='reschedule'),
    path('cancel/<str:booking_reference>/', views.cancel_booking_view, name='cancel'),
]
