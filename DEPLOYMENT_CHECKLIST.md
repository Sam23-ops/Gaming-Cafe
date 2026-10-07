# ✅ DEPLOYMENT CHECKLIST

Complete this checklist before and after deployment to ensure everything works correctly.

---

## 📋 PRE-DEPLOYMENT (Before You Deploy)

### 1. Code & Files
- [ ] All code committed to git
- [ ] `.env` file is NOT committed (check .gitignore)
- [ ] `.env.production` template reviewed
- [ ] `requirements.txt` includes all packages
- [ ] Deployment files exist (Procfile, render.yaml, railway.toml)
- [ ] `runtime.txt` specifies Python version

### 2. Credentials Prepared
- [ ] SECRET_KEY generated (50+ random characters)
- [ ] Gmail app password obtained
  - Go to: https://myaccount.google.com/apppasswords
  - Create password for "Mail"
  - Save 16-digit code
- [ ] Razorpay test keys copied from dashboard
  - Dashboard: https://dashboard.razorpay.com/app/keys
  - Save Key ID and Secret
- [ ] UPI details confirmed (ID and phone number)
- [ ] Business information ready (name, phone, email, address)

### 3. Accounts Created
- [ ] GitHub account created and verified
- [ ] Hosting platform account created:
  - [ ] Railway.app OR
  - [ ] Render.com OR
  - [ ] PythonAnywhere OR
  - [ ] Heroku
- [ ] Gmail account with 2FA enabled
- [ ] Razorpay account created and documents submitted

### 4. Local Testing Done
- [ ] Development server runs without errors
- [ ] Can access homepage: http://127.0.0.1:8000/
- [ ] Can create bookings
- [ ] Payment page loads correctly
- [ ] Test payment works (success@razorpay)
- [ ] Email notifications send (check spam folder)
- [ ] Admin panel accessible
- [ ] Session timers work
- [ ] All pages load without errors
- [ ] No console errors in browser (F12)

### 5. Database Ready
- [ ] All migrations created: `python manage.py makemigrations`
- [ ] All migrations applied: `python manage.py migrate`
- [ ] No migration conflicts
- [ ] Database has all required tables

### 6. Static Files
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] WhiteNoise middleware added to settings.py
- [ ] STATIC_ROOT configured
- [ ] CSS and images load correctly

---

## 🚀 DEPLOYMENT (During Deployment)

### 1. GitHub Repository
- [ ] Repository created on GitHub
- [ ] Local git initialized: `git init`
- [ ] All files added: `git add .`
- [ ] Initial commit: `git commit -m "Deploy Gammers Adda"`
- [ ] Remote added: `git remote add origin URL`
- [ ] Pushed to main: `git push -u origin main`

### 2. Hosting Platform Setup
- [ ] New project/service created
- [ ] GitHub repository connected
- [ ] Build command configured (if manual):
  ```
  pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
  ```
- [ ] Start command configured (if manual):
  ```
  gunicorn gammers_adda.wsgi
  ```
- [ ] Python version specified (3.10+)

### 3. Environment Variables Set
- [ ] `SECRET_KEY` (random 50 chars)
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` (your domain/platform domain)
- [ ] `EMAIL_HOST=smtp.gmail.com`
- [ ] `EMAIL_PORT=587`
- [ ] `EMAIL_USE_TLS=True`
- [ ] `EMAIL_HOST_USER` (your Gmail)
- [ ] `EMAIL_HOST_PASSWORD` (app password)
- [ ] `OWNER_NOTIFICATION_EMAIL` (your email)
- [ ] `RAZORPAY_KEY_ID` (test key for now)
- [ ] `RAZORPAY_KEY_SECRET` (test secret)
- [ ] `UPI_ID` (your UPI ID)
- [ ] `UPI_PHONE` (your phone)
- [ ] `BUSINESS_NAME` (Gammers Adda)
- [ ] `BUSINESS_PHONE` (your business phone)
- [ ] `BUSINESS_EMAIL` (your business email)
- [ ] `BUSINESS_ADDRESS` (your address)

### 4. Database (if PostgreSQL)
- [ ] PostgreSQL add-on added
- [ ] DATABASE_URL automatically set
- [ ] Migrations run automatically or manually

### 5. Deployment Started
- [ ] Build started (watch logs)
- [ ] Build completed successfully
- [ ] No errors in build logs
- [ ] Service started
- [ ] Health check passed

---

## ✅ POST-DEPLOYMENT (After Site is Live)

### 1. Basic Access
- [ ] Site URL accessible (https://your-site.com)
- [ ] Homepage loads correctly
- [ ] No 500 errors
- [ ] No 404 errors on main pages
- [ ] SSL certificate active (HTTPS works)

### 2. Create Superuser
- [ ] Access platform terminal/console
- [ ] Run: `python manage.py createsuperuser`
- [ ] Username created
- [ ] Email set
- [ ] Password set
- [ ] Can login to admin: https://your-site.com/admin/

### 3. Admin Panel Setup
- [ ] Admin panel accessible
- [ ] Can login with superuser
- [ ] All models visible in admin
- [ ] No errors when viewing models

### 4. Add Initial Data
- [ ] **Add Zones:**
  - [ ] PS5 Gaming Zone
  - [ ] PC Gaming Zone
  - [ ] VR Zone (if applicable)
  - [ ] Sim Racing Zone (if applicable)
- [ ] **Add Platforms:**
  - [ ] PlayStation 5
  - [ ] PlayStation 4
  - [ ] Gaming PC
  - [ ] VR Headset
- [ ] **Add Seats:**
  - [ ] Link seats to zones
  - [ ] Set seat status (available)
  - [ ] Add seat identifiers (numbers/names)
- [ ] **Add Games:**
  - [ ] Popular games added
  - [ ] Game posters loading (from game_posters.py)
  - [ ] Games linked to platforms
- [ ] **Add Pricing Packages:**
  - [ ] Hourly rates
  - [ ] Special packages (2hr, 4hr, all-night)
  - [ ] Package prices set
- [ ] **Add Add-ons:**
  - [ ] Snacks and drinks
  - [ ] Extra controllers
  - [ ] Prices set
- [ ] **Add Offers:**
  - [ ] Early bird discount
  - [ ] Weekend specials
  - [ ] Offer validity dates set

### 5. Test Complete Flow
- [ ] **Booking Creation:**
  - [ ] Can access booking wizard
  - [ ] Can select date and time
  - [ ] Can select zone
  - [ ] Seat map displays correctly
  - [ ] Can select seats
  - [ ] Can select duration
  - [ ] Can add add-ons
  - [ ] Can apply offers/coupons
  - [ ] Price calculation correct
  - [ ] Can proceed to payment

- [ ] **Payment Process:**
  - [ ] Payment page loads
  - [ ] Razorpay button visible
  - [ ] Clicking button opens Razorpay modal
  - [ ] Test payment works (success@razorpay)
  - [ ] Payment confirmation received
  - [ ] Redirected to confirmation page

- [ ] **After Payment:**
  - [ ] Booking status = CONFIRMED
  - [ ] Confirmation page shows details
  - [ ] Invoice generated
  - [ ] QR code ticket created
  - [ ] Can download invoice

- [ ] **Email Notifications:**
  - [ ] Booking confirmation email sent
  - [ ] Email received in inbox (check spam)
  - [ ] Email content correct
  - [ ] Owner notification sent
  - [ ] Email template looks professional

- [ ] **Session Timer:**
  - [ ] Can access session timer page
  - [ ] Countdown displays correctly
  - [ ] Time updates every second
  - [ ] Progress bar animates
  - [ ] Status shows correctly

- [ ] **Staff Monitor:**
  - [ ] Can access staff monitor
  - [ ] Active sessions display
  - [ ] Timers update in real-time
  - [ ] Can extend session
  - [ ] Can pause/resume
  - [ ] Can terminate session

### 6. Frontend Verification
- [ ] All pages load without errors
- [ ] CSS styles applied correctly
- [ ] Images and icons display
- [ ] JavaScript works (no console errors)
- [ ] Forms submit correctly
- [ ] Buttons and links work
- [ ] Mobile responsive (test on phone)
- [ ] Tablet view works
- [ ] Desktop view works

### 7. Security Check
- [ ] `DEBUG=False` confirmed
- [ ] Admin panel requires login
- [ ] Customer pages require login (dashboard, etc.)
- [ ] Staff pages require staff permission
- [ ] HTTPS working (padlock in browser)
- [ ] No sensitive data in error pages
- [ ] CSRF protection working

### 8. Performance Check
- [ ] Homepage loads in <3 seconds
- [ ] Booking page loads in <3 seconds
- [ ] Payment page loads in <3 seconds
- [ ] No slow queries (check logs)
- [ ] Static files load from CDN/WhiteNoise

---

## 🔄 GOING TO PRODUCTION (Switch from Test to Live)

### 1. Razorpay Activation
- [ ] Razorpay account fully activated
  - Go to: https://dashboard.razorpay.com/
  - Submit business documents
  - Wait for verification (1-2 days)
  - Activation email received
- [ ] Switch dashboard to LIVE mode
- [ ] Generate LIVE API keys
- [ ] Update environment variables:
  - `RAZORPAY_KEY_ID=rzp_live_...`
  - `RAZORPAY_KEY_SECRET=...`
- [ ] Test real payment with small amount
- [ ] Payment successful
- [ ] Money received in Razorpay account

### 2. Domain Configuration (Optional)
- [ ] Domain purchased (GoDaddy, Namecheap, etc.)
- [ ] DNS records updated
  - CNAME record for www
  - A record for root (if required)
- [ ] SSL certificate provisioned
- [ ] Domain propagated (can access site via domain)
- [ ] Environment variable updated:
  - `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`

### 3. Email Configuration
- [ ] Production email tested
- [ ] Emails not going to spam
- [ ] Email sending rate checked (Gmail: 500/day)
- [ ] Consider upgrading to email service if needed:
  - SendGrid (100 emails/day free)
  - Mailgun (5000 emails/month free)
  - AWS SES (pay as you go)

### 4. Monitoring Setup
- [ ] Error tracking configured (optional):
  - Sentry.io (free tier)
  - Rollbar
- [ ] Uptime monitoring (optional):
  - UptimeRobot (free)
  - Pingdom
- [ ] Analytics added (optional):
  - Google Analytics
  - Plausible

---

## 📊 FINAL VERIFICATION

### Before Announcing to Customers:
- [ ] Complete test booking as customer
- [ ] Make real payment (small amount)
- [ ] Receive confirmation email
- [ ] Check admin panel shows booking
- [ ] Test session timer works
- [ ] Staff can monitor session
- [ ] Customer can view booking history
- [ ] Invoice downloads correctly
- [ ] All links work
- [ ] No broken pages
- [ ] Contact information correct
- [ ] Business details accurate
- [ ] Pricing is correct
- [ ] Terms and conditions present (if applicable)
- [ ] Privacy policy present (if applicable)

### Marketing Ready:
- [ ] Booking URL ready to share
- [ ] QR code generated for physical display
- [ ] Social media posts prepared
- [ ] WhatsApp message template ready
- [ ] Customer instructions written
- [ ] Staff trained on new system

---

## 🆘 TROUBLESHOOTING COMMON ISSUES

### Issue: Site shows "DisallowedHost"
**Solution:**
- Add your domain to `ALLOWED_HOSTS` environment variable
- Format: `yourdomain.com,www.yourdomain.com`

### Issue: Static files (CSS/images) not loading
**Solution:**
- Run: `python manage.py collectstatic --noinput`
- Check `STATIC_ROOT` in settings.py
- Verify WhiteNoise middleware is enabled

### Issue: Payment button doesn't work
**Solution:**
- Check Razorpay keys are correct
- Verify keys are for correct mode (test/live)
- Check browser console for JavaScript errors
- Disable ad blockers

### Issue: Emails not sending
**Solution:**
- Verify Gmail app password is correct
- Check environment variables are set
- Test email manually in Django shell
- Check Gmail sending limits (500/day)
- Look in spam folder

### Issue: Database errors after deployment
**Solution:**
- Run migrations: `python manage.py migrate`
- Check DATABASE_URL is set correctly
- Verify database is accessible

### Issue: 500 Internal Server Error
**Solution:**
- Check platform logs for errors
- Verify `DEBUG=False` (but check logs for real error)
- Run: `python manage.py check --deploy`
- Check all environment variables are set

---

## ✅ SUCCESS CRITERIA

Your deployment is successful when:

✅ Site is accessible via HTTPS  
✅ Customers can create bookings  
✅ Payments process successfully  
✅ Emails send automatically  
✅ Admin can manage bookings  
✅ Staff can monitor sessions  
✅ All timers work correctly  
✅ Mobile devices work properly  
✅ No critical errors in logs  
✅ Performance is acceptable (<3s page loads)  

---

## 🎉 CONGRATULATIONS!

Once all items are checked, your Gammers Adda booking system is fully deployed and operational!

**Next Steps:**
1. Share booking URL with customers
2. Train staff on admin panel and monitor
3. Monitor bookings and feedback
4. Make adjustments as needed

**Good luck with your gaming cafe! 🚀**

---

**Need Help?**
- Check DEPLOYMENT_GUIDE.md for detailed solutions
- Review platform-specific logs
- Email: Sammarvalkar343@gmail.com
