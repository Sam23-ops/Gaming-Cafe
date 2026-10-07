"""
Django settings for Gammers Adda gaming-cafe platform.
"""

import os
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings from environment
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-gammers-adda-ultra-gaming-cafe-secret-key-2026')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Gammers Adda Core & Feature Apps
    'apps.core',
    'apps.accounts',
    'apps.venue',
    'apps.games',
    'apps.pricing',
    'apps.bookings',
    'apps.payments',
    'apps.engagement',
    'apps.staff',
    'apps.dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files for production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'apps.core.middleware.SiteVisitNotificationMiddleware',  # DISABLED - Too many emails
]

ROOT_URLCONF = 'gammers_adda.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.global_settings',
                'apps.accounts.context_processors.user_role_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'gammers_adda.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': BASE_DIR / os.environ.get('DATABASE_NAME', 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 4}
    },
]

AUTH_USER_MODEL = 'accounts.User'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise configuration for static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ── Production Security Settings ──────────────────────────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Seat Hold Expiration Window (in minutes)
SEAT_HOLD_DURATION_MINUTES = int(os.environ.get('SEAT_HOLD_DURATION_MINUTES', 10))

# Tax Rate (e.g., 18% GST)
DEFAULT_TAX_PERCENTAGE = float(os.environ.get('DEFAULT_TAX_PERCENTAGE', 18.0))

# ── SMTP Email Configuration ──────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', "Gammers Adda <noreply@gamersadda.com>")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Owner notification email (from .env)
OWNER_NOTIFICATION_EMAIL = os.environ.get('OWNER_NOTIFICATION_EMAIL', 'Sammarvalkar343@gmail.com')

# ── Razorpay Payment Gateway ──────────────────────────────────────────────────
# Set real keys via environment variables in production.
# Test keys are safe for development - they never charge real money.
RAZORPAY_KEY_ID     = os.environ.get('RAZORPAY_KEY_ID',     'rzp_test_YOUR_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'YOUR_KEY_SECRET')
RAZORPAY_CURRENCY   = 'INR'

# ── UPI Payment Configuration ─────────────────────────────────────────────────
UPI_ID = os.environ.get('UPI_ID', '7977729637@kotak')
UPI_NAME = os.environ.get('UPI_NAME', 'Gammers Adda')
UPI_PHONE = os.environ.get('UPI_PHONE', '+918850411925')

# ── Business Settings ─────────────────────────────────────────────────────────
BUSINESS_NAME = os.environ.get('BUSINESS_NAME', 'Gammers Adda')
BUSINESS_PHONE = os.environ.get('BUSINESS_PHONE', '+918850411925')
BUSINESS_PHONE_2 = os.environ.get('BUSINESS_PHONE_2', '+919870733633')
BUSINESS_EMAIL = os.environ.get('BUSINESS_EMAIL', 'info@gamersadda.com')
BUSINESS_ADDRESS = os.environ.get('BUSINESS_ADDRESS', 'Kopar Khairane, Navi Mumbai, Maharashtra')
