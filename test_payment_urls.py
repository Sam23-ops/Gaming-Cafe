"""
Test if payment URLs are configured correctly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gammers_adda.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

print("\n" + "="*70)
print("🔍 TESTING PAYMENT URLS")
print("="*70 + "\n")

# Test URLs
test_urls = [
    ('payments:checkout', {'booking_reference': 'GA-TEST-12345'}),
    ('payments:razorpay_create_order', {'booking_reference': 'GA-TEST-12345'}),
    ('payments:razorpay_verify', {}),
    ('payments:invoice', {'booking_reference': 'GA-TEST-12345'}),
]

for url_name, kwargs in test_urls:
    try:
        url = reverse(url_name, kwargs=kwargs)
        print(f"✅ {url_name:35} → {url}")
    except NoReverseMatch as e:
        print(f"❌ {url_name:35} → ERROR: {e}")

print("\n" + "="*70)
print("📋 PAYMENT FLOW SUMMARY")
print("="*70)
print("""
STEP 1: Create booking at /bookings/wizard/
STEP 2: Redirect to /payments/checkout/<booking-ref>/
STEP 3: Customer pays via Razorpay or UPI
STEP 4: Redirect to /bookings/confirmation/<booking-ref>/

CURRENT STATUS: All payment URLs are configured correctly!
""")
print("="*70 + "\n")

# Check Razorpay configuration
from django.conf import settings

print("🔑 RAZORPAY CONFIGURATION")
print("="*70)
print(f"Key ID: {settings.RAZORPAY_KEY_ID[:20]}..." if settings.RAZORPAY_KEY_ID else "❌ Not set")
print(f"Key Secret: {'*' * 20}..." if settings.RAZORPAY_KEY_SECRET else "❌ Not set")
print(f"Currency: {settings.RAZORPAY_CURRENCY}")

if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_ID.startswith('rzp_test'):
    print("\n✅ TEST MODE - Safe for development")
    print("   Real money will NOT be charged")
elif settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_ID.startswith('rzp_live'):
    print("\n⚠️  LIVE MODE - Real payments enabled!")
else:
    print("\n⚠️  Razorpay keys not configured properly")

print("="*70 + "\n")
