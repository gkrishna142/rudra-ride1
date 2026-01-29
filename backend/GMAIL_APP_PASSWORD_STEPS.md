# How to Get Gmail App Password - Step by Step

## What is an App Password?
An App Password is a 16-character code that allows less secure apps (like Django) to access your Gmail account. You **cannot** use your regular Gmail password - you MUST use an App Password.

## Step-by-Step Instructions

### Step 1: Enable 2-Step Verification (Required First)

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** (left sidebar)
3. Under "How you sign in to Google", find **2-Step Verification**
4. If it's OFF, click on it and follow the steps to enable it
   - You'll need to verify your phone number
   - Google will send you a verification code
5. Once enabled, you'll see "2-Step Verification" is ON

### Step 2: Generate App Password

1. Go directly to: https://myaccount.google.com/apppasswords
   - Or: Google Account → Security → 2-Step Verification → App passwords (at the bottom)

2. You may be asked to sign in again

3. Under "Select app", choose **Mail**

4. Under "Select device", choose **Other (Custom name)**
   - Type: "Django App" or "Rudra Admin"

5. Click **Generate**

6. Google will show you a 16-character password like:
   ```
   abcd efgh ijkl mnop
   ```
   **IMPORTANT:** Copy this password immediately - you can only see it once!

7. The password will have spaces, but you can use it with or without spaces

### Step 3: Add to Settings

1. Open `backend/backend/settings.py`

2. Find these lines (around line 229-230):
   ```python
   EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
   ```

3. Replace with your Gmail address and the app password:
   ```python
   EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your-email@gmail.com')
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'abcdefghijklmnop')
   ```
   
   **Example:**
   ```python
   EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'john.doe@gmail.com')
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'abcd efgh ijkl mnop')
   ```
   
   Note: You can include or remove spaces from the app password - both work.

4. Save the file

5. Restart your Django server:
   ```bash
   # Stop server (Ctrl+C)
   python manage.py runserver
   ```

## Troubleshooting

**"2-Step Verification not available"**
- Make sure you're using a personal Gmail account (not a Google Workspace account)
- Some accounts may need to verify identity first

**"App passwords option not showing"**
- Make sure 2-Step Verification is enabled first
- Try refreshing the page
- Make sure you're signed in to the correct Google account

**"Authentication failed" error**
- Double-check you copied the app password correctly
- Make sure you're using the App Password, NOT your regular Gmail password
- Try regenerating a new app password

**"Less secure app access"**
- You don't need to enable "Less secure app access" - App Passwords replace this
- Just use the App Password you generated

## Quick Links

- **Google Account Security**: https://myaccount.google.com/security
- **2-Step Verification**: https://myaccount.google.com/signinoptions/two-step-verification
- **App Passwords**: https://myaccount.google.com/apppasswords

## Example Configuration

After getting your app password, your settings.py should look like:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'abcd efgh ijkl mnop'  # Your 16-character app password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

## Security Note

⚠️ **Important:**
- Never share your App Password
- Never commit it to version control (Git)
- If you suspect it's compromised, revoke it and generate a new one
- Each App Password can only be used for one app/device

