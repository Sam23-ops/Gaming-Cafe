# 💳 PAYMENT FLOW - COMPLETE GUIDE

## 🔄 **EXACT BOOKING TO PAYMENT PROCESS**

### Step-by-Step Flow:

---

## **STEP 1: START BOOKING** 🎮

**URL:** http://127.0.0.1:8000/bookings/wizard/

**What happens:**
1. Customer selects date & time
2. Chooses zone (PS5 or Sim Racing)
3. Selects seat/screen
4. Chooses duration (hours)
5. Optional: Add snacks/add-ons
6. Optional: Apply offer/coupon

**After clicking "Continue to Payment":**
- Booking is created with status: `SEAT_HELD`
- Customer is redirected to checkout page

---

## **STEP 2: CHECKOUT PAGE** 💰

**URL:** http://127.0.0.1:8000/payments/checkout/<booking-reference>/

**Example:** http://127.0.0.1:8000/payments/checkout/GA-261006-A1B2C/

### What You Should See:

#### **Left Side - Payment Options**

**Option 1: Razorpay Gateway** (Primary)
- **PAY NOW button** (big orange button)
- Quick UPI app buttons (GPay, PhonePe, Paytm, BHIM)
- When clicked → Opens Razorpay modal with:
  - UPI payment
  - Cards (Debit/Credit)
  - Net Banking
  - Wallets (Paytm, PhonePe, etc.)
  - EMI options

**Option 2: Direct UPI Payment** (Alternative)
- **Tab 1: QR Code**
  - Shows QR code to scan
  - Works with any UPI app
- **Tab 2: UPI ID**
  - Shows: `8355923184@paytm` (copy button)
  - Shows: `+91 83559 23184` (copy button)
  - WhatsApp confirmation button

#### **Right Side - Order Summary**
- Station/Screen number
- Zone name
- Date & time
- Duration
- Pricing breakdown
- Total amount

---

## **STEP 3: PAYMENT PROCESSING** ✅

### **Option A: Razorpay Payment**

1. Click **"PAY ₹XXX NOW"** button
2. Razorpay modal opens
3. Choose payment method:
   - **UPI**: Enter UPI ID or scan QR
   - **Card**: Enter card details
   - **Net Banking**: Select bank
   - **Wallet**: Select wallet
4. Complete payment
5. Payment verified automatically
6. Redirected to confirmation page

### **Option B: Direct UPI Payment**

1. Switch to **"QR Code"** tab
2. Open GPay/PhonePe/Paytm
3. Scan QR code
4. Pay the exact amount
5. Take screenshot of payment
6. Click **"Send Payment Confirmation on WhatsApp"**
7. Send screenshot to +91 83559 23184

**Note:** With direct UPI, admin must manually verify payment and confirm booking.

---

## **STEP 4: CONFIRMATION** 🎉

**URL:** http://127.0.0.1:8000/bookings/confirmation/<booking-reference>/

**What happens:**
- Booking status changes to: `CONFIRMED`
- Email sent to owner: Sammarvalkar343@gmail.com
- Customer receives booking ticket
- Can view/download invoice

---

## 🔍 **TROUBLESHOOTING PAYMENT ISSUES**

### **Issue 1: "Payment page not showing"**

**Check:**
1. Is booking created successfully?
2. Check booking status - should be `SEAT_HELD` or `PAYMENT_PENDING`
3. Check URL format: `/payments/checkout/<booking-reference>/`

**How to verify:**
```bash
# Check if booking exists
http://127.0.0.1:8000/admin/
# Login → Bookings → Search for your booking reference
```

---

### **Issue 2: "Razorpay button not working"**

**Possible causes:**

**A. Razorpay SDK not loading**
- Check browser console (F12)
- Look for: `Razorpay is not defined` error
- **Fix:** Template should have:
  ```html
  <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
  ```

**B. API keys not configured**
- **Check .env file:**
  ```
  RAZORPAY_KEY_ID=rzp_test_TkTO8jfHpUdzvi
  RAZORPAY_KEY_SECRET=YY5BXfXGstlM7UPvTwuG4F70
  ```
- These are valid test keys!

**C. JavaScript error**
- Open browser console (F12)
- Look for red errors
- Common issue: `payWithRazorpay is not defined`

---

### **Issue 3: "QR code not showing"**

**Possible causes:**

**A. Python packages not installed**
```bash
pip install qrcode[pil] pillow
```

**B. QR generation failing**
- Check server terminal for errors
- Error might say: "No module named 'qrcode'"

---

### **Issue 4: "Clicking PAY NOW does nothing"**

**Debug steps:**

1. **Open browser console** (F12 → Console tab)
2. Click the PAY NOW button
3. Look for errors

**Common errors:**

**Error:** `CSRF token missing`
**Fix:** Template should have `{{ csrf_token }}`

**Error:** `fetch failed` or `404 Not Found`
**Fix:** Check API endpoint exists:
- `/payments/razorpay/create-order/<booking-ref>/`

**Error:** `Razorpay is not defined`
**Fix:** Razorpay SDK script not loaded

---

## 🧪 **TESTING THE PAYMENT FLOW**

### **Test with Razorpay Test Mode:**

Razorpay test mode NEVER charges real money!

**Test Card Numbers:**
```
Card: 4111 1111 1111 1111
CVV: Any 3 digits (e.g., 123)
Expiry: Any future date
Name: Any name
```

**Test UPI IDs:**
```
success@razorpay (Successful payment)
failure@razorpay (Failed payment)
```

---

## 📋 **COMPLETE CHECKLIST**

Use this checklist to verify payment is working:

### **Pre-requisites:**
- [ ] Server is running: `python manage.py runserver`
- [ ] .env file has Razorpay keys
- [ ] python-dotenv installed: `pip install python-dotenv`
- [ ] qrcode installed: `pip install qrcode[pil] pillow`

### **Booking Flow:**
- [ ] Can access: http://127.0.0.1:8000/bookings/wizard/
- [ ] Can select date, zone, seat, duration
- [ ] Clicking "Continue to Payment" works
- [ ] Redirects to: `/payments/checkout/<ref>/`

### **Checkout Page:**
- [ ] Page loads without errors
- [ ] See "PAY ₹XXX NOW" button
- [ ] See UPI quick buttons (GPay, PhonePe, etc.)
- [ ] See QR Code tab
- [ ] See UPI ID tab with copy buttons
- [ ] Order summary shows on right side

### **Payment Options:**
- [ ] Clicking "PAY NOW" opens Razorpay modal
- [ ] Modal shows payment options (UPI, Cards, etc.)
- [ ] QR code displays correctly
- [ ] Can copy UPI ID with copy button
- [ ] WhatsApp link works

### **After Payment:**
- [ ] Successful payment redirects to confirmation
- [ ] Booking status changes to CONFIRMED
- [ ] Can view invoice/ticket
- [ ] Email sent to owner (if email configured)

---

## 🔧 **QUICK FIXES**

### **If nothing works, try this:**

```bash
# 1. Stop server (Ctrl+C)

# 2. Install required packages
pip install python-dotenv qrcode[pil] pillow razorpay

# 3. Check .env file exists and has content
cat .env

# 4. Restart server
python manage.py runserver

# 5. Clear browser cache (Ctrl+Shift+Delete)

# 6. Try booking again
```

---

## 📞 **STILL NOT WORKING?**

### **Get exact error details:**

1. **Check browser console:**
   - Press F12
   - Go to Console tab
   - Copy any red errors

2. **Check server terminal:**
   - Look for red error messages
   - Copy the full traceback

3. **Check these URLs work:**
   - http://127.0.0.1:8000/ (Homepage)
   - http://127.0.0.1:8000/bookings/wizard/ (Booking page)
   - http://127.0.0.1:8000/games/ (Games list)

---

## ✅ **EXPECTED BEHAVIOR**

### **Razorpay Test Mode** (Current Setup):

When you click "PAY NOW":
1. Modal opens instantly
2. Shows: "Test Mode" banner
3. All payment methods available
4. Use test credentials (see above)
5. Payment succeeds immediately
6. Redirects to confirmation

### **Direct UPI Payment:**

When you scan QR code:
1. Any UPI app opens
2. Shows: "Pay to Gammers Adda"
3. Amount is pre-filled
4. Note includes booking reference
5. Complete payment in your UPI app
6. Send screenshot via WhatsApp

---

## 🎯 **NEXT STEPS**

1. **Try creating a test booking**
2. **Go through payment flow**
3. **If error occurs, check browser console**
4. **Copy exact error message**
5. **Share error for specific fix**

---

**Your setup is correct! Payment should work.** 

**Test URL:** http://127.0.0.1:8000/bookings/wizard/

If payment page still doesn't show, please share:
1. Exact URL you're trying to access
2. Any error message in browser console (F12)
3. Any error in server terminal

