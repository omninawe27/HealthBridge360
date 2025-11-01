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

# If SendGrid API key is not set, use console backend for testing
sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
if not sendgrid_api_key or sendgrid_api_key == 'your-sendgrid-api-key':
    os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.console.EmailBackend'
    print("WARNING: SendGrid API key not set. Using console email backend for testing.")
else:
    print("Using SendGrid backend.")

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
        print(f"SendGrid API Key configured: {'Yes' if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY else 'No'}")
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
