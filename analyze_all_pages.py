#!/usr/bin/env python
"""
Comprehensive Page Analysis and Bug Detection
Checks all URLs, templates, views, and common issues
"""
import os
import sys
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gammers_adda.settings')
django.setup()

from django.urls import get_resolver, URLPattern, URLResolver
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def get_all_urls(resolver=None, prefix=''):
    """Recursively get all URL patterns"""
    if resolver is None:
        resolver = get_resolver()
    
    urls = []
    for pattern in resolver.url_patterns:
        if isinstance(pattern, URLResolver):
            urls.extend(get_all_urls(pattern, prefix + str(pattern.pattern)))
        elif isinstance(pattern, URLPattern):
            url = prefix + str(pattern.pattern)
            name = pattern.name
            urls.append((url, name))
    return urls

def analyze_pages():
    """Test all pages for common issues"""
    print("="*70)
    print("🔍 GAMMERS ADDA - COMPREHENSIVE PAGE ANALYSIS")
    print("="*70)
    print()
    
    client = Client()
    
    # Get all URLs
    urls = get_all_urls()
    print(f"📋 Found {len(urls)} URL patterns\n")
    
    # Test URLs that don't require parameters
    test_urls = [
        ('/', 'Home'),
        ('/games/', 'Games List'),
        ('/games/cod-warzone/', 'Game Detail (example)'),
        ('/bookings/wizard/', 'Booking Wizard'),
        ('/packages/', 'Packages'),
        ('/offers/', 'Offers'),
        ('/events/', 'Events'),
        ('/gallery/', 'Gallery'),
        ('/reviews/', 'Reviews'),
        ('/about/', 'About'),
        ('/faqs/', 'FAQs'),
        ('/rules/', 'Rules'),
        ('/contact/', 'Contact'),
        ('/accounts/login/', 'Login'),
        ('/accounts/register/', 'Register'),
        ('/admin/', 'Admin'),
    ]
    
    issues = []
    passed = []
    
    for url, name in test_urls:
        try:
            response = client.get(url, follow=True)
            
            if response.status_code == 200:
                passed.append((name, url, response.status_code))
                print(f"✅ {name:30} {url:40} [200 OK]")
                
                # Check for common template issues
                content = response.content.decode('utf-8', errors='ignore')
                
                # Check for template syntax errors
                if '{{' in content and '}}' not in content:
                    issues.append(f"⚠️  {name}: Possible unclosed template tag")
                
                # Check for broken static references
                if 'static/FIXME' in content or 'src=""' in content:
                    issues.append(f"⚠️  {name}: Broken static file reference")
                
                # Check for debug info leaking
                if 'Traceback' in content or 'Django Debug' in content:
                    issues.append(f"❌ {name}: Debug information exposed!")
                    
            elif response.status_code == 404:
                issues.append(f"❌ {name:30} {url:40} [404 NOT FOUND]")
                print(f"❌ {name:30} {url:40} [404 NOT FOUND]")
                
            elif response.status_code in [301, 302]:
                passed.append((name, url, f"Redirect to {response.url}"))
                print(f"↗️  {name:30} {url:40} [REDIRECT to {response.url}]")
                
            elif response.status_code == 500:
                issues.append(f"❌ {name:30} {url:40} [500 SERVER ERROR]")
                print(f"❌ {name:30} {url:40} [500 SERVER ERROR]")
                
            else:
                issues.append(f"⚠️  {name:30} {url:40} [{response.status_code}]")
                print(f"⚠️  {name:30} {url:40} [{response.status_code}]")
                
        except Exception as e:
            issues.append(f"💥 {name:30} {url:40} [ERROR: {str(e)[:50]}]")
            print(f"💥 {name:30} {url:40} [ERROR: {str(e)[:50]}]")
    
    print()
    print("="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"✅ Passed: {len(passed)}")
    print(f"❌ Issues: {len(issues)}")
    print()
    
    if issues:
        print("⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print()
    
    # Check for common configuration issues
    print("="*70)
    print("🔧 CONFIGURATION CHECK")
    print("="*70)
    
    from django.conf import settings
    
    config_issues = []
    
    if settings.DEBUG:
        config_issues.append("⚠️  DEBUG=True (should be False in production)")
    else:
        print("✅ DEBUG=False")
    
    if '*' in settings.ALLOWED_HOSTS:
        config_issues.append("⚠️  ALLOWED_HOSTS='*' (should specify domains in production)")
    else:
        print(f"✅ ALLOWED_HOSTS={settings.ALLOWED_HOSTS}")
    
    if 'insecure' in settings.SECRET_KEY.lower():
        config_issues.append("⚠️  SECRET_KEY appears insecure")
    else:
        print("✅ SECRET_KEY appears secure")
    
    # Check email configuration
    if settings.EMAIL_HOST_USER:
        print(f"✅ Email configured: {settings.EMAIL_HOST_USER}")
    else:
        config_issues.append("⚠️  Email not configured")
    
    # Check Razorpay
    if settings.RAZORPAY_KEY_ID:
        mode = "TEST" if "test" in settings.RAZORPAY_KEY_ID else "LIVE"
        print(f"✅ Razorpay configured: {settings.RAZORPAY_KEY_ID[:20]}... ({mode} mode)")
    else:
        config_issues.append("⚠️  Razorpay not configured")
    
    # Check phone numbers
    if hasattr(settings, 'BUSINESS_PHONE'):
        print(f"✅ Business Phone: {settings.BUSINESS_PHONE}")
    
    if hasattr(settings, 'BUSINESS_PHONE_2'):
        print(f"✅ Business Phone 2: {settings.BUSINESS_PHONE_2}")
    
    if config_issues:
        print("\n⚠️  CONFIGURATION ISSUES:")
        for issue in config_issues:
            print(f"   {issue}")
    
    print()
    print("="*70)
    print("🔍 TEMPLATE CHECK")
    print("="*70)
    
    # Check for template files
    templates_dir = Path('templates')
    if templates_dir.exists():
        template_files = list(templates_dir.rglob('*.html'))
        print(f"✅ Found {len(template_files)} template files")
        
        # Check for common template issues
        for template in template_files[:10]:  # Check first 10
            try:
                content = template.read_text(encoding='utf-8')
                if '{% load static %}' not in content and '{% static' in content:
                    print(f"⚠️  {template.name}: Uses static but doesn't load static tag")
            except:
                pass
    
    print()
    print("="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)
    print()
    
    if len(issues) == 0 and len(config_issues) == 0:
        print("🎉 NO MAJOR ISSUES FOUND! Your site is looking good!")
    else:
        print(f"⚠️  Found {len(issues) + len(config_issues)} issues to review")
    
    print()
    return len(issues) + len(config_issues)

if __name__ == '__main__':
    try:
        exit_code = analyze_pages()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
