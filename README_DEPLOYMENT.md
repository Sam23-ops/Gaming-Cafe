# 🎮 GAMMERS ADDA - Gaming Cafe Booking System

**Professional booking and payment system for gaming cafes**

---

## ✨ FEATURES

### 🎯 Core Features
- ✅ **Interactive Seat Booking** - Real-time seat map with availability
- ✅ **Payment Gateway** - Razorpay integration (UPI, Cards, Net Banking)
- ✅ **QR Code Payments** - UPI QR code generation
- ✅ **Email Notifications** - Professional booking confirmations
- ✅ **Session Timers** - Real-time countdown for gaming sessions
- ✅ **Admin Dashboard** - Comprehensive booking management
- ✅ **Staff Monitor** - Live session tracking for staff
- ✅ **Mobile Responsive** - Works on all devices

### 💼 Business Features
- Multiple gaming zones (PS5, PC, VR, etc.)
- Flexible pricing packages
- Add-ons (snacks, drinks, controllers)
- Discount offers and coupons
- Automatic GST calculation
- Invoice generation
- Booking history and analytics

### 🎨 Premium UI
- Modern gradient designs
- Smooth animations
- Real-time updates
- Professional email templates
- High-quality game posters (60+ games)

---

## 🚀 DEPLOYMENT OPTIONS

### Recommended: Railway.app
**Time:** 5 minutes | **Cost:** $5/month  
**Best for:** Production sites with auto-deployment

### Alternative: Render.com
**Time:** 10 minutes | **Cost:** FREE  
**Best for:** Testing and small sites

### See Full Guide
👉 **Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for step-by-step instructions**

---

## ⚡ QUICK DEPLOY (5 Minutes)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Deploy Gammers Adda"
git remote add origin https://github.com/YOUR_USERNAME/gammers-adda.git
git push -u origin main
```

### Step 2: Deploy on Railway
1. Go to https://railway.app/
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables (see below)
6. Deploy!

### Step 3: Add Environment Variables
```bash
SECRET_KEY=<random-50-characters>
DEBUG=False
ALLOWED_HOSTS=*.railway.app

EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-password>

RAZORPAY_KEY_ID=rzp_live_YOUR_KEY
RAZORPAY_KEY_SECRET=YOUR_SECRET

UPI_ID=yourpayment@paytm
UPI_PHONE=+919876543210
```

### Step 4: Create Admin
In Railway terminal:
```bash
python manage.py createsuperuser
```

**✅ DONE! Your site is LIVE!**

---

## 📋 WHAT'S INCLUDED

### Files Ready for Deployment:
- ✅ `Procfile` - Heroku/Railway deployment config
- ✅ `render.yaml` - Render.com deployment config  
- ✅ `railway.toml` - Railway deployment config
- ✅ `runtime.txt` - Python version specification
- ✅ `requirements.txt` - All dependencies listed
- ✅ `.env.production` - Production environment template
- ✅ `.gitignore` - Protects sensitive files
- ✅ `.dockerignore` - Docker optimization

### Documentation:
- 📚 `DEPLOYMENT_GUIDE.md` - Complete deployment guide (all platforms)
- 🚀 `DEPLOY_NOW.md` - Quick 5-minute deploy guide
- 💳 `PAYMENT_TESTING_GUIDE.md` - Payment system testing
- ✅ `SETUP_COMPLETE.md` - System verification
- 📊 `check_deployment_ready.py` - Pre-deployment checker

---

## 🔧 LOCAL DEVELOPMENT

### Requirements
- Python 3.10 or higher
- SQLite (included with Python)
- Git

### Setup
```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/gammers-adda.git
cd gammers-adda

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
# Copy .env.example to .env and fill in values

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Run development server
python manage.py runserver
```

### Access Points
- **Homepage:** http://127.0.0.1:8000/
- **Booking:** http://127.0.0.1:8000/bookings/wizard/
- **Admin:** http://127.0.0.1:8000/admin/
- **Dashboard:** http://127.0.0.1:8000/accounts/dashboard/

---

## 🔑 ENVIRONMENT VARIABLES

### Required
| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key (50+ chars) | Random string |
| `DEBUG` | Debug mode (False in production) | `False` |
| `ALLOWED_HOSTS` | Allowed domain names | `*.railway.app` |
| `EMAIL_HOST_USER` | Gmail address | `business@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Gmail app password | 16-digit code |
| `RAZORPAY_KEY_ID` | Razorpay key ID | `rzp_live_XXX` |
| `RAZORPAY_KEY_SECRET` | Razorpay secret key | Secret string |
| `UPI_ID` | UPI payment ID | `number@paytm` |
| `UPI_PHONE` | Business phone | `+919876543210` |

### Optional
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_ENGINE` | `sqlite3` | Database backend |
| `SEAT_HOLD_DURATION_MINUTES` | `10` | Seat hold time |
| `DEFAULT_TAX_PERCENTAGE` | `18.0` | GST percentage |
| `BUSINESS_NAME` | `Gammers Adda` | Business name |

See `.env.example` for complete list.

---

## 📊 PROJECT STRUCTURE

```
gammers-adda/
├── apps/
│   ├── accounts/       # User management & authentication
│   ├── bookings/       # Booking system & sessions
│   ├── core/           # Shared utilities
│   ├── dashboard/      # User dashboard
│   ├── engagement/     # Loyalty & rewards
│   ├── games/          # Game catalog & posters
│   ├── payments/       # Payment gateway integration
│   ├── pricing/        # Packages, add-ons, offers
│   ├── staff/          # Staff management tools
│   └── venue/          # Zones, seats, platforms
├── static/             # Static files (CSS, JS, images)
├── templates/          # HTML templates
├── gammers_adda/       # Project settings
├── manage.py           # Django management
├── requirements.txt    # Python dependencies
├── Procfile            # Deployment config
└── .env                # Environment variables (local)
```

---

## 🔒 SECURITY

### Production Security Checklist:
- ✅ `DEBUG=False` in production
- ✅ Random `SECRET_KEY` (never commit to git)
- ✅ Specific `ALLOWED_HOSTS` (not `*`)
- ✅ `.env` file in `.gitignore`
- ✅ HTTPS enabled (SSL certificate)
- ✅ Secure cookies (`SESSION_COOKIE_SECURE=True`)
- ✅ CSRF protection enabled
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection headers

### What's Protected:
- `.env` file (contains secrets)
- `db.sqlite3` database file
- `__pycache__` Python cache
- `media/` user uploads
- `.git` repository data

---

## 💳 PAYMENT INTEGRATION

### Razorpay Setup:

**1. Create Account:**
- Sign up: https://dashboard.razorpay.com/signup

**2. Get Test Keys:**
- Dashboard → Settings → API Keys
- Copy Key ID and Secret
- Use for development/testing

**3. Get Live Keys:**
- Submit business documents
- Wait for verification (1-2 days)
- Switch to Live mode
- Generate Live keys
- Update environment variables

**4. Test Payments:**
- UPI: `success@razorpay`
- Card: `4111 1111 1111 1111`
- CVV: Any 3 digits
- Expiry: Any future date

---

## 📧 EMAIL SETUP

### Gmail App Password:

**1. Enable 2-Factor Authentication:**
- https://myaccount.google.com/security

**2. Generate App Password:**
- https://myaccount.google.com/apppasswords
- Select "Mail" and your device
- Copy 16-digit password

**3. Update Environment:**
```
EMAIL_HOST_USER=your-business@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
```

---

## 🎮 ADDING CONTENT

### After Deployment:

**1. Login to Admin:**
```
https://your-site.com/admin/
```

**2. Add Zones:**
- Venue → Zones → Add Zone
- Example: "PS5 Gaming Zone", "PC Zone", "VR Zone"

**3. Add Seats:**
- Venue → Seats → Add Seat
- Link to zones and platforms

**4. Add Games:**
- Games → Games → Add Game
- Posters auto-load from `apps/games/game_posters.py`

**5. Add Pricing:**
- Pricing → Gaming Packages → Add Package
- Example: "2 Hour Gaming", "All Night Pass"

**6. Add Add-ons:**
- Pricing → Add-Ons → Add Add-On
- Example: Snacks, drinks, extra controllers

**7. Add Offers:**
- Pricing → Offers → Add Offer
- Example: "Early Bird 20% OFF", "Weekend Special"

---

## 🐛 TROUBLESHOOTING

### Common Issues:

**Issue:** Static files not loading  
**Solution:** Run `python manage.py collectstatic`

**Issue:** Payment button doesn't work  
**Solution:** Check Razorpay keys are correct and account is activated

**Issue:** Emails not sending  
**Solution:** Verify Gmail app password is correct

**Issue:** DisallowedHost error  
**Solution:** Add domain to `ALLOWED_HOSTS` environment variable

**Issue:** Database errors  
**Solution:** Run `python manage.py migrate`

See `DEPLOYMENT_GUIDE.md` for more troubleshooting.

---

## 📈 MONITORING

### Check System Health:

**1. Server Logs:**
- Railway: Click service → Logs tab
- Render: Click service → Logs tab

**2. Error Tracking:**
- Check Django logs for exceptions
- Monitor payment success rate
- Track email delivery

**3. Performance:**
- Page load times
- Database query count
- Server response times

---

## 🔄 UPDATES & MAINTENANCE

### Pushing Updates:

```bash
# 1. Make changes locally
# 2. Test thoroughly
# 3. Commit and push
git add .
git commit -m "Description of changes"
git push origin main

# 4. Platform auto-deploys
# (Railway/Render automatically rebuild and deploy)
```

### Database Migrations:

```bash
# After model changes:
python manage.py makemigrations
python manage.py migrate

# Commit migration files:
git add apps/*/migrations/
git commit -m "Add database migrations"
git push
```

---

## 📞 SUPPORT

### Resources:
- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **Quick Start:** `DEPLOY_NOW.md`
- **Payment Testing:** `PAYMENT_TESTING_GUIDE.md`

### Platform Documentation:
- Railway: https://docs.railway.app/
- Render: https://render.com/docs
- Django: https://docs.djangoproject.com/

---

## ✅ PRE-DEPLOYMENT CHECKLIST

Run this before deploying:

```bash
python check_deployment_ready.py
```

This checks:
- ✅ All required files exist
- ✅ Dependencies installed
- ✅ Environment variables set
- ✅ Database migrations ready
- ✅ Static files configured
- ✅ Git repository initialized
- ✅ Sensitive files protected

---

## 📜 LICENSE

This project is proprietary software for Gammers Adda.

---

## 🎉 READY TO DEPLOY?

Choose your path:

**🚀 Fast Deploy (5 min):** Read `DEPLOY_NOW.md`  
**📚 Complete Guide:** Read `DEPLOYMENT_GUIDE.md`  
**✅ Check Readiness:** Run `python check_deployment_ready.py`

---

**Made with ❤️ for Gammers Adda**

🎮 PLAY * ENJOY * CONNECT

---

**Questions? Issues? Contact: Sammarvalkar343@gmail.com**
