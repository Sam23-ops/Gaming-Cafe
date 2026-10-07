from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('dashboard/', views.staff_dashboard_view, name='staff_dashboard'),
    path('live-arena/', views.live_arena_view, name='live_arena'),
    path('session-monitor/', views.session_monitor_view, name='session_monitor'),
    path('qr-scanner/', views.qr_scanner_view, name='qr_scanner'),
    path('api/validate-checkin/', views.api_validate_checkin, name='api_validate_checkin'),
    path('walkin/', views.walkin_booking_view, name='walkin_booking'),
    path('session/extend/<int:session_id>/', views.extend_session_view, name='extend_session'),
    path('session/end/<int:session_id>/', views.end_session_view, name='end_session'),
    path('seat/maintenance/<int:seat_id>/', views.toggle_seat_maintenance_view, name='toggle_maintenance'),
]
