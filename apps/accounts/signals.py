"""
Notification signals:
- Sends email to owner on user login
- Sends professional HTML email to owner on new booking confirmation
Completely fail-safe with threading and fail_silently=True.
"""
import threading
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from apps.core.email_utils import send_booking_confirmation_email


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'Unknown')


def _role_label(user):
    if user.is_superuser:
        return 'Super Admin (Root)'
    role = getattr(user, 'role', None)
    if role:
        return f"{role.name} ({role.code})"
    return 'Customer'


def _send_notification(user, request):
    recipient = getattr(settings, 'OWNER_NOTIFICATION_EMAIL', 'Sammarvalkar343@gmail.com')
    ip_address = _get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    timestamp = timezone.now().strftime('%d %b %Y %I:%M:%S %p IST')
    gamer_tag = getattr(user, 'gamer_tag', '') or user.username
    role_label = _role_label(user)

    subject = f"🎮 Login Alert — {gamer_tag} ({role_label}) | Gamer's Adda"
    body = f"""
╔════════════════════════════════════════════╗
   GAMER'S ADDA — LOGIN NOTIFICATION
╚════════════════════════════════════════════╝

IDENTITY
  Gamer Tag   : {gamer_tag}
  Username    : {user.username}
  Full Name   : {user.get_full_name() or '(not set)'}
  Email       : {user.email or '(not set)'}

ROLE & ACCESS
  Role        : {role_label}
  Staff       : {'Yes' if getattr(user, 'is_staff', False) else 'No'}
  Admin       : {'Yes' if user.is_superuser else 'No'}

SESSION DETAILS
  Timestamp   : {timestamp}
  Client IP   : {ip_address}
  Device      : {user_agent[:150]}

This is an automated security notification.
Contact: +91 8355923184
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


def _send_booking_notification(booking):
    """Send email notification when a new booking is confirmed."""
    recipient = getattr(settings, 'LOGIN_NOTIFICATION_EMAIL', 'sumitmaheshmarvalkar343@gmail.com')
    timestamp = timezone.now().strftime('%d %b %Y %I:%M:%S %p IST')
    
    subject = f"🎮 New Booking #{booking.booking_reference} — {booking.customer_name}"
    body = f"""
╔════════════════════════════════════════════╗
   GAMER'S ADDA — NEW BOOKING ALERT
╚════════════════════════════════════════════╝

BOOKING DETAILS
  Reference   : {booking.booking_reference}
  Status      : {booking.get_status_display()}
  Zone        : {booking.zone.name if booking.zone else 'N/A'}

CUSTOMER INFO
  Name        : {booking.customer_name}
  Email       : {booking.customer_email}
  Phone       : {booking.customer_phone}

SESSION DETAILS
  Date        : {booking.booking_date.strftime('%d %b %Y')}
  Start Time  : {booking.start_time.strftime('%I:%M %p')}
  Duration    : {booking.duration_hours} hour(s)
  End Time    : {booking.end_time.strftime('%I:%M %p')}

FINANCIAL
  Base Amount : ₹{booking.base_amount}
  Add-ons     : ₹{booking.addons_amount}
  Discount    : -₹{booking.discount_amount}
  Tax (GST)   : ₹{booking.tax_amount}
  Total       : ₹{booking.total_amount}

NOTIFICATION TIME
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


@receiver(user_logged_in)
def notify_admin_on_login(sender, request, user, **kwargs):
    """
    Notify owner on every login.
    DISABLED - Too many emails. Re-enable by uncommenting the threading line.
    """
    # t = threading.Thread(target=_send_notification, args=(user, request), daemon=True)
    # t.start()
    pass


@receiver(post_save, sender='bookings.Booking')
def notify_admin_on_booking(sender, instance, created, **kwargs):
    """
    Send professional HTML email when booking is CONFIRMED.
    Includes all details: customer, screen, times, payment, offers.
    """
    # Only send on CONFIRMED status
    if instance.status == 'CONFIRMED':
        # Get payment if exists
        payment = None
        try:
            from apps.payments.models import Payment
            payment = Payment.objects.filter(booking=instance).first()
        except Exception:
            pass
        
        # Send professional HTML email
        send_booking_confirmation_email(instance, payment)
