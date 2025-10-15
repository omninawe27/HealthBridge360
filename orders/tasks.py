from celery import shared_task
from django.db import connections
import logging

from notifications.services import NotificationService
from .models import Order

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation_emails(self, order_id):
    """
    Celery task to send all order-related confirmation emails.
    """
    try:
        order = Order.objects.get(id=order_id)
        logger.info(f"[Celery Task] Sending emails for order {order_id}")

        # 1. Send order status notification to customer
        NotificationService.send_order_status_notification(order)

        # 2. Send new order notification to pharmacist
        NotificationService.send_order_notification_to_pharmacist(order)

        # 3. Send verification code to pharmacist
        NotificationService.send_order_verification_code(order)

        # 4. Send verification code to customer
        NotificationService.send_customer_order_verification_code(order)

        logger.info(f"[Celery Task] Successfully processed emails for order {order_id}")

    except Order.DoesNotExist:
        logger.error(f"[Celery Task] Order with ID {order_id} does not exist. Not retrying.")
    except Exception as exc:
        logger.error(f"[Celery Task] Error sending emails for order {order_id}: {exc}. Retrying...")
        raise self.retry(exc=exc)
    finally:
        connections.close_all()