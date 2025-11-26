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

from users.models import User
from reminders.models import Reminder
from notifications.services import NotificationService

def send_test_reminder_email():
    # Get or create test user
    user, created = User.objects.get_or_create(
        email='omninawe27@gmail.com',
        defaults={
            'username': 'testuser_reminder',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+1234567890'
        }
    )
    print(f"User {'created' if created else 'exists'}: {user.email}")

    # Create a test reminder
    reminder, created = Reminder.objects.get_or_create(
        user=user,
        medicine_name='Test Medicine',
        time_slot='morning',
        defaults={
            'is_active': True,
            'notes': 'This is a test reminder email',
            'alert_type': 'email',
            'send_email': True
        }
    )
    print(f"Reminder {'created' if created else 'exists'}: {reminder.medicine_name}")

    # Send email using the notification service
    try:
        success = NotificationService.send_email_notification(reminder)
        if success:
            print("✓ Test reminder email sent successfully")
        else:
            print("✗ Failed to send test reminder email")
    except Exception as e:
        print(f"✗ Error sending test reminder email: {e}")

if __name__ == '__main__':
    send_test_reminder_email()
