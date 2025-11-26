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

from notifications.services import NotificationService
from users.models import User
from reminders.models import Reminder

# Get the test user and reminder
user = User.objects.get(email='omninawe27@gmail.com')
reminder = Reminder.objects.get(user=user, medicine_name='Test Medicine')

print(f'User: {user.email}')
print(f'Reminder: {reminder.medicine_name}')
print(f'Reminder time slot: {reminder.time_slot}')
print(f'Reminder active: {reminder.is_active}')

# Try to send the email
print('Attempting to send reminder email...')
result = NotificationService.send_email_notification(reminder)
print(f'Result: {result}')
