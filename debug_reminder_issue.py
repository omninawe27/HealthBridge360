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
from datetime import time

# Check current time
now = timezone.localtime()
current_time = now.time().replace(second=0, microsecond=0)
print(f'Current time: {current_time}')

# Check existing reminders
reminders = Reminder.objects.all()
print(f'Total reminders: {reminders.count()}')
for r in reminders:
    print(f'Reminder: {r.medicine_name}, User: {r.user.email}, Time slot: {r.time_slot}, Specific time: {r.specific_time}, Active: {r.is_active}')

# Check default times
default_times = {
    'morning': time(7, 0),
    'afternoon': time(14, 0),
    'evening': time(18, 0),
    'night': time(21, 0)
}
print(f'Default times: {default_times}')

# Check which time slots are due
due_time_slots = []
for slot, default_time in default_times.items():
    if current_time == default_time:
        due_time_slots.append(slot)

print(f'Due time slots: {due_time_slots}')

# Check reminders that would be sent
specific_time_reminders = Reminder.objects.filter(
    is_active=True,
    specific_time__isnull=False,
    specific_time=current_time
)

time_slot_reminders = Reminder.objects.filter(
    is_active=True,
    specific_time__isnull=True,
    time_slot__in=due_time_slots
)

print(f'Specific time reminders: {specific_time_reminders.count()}')
print(f'Time slot reminders: {time_slot_reminders.count()}')

# Check Celery configuration
from healthkart360.settings import CELERY_BEAT_SCHEDULE
print(f'Celery Beat Schedule: {CELERY_BEAT_SCHEDULE}')
