# 🚀 GAMMERS ADDA - DEPLOYMENT GUIDE

Complete guide to deploy your gaming cafe booking system to production!

---

## 📋 TABLE OF CONTENTS

1. [Quick Comparison - Choose Your Platform](#quick-comparison)
2. [Option 1: Railway (Recommended - Easiest)](#option-1-railway)
3. [Option 2: Render (Free Tier Available)](#option-2-render)
4. [Option 3: PythonAnywhere (Free for Small Sites)](#option-3-pythonanywhere)
5. [Option 4: Heroku (Popular Choice)](#option-4-heroku)
6. [Post-Deployment Setup](#post-deployment-setup)
7. [Custom Domain Setup](#custom-domain-setup)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 QUICK COMPARISON

| Platform | Free Tier | Ease | Best For |
|----------|-----------|------|----------|
| **Railway** ⭐ | $5 credit/month | ⭐⭐⭐⭐⭐ Easiest | Production ready, auto-deployments |
| **Render** | 750 hrs/month | ⭐⭐⭐⭐ Easy | Free hosting, sleeps when inactive |
| **PythonAnywhere** | Yes (limited) | ⭐⭐⭐ Medium | Small traffic sites |
| **Heroku** | No free tier | ⭐⭐⭐⭐ Easy | Established, reliable |

**Recommendation:** Start with **Railway** for production or **Render** if you want free hosting.

---

## 🚂 OPTION 1: RAILWAY (RECOMMENDED)

Railway is the **easiest and fastest** way to deploy Django apps. Perfect for production!

### ✅ Pros:
- 🚀 Automatic deployments from GitHub
- 💾 Built-in PostgreSQL database
- 🔒 SSL certificates included
- 📊 Real-time logs and metrics
- ⚡ Fast deployment (under 2 minutes)

### Step 1: Prepare Repository

```bash
# Install Git if not already installed
git --version

# Initialize repository
git init
git add .
git commit -m "Initial commit - Ready for deployment"
```

### Step 2: Push to GitHub

1. Go to https://github.com/new
2. Create new repository: `gammers-adda`
3. **Don't** add README, .gitignore, or license (we have them)
4. Copy the commands shown and run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/gammers-adda.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Railway

1. **Go to:** https://railway.app/
2. **Click:** "Start a New Project"
3. **Choose:** "Deploy from GitHub repo"
4. **Connect:** Your GitHub account
5. **Select:** `gammers-adda` repository
6. **Railway automatically:**
   - Detects it's a Django app
   - Installs dependencies
   - Runs migrations
   - Starts the server

### Step 4: Add Environment Variables

In Railway dashboard:

1. Click your project
2. Go to **"Variables"** tab
3. Click **"New Variable"**
4. Add each of these:

```
SECRET_KEY=<generate-random-50-char-string>
DEBUG=False
ALLOWED_HOSTS=*.railway.app

# Your actual email
EMAIL_HOST_USER=Sammarvalkar343@gmail.com
EMAIL_HOST_PASSWORD=<your-gmail-app-password>
OWNER_NOTIFICATION_EMAIL=Sammarvalkar343@gmail.com

# Your actual Razorpay LIVE keys
RAZORPAY_KEY_ID=rzp_live_YOUR_KEY
RAZORPAY_KEY_SECRET=YOUR_SECRET

# Your actual UPI details
UPI_ID=8355923184@paytm
UPI_PHONE=+918355923184

# Business details
BUSINESS_NAME=Gammers Adda
BUSINESS_PHONE=+918355923184
BUSINESS_EMAIL=info@gamersadda.com
BUSINESS_ADDRESS=Kopar Khairane, Navi Mumbai, Maharashtra
```

### Step 5: Add PostgreSQL Database (Optional but Recommended)

1. In Railway dashboard, click **"New"**
2. Select **"Database" → "PostgreSQL"**
3. Railway automatically sets DATABASE_URL
4. Your app will use it automatically

### Step 6: Deploy!

Railway deploys automatically! Your site will be live at:
```
https://gammers-adda-production.railway.app
```

### Step 7: Create Superuser

In Railway dashboard:
1. Click on your service
2. Go to **"Settings"** → **"Deployments"**
3. Click on latest deployment
4. Click **"Shell"** or **"Terminal"**
5. Run:
```bash
python manage.py createsuperuser
```

**✅ DONE! Your site is LIVE!**

---

## 🎨 OPTION 2: RENDER (FREE TIER)

Render offers **750 hours/month free** - perfect for testing!

### Step 1: Prepare Files (Already Done ✅)

All files are ready:
- ✅ `render.yaml` - Deployment config
- ✅ `requirements.txt` - Dependencies
- ✅ Settings configured for production

### Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Deploy to Render"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/gammers-adda.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Render

1. **Go to:** https://render.com/
2. **Sign up** with GitHub
3. **Click:** "New +" → "Web Service"
4. **Connect:** Your `gammers-adda` repository
5. **Fill in:**
   - Name: `gammers-adda`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command: `gunicorn gammers_adda.wsgi`
6. **Choose:** Free plan
7. **Click:** "Create Web Service"

### Step 4: Add Environment Variables

In Render dashboard, go to **"Environment"** tab and add:

```
SECRET_KEY=<generate-random-string>
DEBUG=False
ALLOWED_HOSTS=*.onrender.com
EMAIL_HOST_USER=Sammarvalkar343@gmail.com
EMAIL_HOST_PASSWORD=<app-password>
OWNER_NOTIFICATION_EMAIL=Sammarvalkar343@gmail.com
RAZORPAY_KEY_ID=rzp_live_YOUR_KEY
RAZORPAY_KEY_SECRET=YOUR_SECRET
UPI_ID=8355923184@paytm
UPI_PHONE=+918355923184
```

### Step 5: Wait for Deploy

- First deploy takes 5-10 minutes
- Watch logs in dashboard
- Your site will be at: `https://gammers-adda.onrender.com`

**⚠️ Note:** Free tier sleeps after 15 minutes of inactivity. First request after sleep takes 30 seconds to wake up.

---

## 🐍 OPTION 3: PYTHONANYWHERE (FREE FOR SMALL SITES)

Good for small traffic sites or testing. **100% FREE** forever!

### Limitations:
- No automatic deployments
- Limited storage (512 MB)
- Only HTTP (no HTTPS on free tier)
- Manual setup required

### Step 1: Sign Up

1. Go to: https://www.pythonanywhere.com/
2. Sign up for **FREE Beginner account**
3. Verify email

### Step 2: Upload Code

**Option A: From GitHub (Recommended)**
```bash
# In PythonAnywhere Bash console:
git clone https://github.com/YOUR_USERNAME/gammers-adda.git
cd gammers-adda
```

**Option B: Upload ZIP**
1. Compress your project folder
2. Upload via Files tab
3. Extract in bash console

### Step 3: Create Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.10 gammers-env
workon gammers-env
pip install -r requirements.txt
```

### Step 4: Configure Web App

1. Go to **"Web"** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Choose **"Python 3.10"**
5. Set:
   - Source code: `/home/YOUR_USERNAME/gammers-adda`
   - Working directory: `/home/YOUR_USERNAME/gammers-adda`
   - Virtualenv: `/home/YOUR_USERNAME/.virtualenvs/gammers-env`

### Step 5: Configure WSGI

Click on WSGI configuration file and replace content with:

```python
import os
import sys

path = '/home/YOUR_USERNAME/gammers-adda'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'gammers_adda.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Step 6: Set Environment Variables

In **"Web"** tab, scroll to **"Environment variables"** and add all your variables.

### Step 7: Setup Static Files

In **"Web"** tab, under **"Static files"**:
- URL: `/static/`
- Directory: `/home/YOUR_USERNAME/gammers-adda/staticfiles/`

### Step 8: Initialize Database

In **Bash console**:
```bash
cd gammers-adda
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### Step 9: Reload

Click green **"Reload"** button in Web tab.

Your site is at: `https://YOUR_USERNAME.pythonanywhere.com`

---

## 🔷 OPTION 4: HEROKU

Reliable and popular, but **no free tier** anymore. Starts at $7/month.

### Step 1: Install Heroku CLI

**Windows:**
```bash
# Download from: https://devcenter.heroku.com/articles/heroku-cli
# Or use chocolatey:
choco install heroku-cli
```

**Verify:**
```bash
heroku --version
```

### Step 2: Login to Heroku

```bash
heroku login
# Opens browser, click "Log in"
```

### Step 3: Create Heroku App

```bash
heroku create gammers-adda
# Or choose your own name:
# heroku create your-custom-name
```

### Step 4: Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:mini
```

### Step 5: Set Environment Variables

```bash
heroku config:set SECRET_KEY='your-secret-key'
heroku config:set DEBUG=False
heroku config:set EMAIL_HOST_USER=Sammarvalkar343@gmail.com
heroku config:set EMAIL_HOST_PASSWORD='your-app-password'
heroku config:set RAZORPAY_KEY_ID='rzp_live_YOUR_KEY'
heroku config:set RAZORPAY_KEY_SECRET='YOUR_SECRET'
heroku config:set UPI_ID=8355923184@paytm
heroku config:set UPI_PHONE=+918355923184
```

### Step 6: Deploy

```bash
git push heroku main
```

### Step 7: Run Migrations

```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Step 8: Open Your Site

```bash
heroku open
```

Your site is at: `https://gammers-adda.herokuapp.com`

---

## ⚙️ POST-DEPLOYMENT SETUP

After deploying to **any platform**, complete these steps:

### 1. Create Superuser (Admin Account)

Access your server's shell and run:
```bash
python manage.py createsuperuser
```

Enter:
- Username: `admin`
- Email: `Sammarvalkar343@gmail.com`
- Password: (choose strong password)

### 2. Access Admin Panel

Visit: `https://your-site.com/admin/`

Login with superuser credentials.

### 3. Add Initial Data

**Add Zones:**
1. Go to Venue → Zones
2. Add: PS5 Gaming Zone, PC Gaming Zone, VR Zone, etc.
3. Add platforms for each zone

**Add Games:**
1. Go to Games → Games
2. Add popular games
3. Game posters will auto-load from `apps/games/game_posters.py`

**Add Pricing:**
1. Go to Pricing → Gaming Packages
2. Add: Hourly packages, Special deals
3. Add Add-ons: Snacks, drinks, etc.

**Add Offers:**
1. Go to Pricing → Offers
2. Add: Early bird discount, Weekend special, etc.

### 4. Update ALLOWED_HOSTS

In your platform's environment variables, update:
```
ALLOWED_HOSTS=your-actual-domain.com,www.your-actual-domain.com
```

### 5. Switch to LIVE Razorpay Keys

⚠️ **IMPORTANT:** You're currently using TEST keys!

1. Go to: https://dashboard.razorpay.com/
2. Switch to **LIVE mode** (toggle in top-right)
3. Go to Settings → API Keys
4. Generate LIVE keys
5. Update environment variables:
   ```
   RAZORPAY_KEY_ID=rzp_live_YOUR_LIVE_KEY
   RAZORPAY_KEY_SECRET=YOUR_LIVE_SECRET
   ```

6. **Activate your Razorpay account:**
   - Submit business documents
   - Wait for verification (1-2 days)
   - Once approved, LIVE mode is active

### 6. Configure Email Notifications

**Get Gmail App Password:**
1. Go to: https://myaccount.google.com/apppasswords
2. Create app password for "Mail"
3. Update environment variable:
   ```
   EMAIL_HOST_PASSWORD=your-16-digit-app-password
   ```

### 7. Test Complete Flow

1. **Create test booking**
2. **Make test payment**
3. **Verify email received**
4. **Check admin panel for booking**
5. **Test session timer**

---

## 🌐 CUSTOM DOMAIN SETUP

Want to use your own domain like `www.gammersadda.com`?

### Step 1: Buy Domain

Buy from:
- GoDaddy: https://godaddy.com/
- Namecheap: https://namecheap.com/
- Google Domains: https://domains.google/

Cost: ₹500-1000/year for `.com` domain

### Step 2: Get Your Platform's DNS Settings

**Railway:**
- Go to Settings → Domains
- Click "Custom Domain"
- Add `gammersadda.com`
- Railway shows DNS records to add

**Render:**
- Go to Settings → Custom Domain
- Add your domain
- Copy provided DNS records

**Heroku:**
```bash
heroku domains:add gammersadda.com
heroku domains:add www.gammersadda.com
```

### Step 3: Update DNS Records

In your domain registrar (GoDaddy, etc.):

1. Go to DNS Management
2. Add CNAME record:
   ```
   Type: CNAME
   Name: www
   Value: your-app-name.platform.com
   ```

3. Add A record (if provided):
   ```
   Type: A
   Name: @
   Value: (IP provided by platform)
   ```

### Step 4: Wait for DNS Propagation

- Takes 1-48 hours
- Usually works in 15-30 minutes
- Check status: https://dnschecker.org/

### Step 5: Update ALLOWED_HOSTS

```
ALLOWED_HOSTS=gammersadda.com,www.gammersadda.com
```

### Step 6: Enable HTTPS

Most platforms (Railway, Render, Heroku) automatically provision SSL certificates.

**If manual setup needed:**
```
SECURE_SSL_REDIRECT=True
```

---

## 🐛 TROUBLESHOOTING

### Issue: "DisallowedHost" Error

**Problem:** Accessing site shows DisallowedHost error

**Solution:**
```
# Add your domain to ALLOWED_HOSTS
ALLOWED_HOSTS=your-site.com,*.railway.app
```

### Issue: Static Files Not Loading

**Problem:** Site loads but no CSS/images

**Solution:**
```bash
python manage.py collectstatic --noinput
```

Make sure `whitenoise` is in requirements.txt and middleware.

### Issue: Database Migration Failed

**Problem:** Deployment fails during migrate step

**Solution:**
```bash
# SSH into your server
python manage.py migrate --run-syncdb
```

### Issue: Email Not Sending

**Problem:** Bookings work but no emails

**Solution:**
1. Check Gmail app password is correct
2. Enable "Less secure app access" (if using old Gmail security)
3. Check environment variables are set
4. Test email in Django shell:
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Message', 'from@gmail.com', ['to@gmail.com'])
   ```

### Issue: Razorpay Payment Fails

**Problem:** Payment button doesn't work

**Solution:**
1. Check Razorpay keys are LIVE keys (start with `rzp_live_`)
2. Check keys are correct in environment variables
3. Verify Razorpay account is activated (not in test mode)
4. Check browser console for JavaScript errors

### Issue: Site is Slow

**Problem:** Pages take long to load

**Solution:**
1. **Use PostgreSQL instead of SQLite**
2. **Enable caching:**
   ```python
   # In settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
       }
   }
   ```
3. **Optimize database queries**
4. **Use CDN for static files**

---

## ✅ PRE-DEPLOYMENT CHECKLIST

Before going live, verify:

- [ ] All environment variables set correctly
- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is random and secret
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] Database migrations completed
- [ ] Static files collected
- [ ] Superuser created
- [ ] Initial data added (zones, games, pricing)
- [ ] Email sending works (test it!)
- [ ] Razorpay LIVE keys configured
- [ ] Razorpay account activated
- [ ] Payment flow tested end-to-end
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate working (HTTPS)
- [ ] All pages load correctly
- [ ] No console errors in browser
- [ ] Mobile responsive design works
- [ ] Booking flow works completely
- [ ] Admin panel accessible

---

## 🎉 YOU'RE LIVE!

Congratulations! Your Gammers Adda booking system is now live and ready for customers!

**Next Steps:**
1. Share your site URL with customers
2. Print QR code linking to booking page
3. Add "Book Now" button to social media
4. Set up Google Analytics (optional)
5. Monitor bookings in admin panel
6. Check email notifications are working

**Need Help?**
- Check server logs for errors
- Test each component individually
- Reach out if you encounter issues

---

## 📞 SUPPORT RESOURCES

- Railway Docs: https://docs.railway.app/
- Render Docs: https://render.com/docs
- Django Deployment Checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
- Razorpay Integration: https://razorpay.com/docs/

---

**Made with ❤️ for Gammers Adda**

🎮 PLAY * ENJOY * CONNECT
