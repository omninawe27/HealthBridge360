#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')
django.setup()

from notifications.services import NotificationService

def test_cache_key_sanitization():
    """Test cache key sanitization function"""
    print("Testing cache key sanitization...")

    # Test cases with invalid characters
    test_keys = [
        "user:email:test@example.com",
        "order:123:status",
        "pharmacy:ABC Pharmacy Ltd.",
        "medicine:Paracetamol 500mg",
        "cache:key:with spaces",
        "key-with-dashes",
        "key_with_underscores",
        "key.with.dots",
        "123starting_with_number",
        "key__with__double__underscores"
    ]

    for key in test_keys:
        sanitized = NotificationService._sanitize_cache_key(key)
        print(f"Original: '{key}' -> Sanitized: '{sanitized}'")

        # Verify sanitized key meets requirements
        assert sanitized.replace('_', '').replace('a', '').replace('z', '').isalnum() == False, f"Invalid characters in sanitized key: {sanitized}"
        assert not sanitized.startswith('_'), f"Sanitized key starts with underscore: {sanitized}"
        assert '__' not in sanitized, f"Double underscores in sanitized key: {sanitized}"

    print("Cache key sanitization tests passed!")

if __name__ == "__main__":
    test_cache_key_sanitization()
