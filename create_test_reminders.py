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

def create_test_data():
    # Check existing users
    users = User.objects.all()
    print(f'Existing users: {list(users.values_list("email", flat=True))}')

    # Get first user or create one
    if users.exists():
        user = users.first()
        print(f'Using existing user: {user.email}')
    else:
        # Create user with unique phone
        import random
        phone = f'+1{random.randint(1000000000, 9999999999)}'
        user = User.objects.create(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            phone_number=phone
        )
        print(f'Created user: {user.email}')

    # Create reminders for each time slot
    time_slots = ['morning', 'afternoon', 'evening', 'night']
    for slot in time_slots:
        reminder, created = Reminder.objects.get_or_create(
            user=user,
            medicine_name=f'Medicine {slot}',
            time_slot=slot,
            defaults={
                'is_active': True,
                'notes': f'Take 1 tablet for {slot}',
                'alert_type': 'email',
                'send_email': True
            }
        )
        print(f'Reminder {slot}: {"created" if created else "exists"}')

    print(f'Total active reminders: {Reminder.objects.filter(is_active=True).count()}')

if __name__ == '__main__':
    create_test_data()
