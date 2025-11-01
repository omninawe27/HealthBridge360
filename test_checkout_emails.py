#!/usr/bin/env python
"""
Test script to verify checkout email functionality
"""
import os
import sys
import django
from django.conf import settings

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem, Cart, CartItem
from medicines.models import Medicine
from pharmacy.models import Pharmacy
from notifications.services import NotificationService

def test_checkout_emails():
    """Test the checkout email functionality"""
    print("Testing checkout email functionality...")

    # Get or create test user
    User = get_user_model()
    user, created = User.objects.get_or_create(
        email='omninawe27@gmail.com',
        defaults={
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    print(f"Using {'existing' if not created else 'new'} user: {user.email}")

    # Get or create test pharmacy
    pharmacy, created = Pharmacy.objects.get_or_create(
        name='Test Pharmacy',
        defaults={
            'email': 'pharmacy@test.com',
            'phone': '1234567890',
            'address': 'Test Address',
            'license_number': 'TEST123',
        }
    )
    print(f"Using {'existing' if not created else 'new'} pharmacy: {pharmacy.name}")

    # Get or create test medicine
    medicine, created = Medicine.objects.get_or_create(
        name='Test Medicine',
        pharmacy=pharmacy,
        defaults={
            'generic_name': 'Test Generic',
            'brand': 'Test Brand',
            'medicine_type': 'tablet',
            'strength': '100mg',
            'price': 10.00,
            'quantity': 100,
            'expiry_date': '2025-12-31',
            'batch_number': 'TEST001',
            'is_essential': False,
            'is_prescription_required': False,
        }
    )
    print(f"Using {'existing' if not created else 'new'} medicine: {medicine.name}")

    # Create test order
    order = Order.objects.create(
        user=user,
        pharmacy=pharmacy,
        status='pending',
        payment_method='cod',
        delivery_method='home_delivery',
        delivery_address='Test Delivery Address',
        notes='Test order notes',
        payment_status='pending',
        delivery_charges=50.00,
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

    # Test the synchronous email sending from checkout
    print("\n1. Testing synchronous email sending from checkout...")

    try:
        # Send order status notification (customer)
        result1 = NotificationService.send_order_status_notification(order)
        print(f"Order status notification to customer result: {result1}")

        # Send order notification to pharmacist
        result2 = NotificationService.send_order_notification_to_pharmacist(order)
        print(f"Order notification to pharmacist result: {result2}")

        # Send verification code to pharmacist
        result3 = NotificationService.send_order_verification_code(order)
        print(f"Verification code to pharmacist result: {result3}")

        # Send verification code to customer
        result4 = NotificationService.send_customer_order_verification_code(order)
        print(f"Verification code to customer result: {result4}")

        all_successful = all([result1, result2, result3, result4])
        print(f"\nAll email sends successful: {all_successful}")

        if all_successful:
            print("✅ Checkout email functionality working correctly!")
        else:
            print("❌ Some emails failed to send")

    except Exception as e:
        print(f"❌ Error during email testing: {str(e)}")
        import traceback
        traceback.print_exc()

    # Clean up
    order.delete()
    print("\nTest completed and cleaned up.")

if __name__ == '__main__':
    test_checkout_emails()
