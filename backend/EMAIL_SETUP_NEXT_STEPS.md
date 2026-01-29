# Email Setup - Next Steps

You've installed the required libraries! Now follow these steps to configure email:

## Step 1: Create .env File

Create a file named `.env` in the `backend/` directory with the following content:

```env
EMAIL_HOST_USER=gurypavithra41@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password-here
```

**Important:** Replace `your-16-character-app-password-here` with your actual Gmail App Password.

## Step 2: Get Gmail App Password

1. Go to: **https://myaccount.google.com/apppasswords**
2. Make sure **2-Step Verification** is enabled on your Google account
3. Select:
   - **App:** Mail
   - **Device:** Other (Custom name) → Type "Django"
4. Click **Generate**
5. Copy the **16-character password** (it will look like: `abcd efgh ijkl mnop`)
6. **Remove ALL spaces** - the password should be exactly 16 characters with no spaces

## Step 3: Add Password to .env File

Open the `.env` file you created and paste your app password (without spaces):

```env
EMAIL_HOST_USER=gurypavithra41@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
```

## Step 4: Switch to SMTP Backend

In `backend/backend/settings.py`, change:

**FROM:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**TO:**
```python
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

## Step 5: Restart Django Server

```bash
# Stop the server (Ctrl+C or Ctrl+Break)
# Then restart:
python manage.py runserver
```

## Step 6: Test

Create a new user via your API - the email should now be sent to the recipient's inbox!

## Troubleshooting

- **Error 535 "Username and Password not accepted"**: 
  - App password is incorrect or expired
  - Make sure you removed all spaces from the password
  - Generate a new app password and try again

- **Email still printing to console**:
  - Make sure you switched to SMTP backend in settings.py
  - Restart the Django server after making changes

- **Can't find .env file**:
  - Make sure the file is named exactly `.env` (with the dot at the beginning)
  - Make sure it's in the `backend/` directory (same level as `manage.py`)

