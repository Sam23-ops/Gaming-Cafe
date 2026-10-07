#!/usr/bin/env python
"""
Pre-Deployment Readiness Checker
Verifies that Gammers Adda is ready to be deployed to production.
"""
import os
import sys
import subprocess
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check(condition, message):
    """Print check result"""
    if condition:
        print(f"{GREEN}✅ {message}{RESET}")
        return True
    else:
        print(f"{RED}❌ {message}{RESET}")
        return False

def warn(message):
    """Print warning"""
    print(f"{YELLOW}⚠️  {message}{RESET}")

def info(message):
    """Print info"""
    print(f"{BLUE}ℹ️  {message}{RESET}")

def main():
    print("\n" + "="*70)
    print("🚀 GAMMERS ADDA - DEPLOYMENT READINESS CHECK")
    print("="*70 + "\n")
    
    checks_passed = 0
    total_checks = 0
    warnings = []
    
    # Check 1: Python version
    total_checks += 1
    python_version = sys.version_info
    if check(python_version >= (3, 8), f"Python version: {python_version.major}.{python_version.minor}"):
        checks_passed += 1
    
    # Check 2: Required files exist
    required_files = [
        'manage.py',
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        '.env',
        '.env.example',
        '.env.production',
        '.gitignore',
    ]
    
    for file in required_files:
        total_checks += 1
        if check(Path(file).exists(), f"File exists: {file}"):
            checks_passed += 1
    
    # Check 3: Required packages installed
    required_packages = [
        'django',
        'razorpay',
        'pillow',
        'qrcode',
        'python-dotenv',
        'gunicorn',
        'whitenoise',
    ]
    
    print("\nChecking Python packages...")
    for package in required_packages:
        total_checks += 1
        try:
            __import__(package.replace('-', '_'))
            if check(True, f"Package installed: {package}"):
                checks_passed += 1
        except ImportError:
            check(False, f"Package installed: {package}")
            warn(f"Install with: pip install {package}")
    
    # Check 4: Environment variables
    print("\nChecking environment variables...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_env_vars = [
        'SECRET_KEY',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'RAZORPAY_KEY_ID',
        'RAZORPAY_KEY_SECRET',
        'UPI_ID',
        'UPI_PHONE',
    ]
    
    for var in required_env_vars:
        total_checks += 1
        value = os.environ.get(var)
        if check(value and value.strip(), f"Environment variable: {var}"):
            checks_passed += 1
            # Check for placeholder values
            if any(x in str(value).lower() for x in ['your', 'change', 'placeholder', 'example']):
                warn(f"{var} appears to be a placeholder value")
                warnings.append(f"Update {var} with actual value")
    
    # Check 5: Django settings
    print("\nChecking Django configuration...")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gammers_adda.settings')
    try:
        import django
        django.setup()
        
        from django.conf import settings
        
        total_checks += 1
        if check(hasattr(settings, 'SECRET_KEY'), "SECRET_KEY configured"):
            checks_passed += 1
        
        total_checks += 1
        if check(hasattr(settings, 'DATABASES'), "Database configured"):
            checks_passed += 1
        
        total_checks += 1
        if check(hasattr(settings, 'STATIC_ROOT'), "Static files configured"):
            checks_passed += 1
        
        # Check DEBUG status
        if settings.DEBUG:
            warn("DEBUG is True - Set DEBUG=False for production!")
            warnings.append("Set DEBUG=False in production environment")
        
        # Check SECRET_KEY
        if 'insecure' in settings.SECRET_KEY.lower() or 'change' in settings.SECRET_KEY.lower():
            warn("SECRET_KEY appears to be default/insecure")
            warnings.append("Generate new SECRET_KEY for production")
        
        # Check ALLOWED_HOSTS
        if '*' in settings.ALLOWED_HOSTS:
            warn("ALLOWED_HOSTS is '*' - Specify actual domains in production")
            warnings.append("Update ALLOWED_HOSTS with your domain")
        
    except Exception as e:
        warn(f"Could not load Django settings: {e}")
    
    # Check 6: Database migrations
    print("\nChecking database...")
    total_checks += 1
    try:
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('showmigrations', '--plan', stdout=out)
        output = out.getvalue()
        
        if '[X]' in output or '(no migrations)' not in output.lower():
            if check(True, "Database migrations exist"):
                checks_passed += 1
        else:
            check(False, "Database migrations exist")
            warn("Run: python manage.py makemigrations")
    except Exception as e:
        warn(f"Could not check migrations: {e}")
    
    # Check 7: Static files
    print("\nChecking static files...")
    total_checks += 1
    static_root = Path('staticfiles')
    if check(static_root.exists(), "Static files directory exists"):
        checks_passed += 1
    else:
        warn("Run: python manage.py collectstatic")
    
    # Check 8: Git repository
    print("\nChecking Git...")
    total_checks += 1
    if check(Path('.git').exists(), "Git repository initialized"):
        checks_passed += 1
    else:
        warn("Initialize with: git init")
    
    # Check 9: .gitignore coverage
    total_checks += 1
    if Path('.gitignore').exists():
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            sensitive_files = ['.env', 'db.sqlite3', '__pycache__', '*.pyc']
            if all(pattern in gitignore_content for pattern in sensitive_files):
                if check(True, ".gitignore covers sensitive files"):
                    checks_passed += 1
            else:
                check(False, ".gitignore covers sensitive files")
                warn("Ensure .env and db.sqlite3 are in .gitignore")
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"\nPassed: {checks_passed}/{total_checks} checks")
    
    percentage = (checks_passed / total_checks * 100) if total_checks > 0 else 0
    
    if percentage == 100:
        print(f"\n{GREEN}✨ PERFECT! Your app is ready for deployment!{RESET}")
    elif percentage >= 80:
        print(f"\n{GREEN}✅ GOOD! Your app is mostly ready for deployment.{RESET}")
        print(f"{YELLOW}Address the warnings below before deploying.{RESET}")
    elif percentage >= 60:
        print(f"\n{YELLOW}⚠️  CAUTION! Fix the failed checks before deploying.{RESET}")
    else:
        print(f"\n{RED}❌ NOT READY! Multiple issues need to be fixed.{RESET}")
    
    # Warnings summary
    if warnings:
        print(f"\n{YELLOW}⚠️  WARNINGS:{RESET}")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    
    # Next steps
    print(f"\n{BLUE}📝 NEXT STEPS:{RESET}")
    if percentage >= 80:
        print("   1. Review and fix any warnings above")
        print("   2. Read DEPLOYMENT_GUIDE.md for detailed instructions")
        print("   3. Choose a hosting platform (Railway, Render, etc.)")
        print("   4. Deploy your app!")
        print(f"\n   {GREEN}Quick deploy: See DEPLOY_NOW.md{RESET}")
    else:
        print("   1. Fix all failed checks above")
        print("   2. Install missing packages: pip install -r requirements.txt")
        print("   3. Run: python manage.py migrate")
        print("   4. Run: python manage.py collectstatic")
        print("   5. Run this check again")
    
    print("\n" + "="*70)
    print(f"{BLUE}📚 Documentation:{RESET}")
    print("   • DEPLOYMENT_GUIDE.md - Complete deployment guide")
    print("   • DEPLOY_NOW.md - Quick 5-minute deploy")
    print("   • .env.production - Production environment template")
    print("="*70 + "\n")
    
    return 0 if percentage >= 80 else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Check cancelled by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Error: {e}{RESET}")
        sys.exit(1)
