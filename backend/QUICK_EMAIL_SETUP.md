# Quick Email Setup - 3 Steps

## Step 1: Get Gmail App Password
1. Go to: **https://myaccount.google.com/apppasswords**
2. Select **"Mail"** → **"Other (Custom name)"** → Type **"Django"**
3. Click **"Generate"**
4. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

## Step 2: Add to settings.py
Open `backend/backend/settings.py` and find lines **233-234**:

**Replace:**
```python
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your-app-password')
```

**With your actual values:**
```python
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'john.doe@gmail.com')  # Your Gmail
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'abcdefghijklmnop')  # Your app password
```

## Step 3: Restart Server
```bash
# Stop server (Ctrl+C)
python manage.py runserver
```

## Test
```bash
python test_email.py
```

✅ Done! Emails will now be sent to recipients.

