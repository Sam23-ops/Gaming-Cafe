#!/usr/bin/env python
"""Quick script to update phone numbers in database"""
import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gammers_adda.settings')
django.setup()

from apps.core.models import SystemSetting

# Update contact phone
try:
    setting = SystemSetting.objects.get(key='contact_phone')
    setting.value = '+91 88504 11925 / +91 98707 33633'
    setting.save()
    print(f"✅ Updated contact_phone: {setting.value}")
except SystemSetting.DoesNotExist:
    SystemSetting.objects.create(
        key='contact_phone',
        value='+91 88504 11925 / +91 98707 33633',
        description='Phone',
        is_public=True
    )
    print("✅ Created contact_phone setting")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ Phone numbers updated successfully!")
print("Primary: +91 88504 11925")
print("Secondary: +91 98707 33633")
