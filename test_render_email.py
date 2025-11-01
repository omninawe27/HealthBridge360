#!/usr/bin/env python
"""
Test script to verify email functionality on Render deployment.
Run this on your Render instance to test email sending.
"""

import os
import django
from django.conf import settings
from django.core.mail import send_mail
from django.test.utils import get_runner

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')
django.setup()

def test_email_sending():
    """Test basic email sending functionality"""
    print("🧪 Testing Email Functionality on Render")
    print("=" * 50)

    # Check email configuration
    print(f"📧 Email Backend: {settings.EMAIL_BACKEND}")
    print(f"📧 From Email: {settings.DEFAULT_FROM_EMAIL}")
    print(f"📧 SendGrid API Key: {'SET' if os.getenv('SENDGRID_API_KEY') else 'NOT SET'}")
    print(f"📧 SendGrid Sandbox Mode: {getattr(settings, 'SENDGRID_SANDBOX_MODE_IN_DEBUG', 'NOT SET')}")

    # Test email sending
    try:
        subject = 'Render Email Test - HealthBridge360'
        message = '''
        This is a test email from your HealthBridge360 application on Render.

        If you receive this email, it means:
        ✅ SendGrid is configured correctly
        ✅ SendGrid API key is working
        ✅ Render environment variables are set
        ✅ Email service is operational

        Test performed at: ''' + str(django.utils.timezone.now())

        recipient = os.getenv('TEST_EMAIL_RECIPIENT', 'omninawe27@gmail.com')

        print(f"\n📤 Sending test email to: {recipient}")

        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False
        )

        if result == 1:
            print("✅ Email sent successfully!")
            return True
        else:
            print("❌ Email sending failed - no recipients")
            return False

    except Exception as e:
        print(f"❌ Email sending failed with error: {str(e)}")
        return False

def test_order_email_simulation():
    """Simulate order email sending like the actual application"""
    print("\n📦 Testing Order Email Simulation")
    print("=" * 40)

    try:
        from notifications.services import NotificationService
        from users.models import User
        from pharmacy.models import Pharmacy

        # Create mock user and pharmacy
        class MockUser:
            def __init__(self):
                self.email = os.getenv('TEST_EMAIL_RECIPIENT', 'omninawe27@gmail.com')
                self.first_name = 'Test'
                self.last_name = 'User'
                self.phone_number = '+91-9876543210'

        class MockPharmacy:
            def __init__(self):
                self.id = 1
                self.email = os.getenv('PHARMACIST_EMAIL', 'omninawe27@gmail.com')
                self.name = 'Test Pharmacy'

        # Create a mock order object with proper attributes
        class MockOrder:
            def __init__(self):
                self.id = 12345
                self.user = MockUser()
                self.pharmacy = MockPharmacy()
                self.total_amount = 150.00
                self.status = 'confirmed'
                self.delivery_charges = 50.00
                self.delivery_address = '123 Test Street, Test City'
                self.notes = 'Test order notes'
                self.created_at = django.utils.timezone.now()
                self.verification_code = '123456'

            def get_payment_method_display(self):
                return 'Online Payment'

            def get_delivery_method_display(self):
                return 'Home Delivery'

            def get_status_display(self):
                return 'Confirmed'

            @property
            def items(self):
                # Return empty queryset for mock
                from django.db.models import QuerySet
                return QuerySet()

        mock_order = MockOrder()

        # Test order confirmation email
        print("📧 Sending order confirmation email...")
        success = NotificationService.send_order_confirmation_email(mock_order)

        if success:
            print("✅ Order confirmation email sent successfully!")
        else:
            print("❌ Order confirmation email failed!")

        # Test pharmacist notification
        print("🏥 Sending pharmacist notification...")
        success = NotificationService.send_order_notification_to_pharmacist(mock_order)

        if success:
            print("✅ Pharmacist notification sent successfully!")
        else:
            print("❌ Pharmacist notification failed!")

        return True

    except Exception as e:
        print(f"❌ Order email simulation failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Render Email Testing Script")
    print("This script tests email functionality on your Render deployment")
    print()

    # Run tests
    email_test = test_email_sending()
    order_test = test_order_email_simulation()

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    if email_test:
        print("✅ Basic email sending: PASSED")
    else:
        print("❌ Basic email sending: FAILED")

    if order_test:
        print("✅ Order email simulation: PASSED")
    else:
        print("❌ Order email simulation: FAILED")

    if email_test and order_test:
        print("\n🎉 ALL TESTS PASSED! Email system is working correctly on Render.")
        print("\n📋 Next Steps:")
        print("1. Place a real order on your website")
        print("2. Check if you receive both customer and pharmacist emails")
        print("3. Verify email content and formatting")
    else:
        print("\n⚠️  SOME TESTS FAILED! Check your Render environment variables:")
        print("- SENDGRID_API_KEY")
        print("- Ensure SendGrid API key is valid and has full access")
        print("- Check Render logs for SendGrid API errors")
