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
            default=30,
            help='Time window in minutes for checking due reminders (default: 30)',
        )

    def handle(self, *args, **options):
        window_minutes = options['window']

        # Send reminders for medicines due at the current time (within the specified window)
        now = timezone.localtime()
        now_time = now.time().replace(second=0, microsecond=0)

        # Default times for time slots
        default_times = {
            'morning': time(7, 0),
            'afternoon': time(14, 0),
            'evening': time(18, 0),
            'night': time(21, 0)
        }

        # Find time slots where current time is within the slot's time window
        due_time_slots = []
        window_delta = timedelta(minutes=window_minutes)
        for slot, default_time in default_times.items():
            # Make slot_datetime timezone-aware like 'now'
            slot_datetime = timezone.make_aware(datetime.combine(now.date(), default_time), timezone.get_current_timezone())
            window_start = slot_datetime - window_delta
            window_end = slot_datetime + window_delta

            # Handle midnight crossing
            if window_start.date() != window_end.date():
                # Window crosses midnight
                if now >= window_start or now <= window_end.replace(day=window_start.day + 1):
                    due_time_slots.append(slot)
            else:
                # Same day
                if window_start <= now <= window_end:
                    due_time_slots.append(slot)

        # Filter reminders in database query
        reminders = Reminder.objects.filter(
            is_active=True
        ).filter(
            Q(specific_time__isnull=True, time_slot__in=due_time_slots) |
            Q(specific_time__isnull=False)  # Include all specific time reminders for now
        ).select_related('user')

        total = reminders.count()
        sent = 0
        skipped = 0

        self.stdout.write(f"Checking {total} reminders for due time slots: {due_time_slots}...")

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
