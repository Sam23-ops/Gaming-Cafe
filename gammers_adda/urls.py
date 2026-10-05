"""
Main URL Configuration for Gammers Adda
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('venue/', include('apps.venue.urls')),
    path('games/', include('apps.games.urls')),
    path('pricing/', include('apps.pricing.urls')),
    path('booking/', include('apps.bookings.urls')),
    path('payments/', include('apps.payments.urls')),
    path('community/', include('apps.engagement.urls')),
    path('staff/', include('apps.staff.urls')),
    path('admin-portal/', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.core.views.error_404_view'
handler500 = 'apps.core.views.error_500_view'
handler403 = 'apps.core.views.error_403_view'
