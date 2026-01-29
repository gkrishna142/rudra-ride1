"""
Test email configuration and send a test email
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
import logging

# Configure logging to see errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_configuration():
    """Test email configuration and send a test email"""
    print("=" * 60)
    print("Email Configuration Test")
    print("=" * 60)
    
    # Check email backend
    print(f"\n1. Email Backend: {settings.EMAIL_BACKEND}")
    
    # Check if using console backend
    is_console = settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend'
    if is_console:
        print("   ⚠ Using console backend - emails will print to terminal, not send")
        print("   To send real emails, change to SMTP backend in settings.py")
        return False
    
    # Check SMTP settings
    print(f"\n2. SMTP Settings:")
    print(f"   HOST: {settings.EMAIL_HOST}")
    print(f"   PORT: {settings.EMAIL_PORT}")
    print(f"   USE_TLS: {settings.EMAIL_USE_TLS}")
    
    # Check credentials
    email_user = getattr(settings, 'EMAIL_HOST_USER', '')
    email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    
    print(f"\n3. Email Credentials:")
    print(f"   USER: {email_user if email_user else '❌ NOT SET (empty)'}")
    print(f"   PASSWORD: {'✅ SET' if email_password else '❌ NOT SET (empty)'}")
    
    if not email_user or not email_password:
        print("\n❌ ERROR: Email credentials are missing!")
        print("\nTo fix:")
        print("1. Open backend/backend/settings.py")
        print("2. Find EMAIL_HOST_USER and EMAIL_HOST_PASSWORD (around line 233-234)")
        print("3. Set them to your email and app password:")
        print("   EMAIL_HOST_USER = 'your-email@gmail.com'")
        print("   EMAIL_HOST_PASSWORD = 'your-app-password'")
        print("\nFor Gmail App Password: https://myaccount.google.com/apppasswords")
        return False
    
    # Test sending email
    print(f"\n4. Testing email send...")
    test_email = input("Enter your email address to send test email to: ").strip()
    
    if not test_email:
        print("❌ No email address provided. Skipping test send.")
        return False
    
    try:
        subject = 'Test Email from Rudra Admin'
        message = """
This is a test email from Rudra Admin.

If you received this email, your email configuration is working correctly!

Best regards,
Rudra Admin Team
        """
        from_email = settings.DEFAULT_FROM_EMAIL or email_user
        
        print(f"\nSending test email to: {test_email}")
        print(f"From: {from_email}")
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        print("\n✅ Test email sent successfully!")
        print(f"   Check your inbox at: {test_email}")
        print("   (Also check spam/junk folder if not in inbox)")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR sending email: {e}")
        print("\nCommon issues:")
        print("1. Wrong email/password - Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
        print("2. Gmail App Password - Make sure you're using App Password, not regular password")
        print("3. 2-Step Verification - Must be enabled for Gmail App Passwords")
        print("4. Network/Firewall - Check if port 587 is blocked")
        print("5. Wrong SMTP settings - Verify EMAIL_HOST and EMAIL_PORT")
        return False

if __name__ == '__main__':
    success = test_email_configuration()
    sys.exit(0 if success else 1)

