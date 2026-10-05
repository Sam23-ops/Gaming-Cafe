import uuid
from django.db import models
from django.conf import settings
from apps.bookings.models import Booking

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('INITIATED', 'Payment Initiated'),
        ('PENDING', 'Payment Pending Gateway Confirmation'),
        ('SUCCESS', 'Payment Successful'),
        ('FAILED', 'Payment Failed'),
        ('REFUNDED', 'Payment Refunded'),
    ]

    PAYMENT_METHODS = [
        ('UPI', 'UPI (Google Pay, PhonePe, Paytm)'),
        ('CARD', 'Credit / Debit Card'),
        ('NETBANKING', 'Net Banking'),
        ('CASH', 'Cash on Counter (Walk-in)'),
        ('WALLET', 'Gammers Loyalty Wallet'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    payment_reference = models.CharField(max_length=50, unique=True)
    gateway_order_id = models.CharField(max_length=100, blank=True)
    gateway_payment_id = models.CharField(max_length=100, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, default='UPI')
    status = models.CharField(max_length=30, choices=PAYMENT_STATUS, default='INITIATED')
    
    failure_reason = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.payment_reference:
            self.payment_reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_reference} - ₹{self.amount} [{self.get_status_display()}]"


class Transaction(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, unique=True)
    transaction_type = models.CharField(max_length=30, default='PAYMENT') # PAYMENT, REFUND
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30)
    gateway_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Txn #{self.transaction_id} ({self.status}) - ₹{self.amount}"


class Refund(models.Model):
    REFUND_STATUS = [
        ('PENDING', 'Refund Processing'),
        ('COMPLETED', 'Refund Completed'),
        ('REJECTED', 'Refund Rejected'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    refund_reference = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=30, choices=REFUND_STATUS, default='PENDING')
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.refund_reference:
            self.refund_reference = f"REF-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.refund_reference} - ₹{self.amount} ({self.get_status_display()})"


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='invoice')
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='invoice')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    gstin = models.CharField(max_length=25, default='29AABCG1234F1Z8')
    issued_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{self.booking.booking_reference}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_number} - ₹{self.total_amount}"
