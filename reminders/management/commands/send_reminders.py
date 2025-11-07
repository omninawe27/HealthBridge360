from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, time
from reminders.models import Reminder
from notifications.services import NotificationService


class Command(BaseCommand):
    help = 'Send due reminders to users at exact scheduled times'

    def handle(self, *args, **options):
        # Send reminders for medicines due at the current exact time
        now = timezone.localtime()
        current_time = now.time().replace(second=0, microsecond=0)

        # Default times for time slots
        default_times = {
            'morning': time(7, 0),
            'afternoon': time(14, 0),
            'evening': time(18, 0),
            'night': time(21, 0)
        }

        # Find time slots where current time exactly matches the slot's default time
        due_time_slots = []
        for slot, default_time in default_times.items():
            if current_time == default_time:
                due_time_slots.append(slot)

        # Filter reminders in database query
        # For specific time reminders, check if they match the current exact time
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

        reminders = (time_slot_reminders | specific_time_reminders).select_related('user').distinct()

        total = reminders.count()
        sent = 0
        skipped = 0

        self.stdout.write(f"Checking {total} reminders for due time slots: {due_time_slots}...")

        for reminder in reminders:
            # Send email notification
            try:
                success = NotificationService.send_email_notification(reminder)
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Email sent for reminder: {reminder.medicine_name} "
                            f"({reminder.user.email}) at {reminder.specific_time}"
                        )
                    )
                    sent += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Failed to send email for reminder: {reminder.medicine_name} "
                            f"({reminder.user.email}) - Email service returned failure"
                        )
                    )
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
