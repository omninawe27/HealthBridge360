#!/usr/bin/env python
"""
Automated Reminder Scheduler
This script runs continuously and checks for due reminders every minute.
It can be run as a background service or scheduled task.
"""

import os
import sys
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(level)s - %(message)s',
    handlers=[
        logging.FileHandler('reminder_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')

import django
django.setup()

from django.core.management import call_command
from django.utils import timezone


def run_reminder_check():
    """Run the reminder check command"""
    try:
        logger.info("Starting reminder check...")
        call_command('send_reminders', verbosity=1)
        logger.info("Reminder check completed successfully")
    except Exception as e:
        logger.error(f"Error during reminder check: {str(e)}")


def main():
    """Main scheduler loop"""
    logger.info("Starting Reminder Scheduler Service")
    logger.info("Press Ctrl+C to stop the service")

    try:
        while True:
            # Get current time
            now = timezone.localtime()
            current_second = now.second

            # Run reminder check every minute at :00 seconds
            if current_second == 0:
                logger.info(f"Running reminder check at {now.strftime('%Y-%m-%d %H:%M:%S')}")
                run_reminder_check()

            # Sleep for 1 second to check again
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Reminder Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error in scheduler: {str(e)}")
        raise


if __name__ == '__main__':
    main()
