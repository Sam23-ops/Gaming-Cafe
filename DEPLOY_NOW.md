# 🚀 DEPLOY NOW - QUICK START

## ⚡ FASTEST WAY TO GET LIVE (5 Minutes)

### Option 1: Railway (Recommended)

**Time:** 5 minutes | **Cost:** $5/month credit (enough for most sites)

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Deploy Gammers Adda"

# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/gammers-adda.git
git push -u origin main

# 2. Go to https://railway.app/
# 3. Click "Start a New Project"
# 4. Choose "Deploy from GitHub repo"
# 5. Select your repo
# 6. Railway auto-deploys!

# 7. Add environment variables in Railway dashboard:
SECRET_KEY=<random-50-chars>
DEBUG=False
ALLOWED_HOSTS=*.railway.app
EMAIL_HOST_USER=Sammarvalkar343@gmail.com
EMAIL_HOST_PASSWORD=<gmail-app-password>
RAZORPAY_KEY_ID=<your-key>
RAZORPAY_KEY_SECRET=<your-secret>

# ✅ DONE! Live at: https://gammers-adda-production.railway.app
```

---

### Option 2: Render (Free)

**Time:** 10 minutes | **Cost:** FREE (750 hours/month)

```bash
# 1. Push to GitHub (same as above)

# 2. Go to https://render.com/
# 3. New → Web Service
# 4. Connect GitHub repo
# 5. Settings:
#    Build: pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
#    Start: gunicorn gammers_adda.wsgi
# 6. Add environment variables
# 7. Create Web Service

# ✅ DONE! Live at: https://gammers-adda.onrender.com
```

---

## 🔑 REQUIRED ENVIRONMENT VARIABLES

Copy these to your hosting platform:

```bash
SECRET_KEY=<generate-random-string-50-chars>
DEBUG=False
ALLOWED_HOSTS=*.railway.app,*.onrender.com

# Email (get app password: https://myaccount.google.com/apppasswords)
EMAIL_HOST_USER=Sammarvalkar343@gmail.com
EMAIL_HOST_PASSWORD=<16-digit-app-password>
OWNER_NOTIFICATION_EMAIL=Sammarvalkar343@gmail.com

# Razorpay (get from: https://dashboard.razorpay.com/app/keys)
RAZORPAY_KEY_ID=rzp_test_TkTO8jfHpUdzvi
RAZORPAY_KEY_SECRET=<your-secret>

# UPI
UPI_ID=8355923184@paytm
UPI_PHONE=+918355923184

# Business
BUSINESS_NAME=Gammers Adda
BUSINESS_PHONE=+918355923184
BUSINESS_EMAIL=info@gamersadda.com
BUSINESS_ADDRESS=Kopar Khairane, Navi Mumbai, Maharashtra
```

---

## ✅ AFTER DEPLOYMENT

1. **Create admin:**
   ```bash
   python manage.py createsuperuser
   ```

2. **Access admin:**
   ```
   https://your-site.com/admin/
   ```

3. **Add data:**
   - Zones (PS5, PC, VR)
   - Games
   - Pricing packages
   - Offers

4. **Test booking:**
   - Make test booking
   - Test payment: `success@razorpay`
   - Check email received

---

## 🎯 WHAT YOU GET

✅ Live booking system at your-site.com  
✅ Payment gateway (Razorpay)  
✅ Email notifications  
✅ Admin dashboard  
✅ Session timers  
✅ QR code tickets  
✅ Mobile responsive  
✅ SSL/HTTPS included  

---

## 🆘 NEED HELP?

Read: `DEPLOYMENT_GUIDE.md` for detailed instructions

---

**Ready? Let's deploy! 🚀**
