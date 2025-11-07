from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_reminder_emails(self):
    """
    Celery task to send reminder emails every minute.
    This task is scheduled via Celery Beat to run automatically.
    """
    try:
        logger.info("[Celery Beat] Starting scheduled reminder email check")

        # Call the Django management command
        call_command('send_reminders', verbosity=1)

        logger.info("[Celery Beat] Completed scheduled reminder email check")

    except Exception as exc:
        logger.error(f"[Celery Beat] Error in scheduled reminder check: {exc}")
        raise self.retry(exc=exc)
