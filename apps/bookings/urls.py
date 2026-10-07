from django.urls import path
from . import views, api_views

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
    
    # ── Customer Session Timer ────────────────────────────────────────────────
    path('session/<str:booking_reference>/', views.my_session_timer_view, name='my_session_timer'),
    
    # ── Real-Time Session Timer APIs ──────────────────────────────────────────
    path('api/session/timer/<str:booking_reference>/', api_views.session_timer_data, name='api_session_timer'),
    path('api/sessions/active/', api_views.active_sessions_list, name='api_active_sessions'),
    path('api/session/extend/<str:booking_reference>/', api_views.extend_session, name='api_extend_session'),
    path('api/session/terminate/<str:booking_reference>/', api_views.terminate_session, name='api_terminate_session'),
    path('api/session/pause/<str:booking_reference>/', api_views.pause_session, name='api_pause_session'),
    path('api/session/resume/<str:booking_reference>/', api_views.resume_session, name='api_resume_session'),
]
