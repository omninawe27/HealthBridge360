#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')

# Set environment variables for testing
os.environ['SECRET_KEY'] = 'test-key-for-debug'
os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
os.environ['DEBUG'] = 'True'
os.environ['SENDGRID_API_KEY'] = 'your-sendgrid-api-key'  # Placeholder for testing

django.setup()

from notifications.services import NotificationService
from django.contrib.auth import get_user_model
from orders.models import Prescription

User = get_user_model()

def test_email():
    try:
        print("Testing email functionality...")

        # Create or get test user with specific email
        test_email = 'omninawe27@gmail.com'
        user, created = User.objects.get_or_create(
            email=test_email,
            defaults={
                'username': 'test_user_omninawe27',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )

        if created:
            print(f"Created new test user: {user.email}")
        else:
            print(f"Using existing user: {user.email}")

        # Create a test prescription
        prescription = Prescription.objects.create(
            user=user,
            status='processing'
        )

        print(f"Created test prescription: {prescription.id}")

        # Test email sending
        print(f"Sending verification code email to {test_email}...")
        result = NotificationService.send_prescription_verification_code(prescription)

        print(f"Email send result: {result}")

        if result:
            print("Email sent successfully!")
            print(f"Verification code: {prescription.verification_code}")
        else:
            print("Email failed to send")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_email()
