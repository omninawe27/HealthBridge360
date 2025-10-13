#!/usr/bin/env python
"""
Script to add database indexes for performance optimization.
Run this script to create indexes on frequently queried fields.
"""

import os
import sys
import django

# Setup Django
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def create_indexes():
    """Create performance indexes"""

    indexes = [
        # Reminder indexes
        ("idx_reminder_active_time", "reminders_reminder", "is_active, specific_time"),
        ("idx_reminder_active", "reminders_reminder", "is_active"),

        # Order indexes
        ("idx_order_user_status", "orders_order", "user_id, status"),
        ("idx_order_pharmacy_status", "orders_order", "pharmacy_id, status"),
        ("idx_order_created_at", "orders_order", "created_at"),
        ("idx_order_user_created", "orders_order", "user_id, created_at"),

        # Pharmacy indexes
        ("idx_pharmacy_active_24x7", "pharmacy_pharmacy", "is_active, is_24x7"),
        ("idx_pharmacy_active", "pharmacy_pharmacy", "is_active"),

        # Medicine indexes
        ("idx_medicine_pharmacy_quantity", "medicines_medicine", "pharmacy_id, quantity"),
        ("idx_medicine_essential", "medicines_medicine", "is_essential"),
        ("idx_medicine_quantity", "medicines_medicine", "quantity"),

        # Prescription indexes
        ("idx_prescription_user_status", "orders_prescription", "user_id, status"),
        ("idx_prescription_created", "orders_prescription", "created_at"),

        # Cart indexes
        ("idx_cart_user", "orders_cart", "user_id"),
    ]

    with connection.cursor() as cursor:
        for index_name, table_name, columns in indexes:
            try:
                # Check if index exists
                cursor.execute(f"SHOW INDEX FROM {table_name} WHERE Key_name = '{index_name}'")
                if cursor.fetchone():
                    print(f"○ Index {index_name} already exists on {table_name}")
                    continue

                # Create index
                cursor.execute(f"CREATE INDEX {index_name} ON {table_name} ({columns})")
                print(f"✓ Created index: {index_name} on {table_name}")
            except Exception as e:
                print(f"✗ Failed to create index {index_name}: {e}")

if __name__ == '__main__':
    print("Adding performance indexes...")
    create_indexes()
    print("Index creation completed!")
