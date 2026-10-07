"""
Professional email utility functions for Gammers Adda
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import threading


def send_booking_confirmation_email(booking, payment=None):
    """
    Send professional HTML booking confirmation email to owner
    
    Args:
        booking: Booking instance
        payment: Payment instance (optional)
    """
    recipient = getattr(settings, 'OWNER_NOTIFICATION_EMAIL', 'Sammarvalkar343@gmail.com')
    
    # Determine payment status
    payment_status = 'PENDING'
    payment_badge_class = 'badge-warning'
    if payment:
        payment_status = payment.get_status_display()
        if payment.status == 'SUCCESS':
            payment_badge_class = 'badge-success'
        elif payment.status == 'FAILED':
            payment_badge_class = 'badge-warning'
    
    # Get offer details if any
    offer_applied = booking.discount_amount > 0
    offer_name = ''
    offer_discount = ''
    offer_description = ''
    
    if offer_applied and hasattr(booking, 'applied_offer') and booking.applied_offer:
        offer = booking.applied_offer
        offer_name = offer.title
        if offer.offer_type == 'PERCENT':
            offer_discount = f'{offer.discount_value}% OFF'
        else:
            offer_discount = f'₹{offer.discount_value} OFF'
        offer_description = offer.description
    
    # Get screen/station number
    screen_number = 'N/A'
    if booking.seats.exists():
        seats = booking.seats.all()
        screen_number = ', '.join([seat.seat.code for seat in seats])
    
    # Prepare context
    context = {
        'booking': booking,
        'customer_name': booking.customer_name,
        'customer_email': booking.customer_email,
        'customer_phone': booking.customer_phone,
        'screen_number': screen_number,
        'zone_name': booking.zone.name if booking.zone else 'N/A',
        'booking_date': booking.booking_date.strftime('%d %b %Y'),
        'start_time': booking.start_time.strftime('%I:%M %p'),
        'total_hours': booking.duration_hours,
        'end_time': booking.end_time.strftime('%I:%M %p'),
        'payment_status': payment_status,
        'payment_badge_class': payment_badge_class,
        'base_amount': f'{booking.base_amount:.2f}',
        'addons_amount': f'{booking.addons_amount:.2f}',
        'discount_amount': f'{booking.discount_amount:.2f}',
        'tax_amount': f'{booking.tax_amount:.2f}',
        'total_amount': f'{booking.total_amount:.2f}',
        'offer_applied': offer_applied,
        'offer_name': offer_name,
        'offer_discount': offer_discount,
        'offer_description': offer_description,
        'notification_time': timezone.now().strftime('%d %b %Y, %I:%M %p IST'),
    }
    
    # Render HTML email
    html_content = render_to_string('emails/booking_confirmation.html', context)
    
    # Plain text fallback
    text_content = f"""
╔════════════════════════════════════════════╗
   GAMER'S ADDA — NEW BOOKING CONFIRMED
╚════════════════════════════════════════════╝

BOOKING REFERENCE
  Reference   : #{booking.booking_reference}
  Status      : {booking.get_status_display()}

CUSTOMER INFORMATION
  Name        : {booking.customer_name}
  Email       : {booking.customer_email}
  Phone       : {booking.customer_phone}

SESSION DETAILS
  Screen      : {screen_number}
  Zone        : {booking.zone.name if booking.zone else 'N/A'}
  Date        : {booking.booking_date.strftime('%d %b %Y')}
  Start Time  : {booking.start_time.strftime('%I:%M %p')}
  Duration    : {booking.duration_hours} hour(s)
  End Time    : {booking.end_time.strftime('%I:%M %p')}

PAYMENT INFORMATION
  Payment Status : {payment_status}
  Base Amount    : ₹{booking.base_amount}
  Add-ons        : ₹{booking.addons_amount}
  Discount       : -₹{booking.discount_amount}
  GST (18%)      : ₹{booking.tax_amount}
  TOTAL AMOUNT   : ₹{booking.total_amount}

{'OFFER APPLIED: ' + offer_name + ' - ' + offer_discount if offer_applied else ''}

Notification Time: {timezone.now().strftime('%d %b %Y, %I:%M %p IST')}

Contact: +91 83559 23184
Email: Sammarvalkar343@gmail.com
""".strip()
    
    # Create email
    subject = f"🎮 New Booking #{booking.booking_reference} — {booking.customer_name}"
    
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient]
    )
    msg.attach_alternative(html_content, "text/html")
    
    # Send in thread
    def send():
        try:
            msg.send(fail_silently=True)
        except Exception:
            pass
    
    t = threading.Thread(target=send, daemon=True)
    t.start()


def send_session_start_notification(booking):
    """
    Send notification when gaming session starts
    
    Args:
        booking: Booking instance
    """
    recipient = getattr(settings, 'OWNER_NOTIFICATION_EMAIL', 'Sammarvalkar343@gmail.com')
    
    # Get screen/station number
    screen_number = 'N/A'
    if booking.seats.exists():
        seats = booking.seats.all()
        screen_number = ', '.join([seat.seat.code for seat in seats])
    
    # Get offer details if any
    offer_info = ''
    if booking.discount_amount > 0 and hasattr(booking, 'applied_offer') and booking.applied_offer:
        offer = booking.applied_offer
        if offer.offer_type == 'PERCENT':
            offer_discount = f'{offer.discount_value}% OFF'
        else:
            offer_discount = f'₹{offer.discount_value} OFF'
        offer_info = f"\n  Applied Offer : {offer.title} ({offer_discount})"
    
    subject = f"🕹️ Session Started — {booking.customer_name} @ {screen_number}"
    
    body = f"""
╔════════════════════════════════════════════╗
   GAMER'S ADDA — GAMING SESSION STARTED
╚════════════════════════════════════════════╝

🎮 TIMER ACTIVATED

CUSTOMER INFORMATION
  Name        : {booking.customer_name}
  Phone       : {booking.customer_phone}

SESSION DETAILS
  Screen      : {screen_number}
  Booking Ref : #{booking.booking_reference}
  Start Time  : {booking.start_time.strftime('%I:%M %p')}
  Duration    : {booking.duration_hours} hour(s)
  End Time    : {booking.end_time.strftime('%I:%M %p')}{offer_info}

⏱️ The customer's gaming timer has officially started!

Notification Time: {timezone.now().strftime('%d %b %Y, %I:%M %p IST')}

Contact: +91 83559 23184
Email: Sammarvalkar343@gmail.com
""".strip()
    
    def send():
        try:
            from django.core.mail import send_mail
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=True,
            )
        except Exception:
            pass
    
    t = threading.Thread(target=send, daemon=True)
    t.start()
