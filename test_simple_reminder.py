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

from django.core.mail import EmailMultiAlternatives
from notifications.services import NotificationService
from users.models import User
from reminders.models import Reminder

# Get the test user and reminder
user = User.objects.get(email='omninawe27@gmail.com')
reminder = Reminder.objects.get(user=user, medicine_name='Test Medicine')

print(f'User: {user.email}')
print(f'Reminder: {reminder.medicine_name}')

# Try to send a simple email directly
print('Attempting to send simple reminder email...')
subject = f"Medicine Reminder: {reminder.medicine_name}"
message = f"""
Hello {user.first_name},

It's time to take your medicine!

Medicine: {reminder.medicine_name}
Time: {reminder.get_time_slot_display()}

Please take your medicine as prescribed.

Best regards,
HealthKart 360 Team
"""

recipient_email = user.email

# Send simple HTML email
email = EmailMultiAlternatives(subject, message, 'noreply@healthbridge360.sendgrid.net', [recipient_email])
email.attach_alternative(f"""
<html>
<body>
<h1>Medicine Reminder</h1>
<p>Hello {user.first_name},</p>
<p>It's time to take your medicine!</p>
<ul>
<li><strong>Medicine:</strong> {reminder.medicine_name}</li>
<li><strong>Time:</strong> {reminder.get_time_slot_display()}</li>
</ul>
<p>Please take your medicine as prescribed.</p>
<p>Best regards,<br/>HealthKart 360 Team</p>
</body>
</html>
""", "text/html")

success = NotificationService._send_email_with_retry(email)
print(f'Simple email result: {success}')
