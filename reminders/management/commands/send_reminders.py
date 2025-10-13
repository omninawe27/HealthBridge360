from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta, datetime, time
from reminders.models import Reminder
from notifications.services import NotificationService


class Command(BaseCommand):
    help = 'Send due reminders to users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--window',
            type=int,
            default=5,
            help='Time window in minutes for checking due reminders (default: 5)',
        )

    def handle(self, *args, **options):
        window_minutes = options['window']

        # Send reminders for medicines due at the current time (within the specified window)
        now = timezone.localtime()
        now_time = now.time().replace(second=0, microsecond=0)

        # Calculate time window
        window_delta = timedelta(minutes=window_minutes)
        start_time = (datetime.combine(now.date(), now_time) - window_delta).time()
        end_time = (datetime.combine(now.date(), now_time) + window_delta).time()

        # Filter reminders in database query instead of loading all active reminders
        if start_time <= end_time:
            # Window doesn't cross midnight
            reminders = Reminder.objects.filter(
                is_active=True,
                specific_time__gte=start_time,
                specific_time__lte=end_time
            ).select_related('user')  # Optimize query by selecting related user
        else:
            # Window crosses midnight
            reminders = Reminder.objects.filter(
                is_active=True
            ).filter(
                Q(specific_time__gte=start_time) | Q(specific_time__lte=end_time)
            ).select_related('user')

        total = reminders.count()
        sent = 0
        skipped = 0

        self.stdout.write(f"Checking {total} reminders within time window {start_time} - {end_time}...")

        for reminder in reminders:
            # Send email notification
            try:
                NotificationService.send_email_notification(reminder)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Email sent for reminder: {reminder.medicine_name} "
                        f"({reminder.user.email}) at {reminder.specific_time}"
                    )
                )
                sent += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Failed to send email for reminder: {reminder.medicine_name} "
                        f"({reminder.user.email}) - Error: {str(e)}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSummary: Total reminders checked: {total}, "
                f"Emails sent: {sent}"
            )
        )
