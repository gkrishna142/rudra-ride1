# Email Configuration Guide

## Quick Setup

To enable real email delivery, you need to configure your email credentials in `backend/backend/settings.py`.

### Step 1: Get Your Email App Password

**For Gmail:**
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Go to https://myaccount.google.com/apppasswords
4. Select "Mail" and your device
5. Click "Generate"
6. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

**For Outlook/Hotmail:**
- Use your regular password or create an app password from Microsoft account settings

**For Yahoo:**
- Create an app password from Yahoo Account Security settings

### Step 2: Configure Settings

Open `backend/backend/settings.py` and find these lines (around line 229-230):

```python
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')  # e.g., 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')  # e.g., 'your-app-password'
```

**Option A: Direct Configuration (Quick but less secure)**
Replace the empty strings with your credentials:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'  # Your email address
EMAIL_HOST_PASSWORD = 'your-app-password'  # Your 16-character app password
```

**Option B: Environment Variables (Recommended for security)**
1. Create a `.env` file in the `backend` folder (or set system environment variables)
2. Add:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```
3. The settings.py already uses `os.environ.get()`, so it will automatically read from environment variables

### Step 3: Restart Django Server

After configuring, restart your Django development server:
```bash
# Stop the server (Ctrl+C)
# Then restart:
python manage.py runserver
```

### Step 4: Test

Create a new user via API - the email should now be sent to the recipient's inbox instead of printing to console.

## Troubleshooting

**Error: "Email configuration missing"**
- Make sure `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are not empty
- Restart the Django server after making changes

**Error: "Authentication failed"**
- For Gmail: Make sure you're using an App Password, not your regular password
- Check that 2-Step Verification is enabled
- Verify the app password is correct (no spaces)

**Error: "Connection refused"**
- Check your internet connection
- Verify `EMAIL_HOST` and `EMAIL_PORT` are correct for your email provider
- Some networks block SMTP ports - try a different network or use a VPN

**Emails still printing to console:**
- Make sure `EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'` is set
- Check that you restarted the server after making changes

## Email Provider Settings

| Provider | EMAIL_HOST | EMAIL_PORT | EMAIL_USE_TLS |
|----------|------------|------------|---------------|
| Gmail | smtp.gmail.com | 587 | True |
| Outlook/Hotmail | smtp-mail.outlook.com | 587 | True |
| Yahoo | smtp.mail.yahoo.com | 587 | True |
| Custom SMTP | Your SMTP server | Usually 587 or 465 | True/False |

## Security Note

⚠️ **Never commit email passwords to version control!**

- Use environment variables for production
- Add `.env` to `.gitignore`
- Use app passwords instead of regular passwords

