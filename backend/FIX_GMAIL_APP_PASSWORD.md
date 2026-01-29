# Fix Gmail Authentication Error

## The Problem
Error: `(535, b'5.7.8 Username and Password not accepted')`

This means you're using a **regular Gmail password** instead of a **Gmail App Password**.

## What's Wrong
- ❌ `'gury pavithra_7'` - This is NOT a Gmail App Password
- ✅ Gmail App Passwords are **16 characters** long (e.g., `abcd efgh ijkl mnop`)

## Solution: Get a Real Gmail App Password

### Step 1: Enable 2-Step Verification (Required First)
1. Go to: **https://myaccount.google.com/security**
2. Find **"2-Step Verification"**
3. If it's OFF, click it and enable it
   - You'll need to verify your phone number
   - Google will send you a code

### Step 2: Generate App Password
1. Go to: **https://myaccount.google.com/apppasswords**
2. You may need to sign in again
3. Under **"Select app"**, choose **"Mail"**
4. Under **"Select device"**, choose **"Other (Custom name)"**
   - Type: **"Django"** or **"Rudra Admin"**
5. Click **"Generate"**
6. Google will show you a **16-character password** like:
   ```
   abcd efgh ijkl mnop
   ```
   **⚠️ COPY THIS IMMEDIATELY** - You can only see it once!

### Step 3: Update settings.py
Open `backend/backend/settings.py` and find line 234:

**Current (WRONG):**
```python
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'gury pavithra_7')
```

**Change to (with your 16-character App Password):**
```python
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'abcdefghijklmnop')
```

**Example:**
If your App Password is `abcd efgh ijkl mnop`, use:
```python
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'abcdefghijklmnop')
```
or
```python
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'abcd efgh ijkl mnop')
```
(Both work - with or without spaces)

### Step 4: Restart Server
```bash
# Stop server (Ctrl+C)
python manage.py runserver
```

### Step 5: Test
```bash
python test_email.py
```

## Important Notes

⚠️ **You CANNOT use:**
- Your regular Gmail password
- Your Gmail username
- Any password shorter than 16 characters

✅ **You MUST use:**
- A 16-character Gmail App Password
- Generated from: https://myaccount.google.com/apppasswords
- Only works if 2-Step Verification is enabled

## Quick Links
- **App Passwords**: https://myaccount.google.com/apppasswords
- **2-Step Verification**: https://myaccount.google.com/security
- **Gmail Help**: https://support.google.com/mail/?p=BadCredentials

