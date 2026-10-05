from django.contrib import admin
from .models import Payment, Transaction, Refund, Invoice

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ['transaction_id', 'transaction_type', 'amount', 'status', 'created_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_reference', 'booking', 'amount', 'payment_method', 'status', 'paid_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['payment_reference', 'booking__booking_reference', 'gateway_payment_id']
    readonly_fields = ['payment_reference', 'created_at', 'updated_at']
    inlines = [TransactionInline]

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'payment', 'transaction_type', 'amount', 'status', 'created_at']
    list_filter = ['transaction_type', 'status']
    search_fields = ['transaction_id', 'payment__payment_reference']

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['refund_reference', 'payment', 'amount', 'status', 'processed_by', 'created_at']
    list_filter = ['status']
    search_fields = ['refund_reference', 'payment__payment_reference']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'booking', 'total_amount', 'gstin', 'issued_at']
    search_fields = ['invoice_number', 'booking__booking_reference']
    readonly_fields = ['invoice_number', 'issued_at']
