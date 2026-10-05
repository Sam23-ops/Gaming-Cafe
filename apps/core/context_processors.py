from django.utils import timezone
from .models import SystemSetting, Announcement

def global_settings(request):
    """
    Expose global café settings and active announcements across all templates.
    """
    settings_dict = {
        'SITE_NAME': SystemSetting.get_val('site_name', "Gamer's Adda"),
        'TAGLINE': SystemSetting.get_val('tagline', 'PLAY • ENJOY • CONNECT'),
        'CONTACT_PHONE': SystemSetting.get_val('contact_phone', '+91 98765 43210'),
        'CONTACT_EMAIL': SystemSetting.get_val('contact_email', 'contact@gamersadda.com'),
        'VENUE_ADDRESS': SystemSetting.get_val('venue_address', 'Level 2, Cyber Hub, Tech District, Bangalore'),
        'OPENING_HOURS': SystemSetting.get_val('opening_hours', '10:00 AM - 02:00 AM (Mon - Sun)'),
        'CURRENCY_SYMBOL': SystemSetting.get_val('currency_symbol', '₹'),
        'TAX_PERCENTAGE': SystemSetting.get_val('tax_percentage', '18'),
    }

    # Fetch active announcements
    now = timezone.now()
    announcements = Announcement.objects.filter(is_active=True).filter(
        models_Q_helper(now)
    ).order_by('-created_at')[:2]

    return {
        'GLOBAL_SETTINGS': settings_dict,
        'ACTIVE_ANNOUNCEMENTS': announcements,
        'NOW': now,
    }

def models_Q_helper(now):
    from django.db.models import Q
    return (Q(starts_at__isnull=True) | Q(starts_at__lte=now)) & (Q(ends_at__isnull=True) | Q(ends_at__gte=now))
