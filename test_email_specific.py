#!/usr/bin/env python
import os
import sys
import django
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup Django environment
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')

# Set environment variables for testing
os.environ['SECRET_KEY'] = 'test-key-for-debug'
os.environ['DEBUG'] = 'True'

# If email credentials are not set or are placeholders, use console backend for testing
email_user = os.getenv('EMAIL_HOST_USER')
email_pass = os.getenv('EMAIL_HOST_PASSWORD')
if not email_user or not email_pass or email_user == 'your-email@gmail.com' or email_pass == 'your-app-password':
    os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.console.EmailBackend'
    print("WARNING: Email credentials not set or are placeholders. Using console email backend for testing.")
else:
    print(f"Using SMTP email backend with user: {email_user}")

django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from notifications.services import NotificationService

def test_email_to_specific_address():
    try:
        print("Testing email functionality to omninawe27@gmail.com...")

        subject = "Test Email - HealthBridge 360"
        message = """
        Hello,

        This is a test email to verify the email sending functionality.

        Best regards,
        HealthBridge 360 Team
        """

        html_message = """
        <html>
        <body>
            <h2>Hello,</h2>
            <p>This is a test email to verify the email sending functionality.</p>
            <p>Best regards,<br>HealthBridge 360 Team</p>
        </body>
        </html>
        """

        recipient_email = "omninawe27@gmail.com"

        print(f"Sending test email to: {recipient_email}")
        print(f"Email backend: {settings.EMAIL_BACKEND}")
        print(f"SMTP host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        print(f"From email: {settings.DEFAULT_FROM_EMAIL}")

        # Send HTML email with retry
        email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
        email.attach_alternative(html_message, "text/html")
        success = NotificationService._send_email_with_retry(email)

        if success:
            print("Test email sent successfully!")
        else:
            print("Test email failed to send")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_email_to_specific_address()
