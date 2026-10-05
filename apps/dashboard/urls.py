from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard_view, name='admin_dashboard'),
    path('bookings/', views.bookings_list_view, name='bookings_list'),
    path('seats/', views.seats_management_view, name='seat_management'),
    path('games/', views.games_manage_view, name='games_manage'),
    path('offers/', views.offers_manage_view, name='offers_manage'),
    path('reviews/', views.reviews_moderation_view, name='reviews_moderation'),
    path('payments/', views.payments_list_view, name='payments_list'),
    path('rbac/', views.rbac_matrix_view, name='rbac_matrix'),
    path('audit-logs/', views.audit_logs_view, name='audit_logs'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),
]
