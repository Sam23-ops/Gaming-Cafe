"""
apps/payments/views.py
Supports both real Razorpay gateway and a dev-mode simulator fallback.
"""
import uuid
import hmac
import hashlib
import json
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False

from .models import Payment, Transaction, Refund, Invoice
from apps.bookings.models import Booking
from apps.bookings.services import BookingStateMachine
from apps.accounts.decorators import permission_required
from apps.core.utils import log_action
from .utils import generate_upi_qr_code, format_upi_id, format_phone_number


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_razorpay_client():
    if not RAZORPAY_AVAILABLE:
        return None
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


def _confirm_payment(booking, payment_method, gateway_payment_id='', gateway_order_id=''):
    """Shared helper: create Payment + Invoice + confirm booking state."""
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount':             booking.total_amount,
            'payment_method':     payment_method,
            'status':             'SUCCESS',
            'gateway_payment_id': gateway_payment_id,
            'gateway_order_id':   gateway_order_id,
            'paid_at':            timezone.now(),
        }
    )
    if not created:
        payment.status             = 'SUCCESS'
        payment.payment_method     = payment_method
        payment.gateway_payment_id = gateway_payment_id
        payment.gateway_order_id   = gateway_order_id
        payment.paid_at            = timezone.now()
        payment.save()

    Transaction.objects.create(
        payment=payment,
        transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
        transaction_type='PAYMENT',
        amount=payment.amount,
        status='SUCCESS',
        gateway_response={
            'method':   payment_method,
            'status':   'captured',
            'order_id': gateway_order_id,
            'pay_id':   gateway_payment_id,
        }
    )

    Invoice.objects.get_or_create(
        booking=booking,
        defaults={
            'payment':          payment,
            'subtotal':         booking.base_amount + booking.addons_amount,
            'discount_amount':  booking.discount_amount,
            'tax_amount':       booking.tax_amount,
            'total_amount':     booking.total_amount,
        }
    )
    BookingStateMachine.confirm_booking(booking, payment)
    return payment


# ── Views ─────────────────────────────────────────────────────────────────────

def checkout_view(request, booking_reference):
    """Checkout page — shows Razorpay Pay button + dev simulator fallback."""
    booking = get_object_or_404(
        Booking.objects.prefetch_related('seats__seat', 'items__addon'),
        booking_reference=booking_reference
    )

    if booking.status == 'CONFIRMED':
        return redirect('bookings:confirmation',
                        booking_reference=booking.booking_reference)

    # Determine whether real Razorpay keys are configured
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    real_gateway = (
        RAZORPAY_AVAILABLE
        and key_id
        and key_id != 'rzp_test_YOUR_KEY_ID'
        and not key_id.startswith('rzp_test_YOUR')
    )

    # Generate UPI QR code and payment details with better error handling
    upi_qr_code = None
    try:
        upi_qr_code = generate_upi_qr_code(
            amount=float(booking.total_amount),
            booking_reference=booking.booking_reference
        )
    except Exception as e:
        print(f"QR Code generation error: {e}")
        # QR code is optional, continue without it
    
    upi_id = format_upi_id()
    upi_phone = format_phone_number()
    business_name = getattr(settings, 'BUSINESS_NAME', 'Gammers Adda')

    return render(request, 'payments/checkout.html', {
        'booking':       booking,
        'razorpay_key':  key_id,
        'real_gateway':  real_gateway,
        'upi_qr_code':   upi_qr_code,
        'upi_id':        upi_id,
        'upi_phone':     upi_phone,
        'business_name': business_name,
    })


# ── Razorpay: Create Order ────────────────────────────────────────────────────

def razorpay_create_order(request, booking_reference):
    """
    POST → creates a Razorpay order and returns {order_id, amount, key}.
    Called via AJAX from the checkout page.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    booking = get_object_or_404(Booking, booking_reference=booking_reference)
    
    # Check if Razorpay is available and configured
    if not RAZORPAY_AVAILABLE:
        return JsonResponse({
            'error': 'Razorpay module not installed. Please install: pip install razorpay'
        }, status=503)
    
    client = _get_razorpay_client()
    if not client:
        return JsonResponse({
            'error': 'Razorpay not configured. Please check RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET'
        }, status=503)
    
    # Validate Razorpay keys
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    if not key_id or key_id == 'rzp_test_YOUR_KEY_ID':
        return JsonResponse({
            'error': 'Invalid Razorpay keys. Please configure valid API keys in environment variables.'
        }, status=503)

    # Amount in paise (₹1 = 100 paise)
    amount_paise = int(booking.total_amount * 100)

    try:
        order = client.order.create({
            'amount':   amount_paise,
            'currency': getattr(settings, 'RAZORPAY_CURRENCY', 'INR'),
            'receipt':  booking.booking_reference,
            'notes': {
                'booking_ref':   booking.booking_reference,
                'customer_name': booking.customer_name,
                'customer_email': booking.customer_email,
            }
        })
    except Exception as exc:
        return JsonResponse({
            'error': f'Razorpay API error: {str(exc)}',
            'details': 'Please check your Razorpay credentials or try UPI payment instead.'
        }, status=500)

    # Persist the gateway order id on Payment record
    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount':          booking.total_amount,
            'payment_method':  'UPI',
            'status':          'INITIATED',
            'gateway_order_id': order['id'],
        }
    )
    payment.gateway_order_id = order['id']
    payment.status = 'INITIATED'
    payment.save()

    return JsonResponse({
        'order_id': order['id'],
        'amount':   amount_paise,
        'currency': settings.RAZORPAY_CURRENCY,
        'key':      settings.RAZORPAY_KEY_ID,
        'name':     "Gamer's Adda",
        'description': f"Booking {booking.booking_reference}",
        'prefill': {
            'name':    booking.customer_name,
            'email':   booking.customer_email,
            'contact': booking.customer_phone,
        },
    })


# ── Razorpay: Verify Signature ────────────────────────────────────────────────

@csrf_exempt
def razorpay_verify(request):
    """
    POST → verifies Razorpay payment signature, confirms booking on success.
    Called by the JS handler after payment.success callback.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST.dict()

    booking_reference = data.get('booking_reference', '')
    razorpay_order_id   = data.get('razorpay_order_id', '')
    razorpay_payment_id = data.get('razorpay_payment_id', '')
    razorpay_signature  = data.get('razorpay_signature', '')

    booking = get_object_or_404(Booking, booking_reference=booking_reference)
    client  = _get_razorpay_client()

    if client:
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id':   razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature':  razorpay_signature,
            })
        except Exception:
            # Signature mismatch — payment tampered
            booking.status = 'PAYMENT_FAILED'
            booking.save(update_fields=['status'])
            return JsonResponse({'status': 'failed', 'message': 'Payment signature invalid.'}, status=400)

    # Signature valid → confirm booking
    _confirm_payment(
        booking,
        payment_method='UPI',
        gateway_payment_id=razorpay_payment_id,
        gateway_order_id=razorpay_order_id,
    )

    return JsonResponse({
        'status':        'success',
        'redirect_url':  f"/booking/confirmation/{booking_reference}/",
    })


# ── Dev Simulator (fallback when Razorpay keys are test placeholders) ─────────

@csrf_exempt
def process_payment_view(request, booking_reference):
    """Dev-mode payment simulator — SUCCESS / PENDING / FAILED outcomes."""
    booking = get_object_or_404(Booking, booking_reference=booking_reference)

    if request.method == 'POST':
        outcome        = request.POST.get('outcome', 'SUCCESS')
        payment_method = request.POST.get('payment_method', 'UPI')

        if outcome == 'SUCCESS':
            _confirm_payment(
                booking,
                payment_method=payment_method,
                gateway_payment_id=f"pay_DEV_{uuid.uuid4().hex[:10]}",
            )
            messages.success(
                request,
                f"🎉 Payment of ₹{booking.total_amount} confirmed! Booking locked in."
            )
            return redirect('bookings:confirmation',
                            booking_reference=booking.booking_reference)

        elif outcome == 'PENDING':
            payment, _ = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    'amount': booking.total_amount,
                    'payment_method': payment_method,
                    'status': 'PENDING',
                }
            )
            booking.status = 'PAYMENT_PENDING'
            booking.save(update_fields=['status'])
            return render(request, 'payments/payment_pending.html',
                          {'booking': booking, 'payment': payment})

        else:
            payment, _ = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    'amount': booking.total_amount,
                    'payment_method': payment_method,
                    'status': 'FAILED',
                    'failure_reason': 'Transaction declined — simulator failure.',
                }
            )
            booking.status = 'PAYMENT_FAILED'
            booking.save(update_fields=['status'])
            return render(request, 'payments/payment_failed.html',
                          {'booking': booking, 'payment': payment})

    return redirect('payments:checkout',
                    booking_reference=booking.booking_reference)


# ── Invoice ───────────────────────────────────────────────────────────────────

def invoice_view(request, booking_reference):
    """Receipt/invoice page — ONLY accessible if payment status is SUCCESS."""
    booking = get_object_or_404(
        Booking.objects.prefetch_related(
            'seats__seat', 'items__addon', 'invoice'
        ),
        booking_reference=booking_reference
    )
    
    # Block access if payment not successful
    try:
        payment = booking.payment
        if payment.status != 'SUCCESS':
            messages.error(request, '⚠️ Payment not completed yet. Please complete payment first.')
            return redirect('payments:checkout', booking_reference=booking.booking_reference)
    except Payment.DoesNotExist:
        messages.error(request, '⚠️ No payment found for this booking. Please complete payment.')
        return redirect('payments:checkout', booking_reference=booking.booking_reference)
    
    invoice = getattr(booking, 'invoice', None)
    if not invoice:
        try:
            payment = booking.payment
            if payment.status == 'SUCCESS':
                invoice = Invoice.objects.create(
                    booking=booking,
                    payment=payment,
                    subtotal=booking.base_amount + booking.addons_amount,
                    discount_amount=booking.discount_amount,
                    tax_amount=booking.tax_amount,
                    total_amount=booking.total_amount,
                )
        except Exception:
            pass

    return render(request, 'payments/invoice.html', {
        'booking': booking,
        'invoice': invoice,
    })


# ── Admin Refund ──────────────────────────────────────────────────────────────

@permission_required('payment.refund')
def admin_refund_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Administrative refund')
        amount = Decimal(request.POST.get('amount', str(payment.amount)))

        Refund.objects.create(
            payment=payment,
            amount=amount,
            reason=reason,
            status='COMPLETED',
            processed_by=request.user,
            processed_at=timezone.now(),
        )
        payment.status = 'REFUNDED'
        payment.save()
        payment.booking.status = 'REFUNDED'
        payment.booking.save()

        log_action(
            request.user, 'REFUND', 'Payment', payment.id,
            f"Refund ₹{amount} for {payment.booking.booking_reference}. Reason: {reason}"
        )
        messages.success(request, f"Refund of ₹{amount} processed successfully.")
        return redirect('dashboard:payments_list')

    return render(request, 'payments/admin_refund_modal.html', {'payment': payment})
