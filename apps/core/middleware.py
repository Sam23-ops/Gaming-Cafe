"""
Site visit notification middleware.
Sends email notification on every unique page visit.
"""
import threading
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'Unknown')


def _send_visit_notification(path, ip, user_agent, user):
    """Send email notification when someone visits the site."""
    recipient = getattr(settings, 'LOGIN_NOTIFICATION_EMAIL', 'sumitmaheshmarvalkar343@gmail.com')
    timestamp = timezone.now().strftime('%d %b %Y %I:%M:%S %p IST')
    
    user_info = 'Anonymous Visitor'
    if user and user.is_authenticated:
        gamer_tag = getattr(user, 'gamer_tag', '') or user.username
        user_info = f"{gamer_tag} ({user.email})"
    
    subject = f"🌐 Site Visit — {path}"
    body = f"""
╔════════════════════════════════════════════╗
   GAMER'S ADDA — SITE VISIT ALERT
╚════════════════════════════════════════════╝

PAGE VISITED
  URL Path    : {path}
  
VISITOR INFO
  User        : {user_info}
  IP Address  : {ip}
  Device      : {user_agent[:150]}

TIMESTAMP
  {timestamp}

Contact: +91 8355923184
Email: sumitmaheshmarvalkar343@gmail.com
""".strip()

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=True,
        )
    except Exception:
        pass


class SiteVisitNotificationMiddleware:
    """
    Middleware to send email notification on every page visit.
    Only tracks HTML pages, not static files or media.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only track actual page visits (not static/media)
        if not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            ip_address = _get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            user = request.user
            
            # Send notification in background thread
            t = threading.Thread(
                target=_send_visit_notification,
                args=(request.path, ip_address, user_agent, user),
                daemon=True
            )
            t.start()
        
        response = self.get_response(request)
        return response
