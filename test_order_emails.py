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

django.setup()

from notifications.services import NotificationService
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem, Cart, CartItem
from medicines.models import Medicine
from pharmacy.models import Pharmacy
from decimal import Decimal

User = get_user_model()

def test_order_emails():
    try:
        print("Testing order email functionality...")

        # Create or get test user
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

        # Get or create a pharmacy
        pharmacy, created = Pharmacy.objects.get_or_create(
            name='Test Pharmacy',
            defaults={
                'address': 'Test Address',
                'phone': '1234567890',
                'email': 'pharmacy@test.com'
            }
        )

        # Get or create a medicine
        medicine, created = Medicine.objects.get_or_create(
            name='Test Medicine',
            pharmacy=pharmacy,
            defaults={
                'generic_name': 'Test Generic',
                'brand': 'Test Brand',
                'medicine_type': 'tablet',
                'strength': '100mg',
                'price': Decimal('10.00'),
                'quantity': 100,
                'expiry_date': '2025-12-31',
                'batch_number': 'TEST001',
                'is_essential': False,
                'is_prescription_required': False,
            }
        )

        # Create a test order
        order = Order.objects.create(
            user=user,
            pharmacy=pharmacy,
            status='pending',
            payment_method='cod',
            delivery_method='home_delivery',
            delivery_address='Test Delivery Address',
            notes='Test order notes'
        )

        # Create order item
        OrderItem.objects.create(
            order=order,
            medicine=medicine,
            quantity=2,
            price=medicine.price
        )

        # Calculate totals
        order.calculate_totals()

        print(f"Created test order: {order.id} with total amount: {order.total_amount}")

        # Test order status notification to customer
        print("\n1. Testing order status notification to customer...")
        result1 = NotificationService.send_order_status_notification(order)
        print(f"Order status notification to customer result: {result1}")

        # Test order notification to pharmacist
        print("\n2. Testing order notification to pharmacist...")
        result2 = NotificationService.send_order_notification_to_pharmacist(order)
        print(f"Order notification to pharmacist result: {result2}")

        # Test verification code to pharmacist
        print("\n3. Testing verification code to pharmacist...")
        result3 = NotificationService.send_order_verification_code(order)
        print(f"Verification code to pharmacist result: {result3}")

        # Test verification code to customer
        print("\n4. Testing verification code to customer...")
        result4 = NotificationService.send_customer_order_verification_code(order)
        print(f"Verification code to customer result: {result4}")

        print("
Order verification codes:")
        print(f"Pharmacist verification code: {order.verification_code}")
        print(f"Customer verification code: {order.customer_verification_code}")

        # Summary
        all_success = all([result1, result2, result3, result4])
        print(f"\nAll email sends successful: {all_success}")

        if all_success:
            print("✅ All order emails sent successfully!")
        else:
            print("❌ Some emails failed to send")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_order_emails()
