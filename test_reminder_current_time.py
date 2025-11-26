import os
import sys
import django

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')

django.setup()

from reminders.models import Reminder
from users.models import User
from django.utils import timezone
from notifications.services import NotificationService

# Get the test user
user = User.objects.get(email='omninawe27@gmail.com')

# Get current time
now = timezone.localtime()
current_time = now.time().replace(second=0, microsecond=0)

print(f'Current time: {current_time}')

# Create a reminder for the current time
reminder = Reminder.objects.create(
    user=user,
    medicine_name='Test Current Time Reminder',
    time_slot='',
    specific_time=current_time,
    is_active=True,
    notes='This is a test reminder for current time'
)

print(f'Created reminder: {reminder.medicine_name} at {reminder.specific_time}')

# Try to send the email
print('Attempting to send reminder email...')
result = NotificationService.send_email_notification(reminder)
print(f'Result: {result}')
