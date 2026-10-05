from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<str:booking_reference>/',          views.checkout_view,          name='checkout'),
    path('process/<str:booking_reference>/',           views.process_payment_view,   name='process'),
    # ── Razorpay real gateway ─────────────────────────────────────────────────
    path('razorpay/create-order/<str:booking_reference>/', views.razorpay_create_order, name='razorpay_create_order'),
    path('razorpay/verify/',                           views.razorpay_verify,        name='razorpay_verify'),
    # ── Existing ─────────────────────────────────────────────────────────────
    path('invoice/<str:booking_reference>/',           views.invoice_view,           name='invoice'),
    path('refund/<int:payment_id>/',                   views.admin_refund_view,      name='admin_refund'),
]
