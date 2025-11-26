#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')

django.setup()

from django.core.mail import send_mail
from django.conf import settings

def send_test_reminder_email():
    subject = "Test Medicine Reminder"
    message = """
    Hello,

    This is a test reminder email for your medicine.

    Medicine: Test Medicine
    Time: Now
    Notes: This is a test email to verify the reminder system is working.

    Please take your medicine as prescribed.

    Best regards,
    HealthKart 360 Team
    """

    recipient_email = 'test@example.com'

    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )

        if result > 0:
            print(f"✓ Test email sent successfully to {recipient_email}")
            print(f"Email backend: {settings.EMAIL_BACKEND}")
        else:
            print(f"✗ Failed to send test email to {recipient_email}")

    except Exception as e:
        print(f"✗ Error sending test email: {e}")
        print(f"Email backend: {settings.EMAIL_BACKEND}")

if __name__ == '__main__':
    send_test_reminder_email()
