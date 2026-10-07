"""
Payment utility functions for Gammers Adda
"""
import qrcode
from io import BytesIO
import base64
from django.conf import settings


def generate_upi_qr_code(amount, booking_reference, upi_id=None, name=None):
    """
    Generate UPI QR code for payment
    
    Args:
        amount: Payment amount in INR
        booking_reference: Unique booking reference
        upi_id: UPI ID (defaults to settings.UPI_ID)
        name: Payee name (defaults to settings.UPI_NAME)
    
    Returns:
        Base64 encoded PNG image of QR code
    """
    upi_id = upi_id or getattr(settings, 'UPI_ID', '8355923184@paytm')
    name = name or getattr(settings, 'UPI_NAME', 'Gammers Adda')
    
    # UPI payment string format
    # Reference: https://www.npci.org.in/what-we-do/upi/upi-specifications
    upi_string = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR&tn=Booking-{booking_reference}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(upi_string)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"


def format_upi_id(upi_id=None):
    """Format UPI ID for display"""
    upi_id = upi_id or getattr(settings, 'UPI_ID', '8355923184@paytm')
    return upi_id


def format_phone_number(phone=None):
    """Format phone number for display"""
    phone = phone or getattr(settings, 'UPI_PHONE', '+918355923184')
    # Format: +91 8355923184 -> +91 83559 23184
    if phone.startswith('+91'):
        digits = phone[3:]
        if len(digits) == 10:
            return f"+91 {digits[:5]} {digits[5:]}"
    return phone
