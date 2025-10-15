from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from notifications.models import Notification
from reminders.models import Reminder
from core.utils import sanitize_cache_key
import logging
import random
import string
import time
import re

# Twilio for SMS removed

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def _sanitize_cache_key(key):
        """Sanitize cache key to remove invalid characters for memcached"""
        # Replace spaces and special characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', key)
        # Ensure it doesn't start with a number or contain consecutive underscores
        sanitized = re.sub(r'^[^a-zA-Z_]+', '', sanitized)
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized

    @staticmethod
    def _send_email_with_retry(email_message, max_retries=3, delay=1):
        """Send email with retry logic and better error handling"""
        logger.info(f"Attempting to send email to: {email_message.to}")
        for attempt in range(max_retries):
            try:
                result = email_message.send()
                if result > 0:
                    logger.info(f"Email sent successfully on attempt {attempt + 1} to {email_message.to}")
                    return True
                else:
                    logger.warning(f"Email send returned 0 on attempt {attempt + 1} to {email_message.to}")
            except Exception as e:
                error_msg = str(e).lower()
                logger.warning(f"Email send failed on attempt {attempt + 1}: {e}")
                if 'network is unreachable' in error_msg or 'connection refused' in error_msg:
                    logger.warning(f"Network error on attempt {attempt + 1}: {e}. Error type: {type(e).__name__}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                        continue
                elif 'authentication failed' in error_msg or '535' in error_msg:
                    logger.error(f"SMTP authentication failed: {e}")
                    return False  # Don't retry auth failures
                elif 'timeout' in error_msg:
                    logger.warning(f"SMTP timeout on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))
                        continue
                else:
                    logger.error(f"Unexpected email error on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))
                        continue
        logger.error(f"Failed to send email after {max_retries} attempts to {email_message.to}")
        return False
    @staticmethod
    def send_email_notification(reminder):
        """Send email notification for a reminder"""
        try:
            user = reminder.user
            subject = f"Medicine Reminder: {reminder.medicine_name}"

            # Plain text message for fallback
            message = f"""
            Hello {user.first_name},

            It's time to take your medicine!

            Medicine: {reminder.medicine_name}
            Time: {reminder.get_time_slot_display()}
            Notes: {reminder.notes or 'No additional notes'}

            Please take your medicine as prescribed.

            Best regards,
            HealthKart 360 Team
            """

            # HTML message
            html_message = render_to_string('notifications/reminder_email.html', {
                'user': user,
                'reminder': reminder,
                'medication_tracking_url': f"{settings.SITE_URL}/reminders/{reminder.id}/mark-taken/"
            })

            recipient_email = user.email

            # Send HTML email with retry
            email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
            email.attach_alternative(html_message, "text/html")
            success = NotificationService._send_email_with_retry(email)

            if success:
                # Create notification record
                notification = Notification.objects.create(
                    user=user,
                    reminder=reminder,
                    notification_type='email',
                    message=message,
                    status='sent',
                    sent_at=timezone.now()
                )
                logger.info(f"Email notification sent for reminder {reminder.id}")
                return True
            else:
                logger.error(f"Failed to send email notification for reminder {reminder.id}")
                return False
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False

    @staticmethod
    def send_prescription_verification_code(prescription):
        """Send verification code email for prescription"""
        try:
            import random
            import string

            user = prescription.user
            # Generate 6-digit verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            prescription.verification_code = verification_code
            prescription.save()

            subject = f"Prescription Verification Code - HealthBridge 360"
            recipient_email = user.email

            logger.info(f"Attempting to send verification code email to {recipient_email} for prescription {prescription.id}")
            logger.info(f"Verification code generated: {verification_code}")
            logger.info(f"Email backend: {settings.EMAIL_BACKEND}")
            logger.info(f"SMTP host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
            logger.info(f"From email: {settings.DEFAULT_FROM_EMAIL}")

            # Plain text message for fallback
            message = f"""
            Hello {user.first_name},

            Your prescription has been uploaded successfully!

            Verification Code: {verification_code}

            Please provide this code to the pharmacist to verify your prescription.

            If you did not upload this prescription, please contact our support team immediately.

            Best regards,
            HealthBridge 360 Team
            """

            # HTML message
            html_message = render_to_string('notifications/prescription_verification_email.html', {
                'user': user,
                'verification_code': verification_code,
                'support_url': f"{settings.SITE_URL}/support/"
            })

            # Send HTML email with retry
            email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
            email.attach_alternative(html_message, "text/html")
            success = NotificationService._send_email_with_retry(email)

            if success:
                logger.info(f"Verification code email sent successfully to {recipient_email} for prescription {prescription.id}")
                return True
            else:
                logger.warning(f"Failed to send verification code email to {recipient_email} for prescription {prescription.id}")
                return False
        except Exception as e:
            logger.error(f"Error sending verification code email: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    @staticmethod
    def send_order_status_notification(order):
        """Send order status update email"""
        try:
            user = order.user
            subject = f"Order Status Update - HealthKart 360"

            # Plain text message for fallback
            message = f"""
            Hello {user.first_name},

            Your order #{order.id} status has been updated!

            Current Status: {order.get_status_display()}
            Pharmacy: {order.pharmacy.name}
            Total Amount: ₹{order.total_amount}

            You can track your order status on our website.

            Best regards,
            HealthKart 360 Team
            """

            # HTML message
            # Fix: Replace order.id with order.id value in template context
            html_message = render_to_string('notifications/order_status_email.html', {
                'user': user,
                'order': order,
                'order_tracking_url': f"{settings.SITE_URL}/orders/{order.id}/"
            })

            recipient_email = user.email

            # Send HTML email with retry
            email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
            email.attach_alternative(html_message, "text/html")
            success = NotificationService._send_email_with_retry(email)

            if success:
                logger.info(f"Order status email sent for order {order.id}")
                return True
            else:
                logger.error(f"Failed to send order status email for order {order.id}")
                return False
        except Exception as e:
            logger.error(f"Error sending order status email: {e}")
            return False

    @staticmethod
    def send_order_notification_to_pharmacist(order):
        """Send new order notification email to pharmacist"""
        try:
            from users.models import User

            # Send to pharmacist - check both owner and pharmacists
            pharmacist_emails = []

            # Add pharmacy owner email if exists
            if hasattr(order.pharmacy, 'owner') and order.pharmacy.owner.email:
                pharmacist_emails.append(order.pharmacy.owner.email)
                logger.info(f"Added pharmacy owner email: {order.pharmacy.owner.email}")
            
            # Add emails of all users (pharmacists) associated with this pharmacy
            pharmacists = User.objects.filter(pharmacy=order.pharmacy, is_pharmacist=True)
            for pharmacist in pharmacists:
                if pharmacist.email and pharmacist.email not in pharmacist_emails:
                    pharmacist_emails.append(pharmacist.email)
                    logger.info(f"Added pharmacist user email: {pharmacist.email}")

            # Also add pharmacy email if it exists
            if order.pharmacy.email:
                pharmacist_emails.append(order.pharmacy.email)
                logger.info(f"Added pharmacy email: {order.pharmacy.email}")

            if not pharmacist_emails:
                logger.warning(f"No pharmacist emails found for pharmacy {order.pharmacy.id}")
                return False

            logger.info(f"Sending order notification to {len(pharmacist_emails)} email addresses: {pharmacist_emails}")

            user = order.user
            subject = f"New Order Received - HealthBridge 360"

            # Plain text message for fallback
            message = f"""
            Dear Pharmacist,

            A new order has been placed at your pharmacy!

            Order Details:
            Order ID: #{order.id}
            Customer: {user.first_name} {user.last_name}
            Customer Email: {user.email}
            Customer Phone: {user.phone_number}
            Order Status: {order.get_status_display()}
            Payment Method: {order.get_payment_method_display()}
            Delivery Method: {order.get_delivery_method_display()}

            Items Ordered:
            """
            for item in order.items.all():
                message += f"- {item.medicine.name} ({item.medicine.strength}) x {item.quantity} = ₹{item.price * item.quantity}\n"

            message += f"""

            Order Total: ₹{order.total_amount}
            Delivery Charges: ₹{order.delivery_charges}
            """

            if order.delivery_address:
                message += f"Delivery Address: {order.delivery_address}\n"

            if order.notes:
                message += f"Customer Notes: {order.notes}\n"

            message += f"""

            Please process this order and update the status accordingly.

            Best regards,
            HealthBridge 360 Team
            """

            # HTML message
            html_message = render_to_string('notifications/order_notification_pharmacist.html', {
                'order': order,
                'user': user,
                'order_detail_url': f"{settings.SITE_URL}/orders/pharmacy/{order.id}/",
                'update_status_url': f"{settings.SITE_URL}/orders/pharmacy/{order.id}/update-status/"
            })

            # Send HTML email to all pharmacists with retry
            success_count = 0
            for email_addr in pharmacist_emails:
                email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [email_addr])
                email.attach_alternative(html_message, "text/html")
                if NotificationService._send_email_with_retry(email):
                    success_count += 1
                else:
                    logger.error(f"Failed to send order notification to pharmacist {email_addr} for order {order.id}")

            if success_count > 0:
                logger.info(f"Order notification HTML email sent to {success_count}/{len(pharmacist_emails)} pharmacists for order {order.id}")
                return True
            else:
                logger.error(f"Failed to send order notification to any pharmacists for order {order.id}")
                return False
        except Exception as e:
            logger.error(f"Error sending order notification email to pharmacist: {e}")
            return False

    @staticmethod
    def send_order_verification_code(order_or_advance_order):
        """Send verification code email to pharmacist for order verification"""
        try:
            from users.models import User

            import random
            import string

            # Generate 6-digit verification code
            verification_code = ''.join(random.choices(string.digits, k=6))

            # Determine if it's an Order or AdvanceOrder
            if hasattr(order_or_advance_order, 'pharmacy'):
                # It's an Order
                order_obj = order_or_advance_order
                order_type = "Order"
                order_id = order_obj.id
                pharmacy = order_obj.pharmacy
                customer = order_obj.user
                items = order_obj.items.all()
            else:
                # It's an AdvanceOrder
                order_obj = order_or_advance_order
                order_type = "Advance Order"
                order_id = order_obj.id
                pharmacy = order_obj.pharmacy
                customer = order_obj.user
                items = order_obj.items.all()

            # Save verification code
            order_obj.verification_code = verification_code
            order_obj.save()

            # Send to pharmacist - check both owner and pharmacists
            pharmacist_emails = []

            # Add pharmacy owner email if exists
            if hasattr(pharmacy, 'owner') and pharmacy.owner.email:
                pharmacist_emails.append(pharmacy.owner.email)
                logger.info(f"Added pharmacy owner email: {pharmacy.owner.email}")
            
            # Add emails of all users (pharmacists) associated with this pharmacy
            pharmacists = User.objects.filter(pharmacy=pharmacy, is_pharmacist=True)
            for pharmacist in pharmacists:
                if pharmacist.email and pharmacist.email not in pharmacist_emails:
                    pharmacist_emails.append(pharmacist.email)
                    logger.info(f"Added pharmacist user email: {pharmacist.email}")
            
            # Also add pharmacy email if it exists
            if pharmacy.email:
                pharmacist_emails.append(pharmacy.email)
                logger.info(f"Added pharmacy email: {pharmacy.email}")

            if not pharmacist_emails:
                logger.warning(f"No pharmacist emails found for pharmacy {pharmacy.id}")
                return False

            logger.info(f"Sending verification code to {len(pharmacist_emails)} email addresses: {pharmacist_emails}")

            subject = f"{order_type} Verification Code - HealthBridge 360"

            # Plain text message for fallback
            message = f"""
            Dear Pharmacist,

            A new {order_type.lower()} has been placed and requires verification!

            {order_type} Details:
            {order_type} ID: #{order_id}
            Customer: {customer.first_name} {customer.last_name}
            Customer Email: {customer.email}
            Pharmacy: {pharmacy.name}

            Verification Code: {verification_code}

            Please use this verification code to verify and process the {order_type.lower()}.

            Best regards,
            HealthBridge 360 Team
            """

            # HTML message
            html_message = render_to_string('notifications/order_verification_pharmacist.html', {
                'order_type': order_type,
                'order_id': order_id,
                'pharmacy': pharmacy,
                'customer': customer,
                'verification_code': verification_code,
                'order_obj': order_obj,
                'items': items,
                'order_detail_url': f"{settings.SITE_URL}/orders/pharmacy/{order_id}/"
            })

            # Send HTML email to all pharmacists with retry
            success_count = 0
            for email_addr in pharmacist_emails:
                email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [email_addr])
                email.attach_alternative(html_message, "text/html")
                if NotificationService._send_email_with_retry(email):
                    success_count += 1
                else:
                    logger.error(f"Failed to send verification code to pharmacist {email_addr} for {order_type.lower()} {order_id}")

            if success_count > 0:
                logger.info(f"Verification code HTML email sent to {success_count}/{len(pharmacist_emails)} pharmacists for {order_type.lower()} {order_id}")
                return True
            else:
                logger.error(f"Failed to send verification code to any pharmacists for {order_type.lower()} {order_id}")
                return False
        except Exception as e:
            logger.error(f"Error sending verification code email to pharmacist: {e}")
            return False

    @staticmethod
    def send_customer_order_verification_code(order_or_advance_order):
        """Send verification code email to customer for order confirmation"""
        try:
            import random
            import string

            # Determine if it's an Order or AdvanceOrder
            if hasattr(order_or_advance_order, 'pharmacy'):
                # It's an Order
                order_obj = order_or_advance_order
                order_type = "Order"
                order_id = order_obj.id
                pharmacy = order_obj.pharmacy
                customer = order_obj.user
                items = order_obj.items.all()
            else:
                # It's an AdvanceOrder
                order_obj = order_or_advance_order
                order_type = "Advance Order"
                order_id = order_obj.id
                pharmacy = order_obj.pharmacy
                customer = order_obj.user
                items = order_obj.items.all()

            # Use existing verification code if available, otherwise generate new one
            if not order_obj.verification_code:
                verification_code = ''.join(random.choices(string.digits, k=6))
                order_obj.verification_code = verification_code
                order_obj.save()

            subject = f"Your {order_type} Verification Code - HealthKart 360"

            # Plain text message for fallback
            message = f"""
            Hello {customer.first_name},

            Thank you for placing your {order_type.lower()} with HealthBridge 360!

            {order_type} Details:
            {order_type} ID: #{order_id}
            Pharmacy: {pharmacy.name}
            Status: {order_obj.get_status_display()}

            Your Verification Code: {order_obj.verification_code}

            Please keep this verification code safe. You may need it for:
            - Order tracking and updates
            - Verification with the pharmacy
            - Customer support queries

            Order Summary:
            """

            # Add order items
            for item in items:
                if hasattr(item, 'medicine'):
                    # Regular order item
                    message += f"- {item.medicine.name} ({item.medicine.strength}) x {item.quantity} = ₹{item.price * item.quantity}\n"
                else:
                    # Advance order item
                    message += f"- {item.medicine_name} ({item.dosage}) x {item.quantity_requested}\n"

            if hasattr(order_obj, 'total_amount'):
                message += f"""

            Total Amount: ₹{order_obj.total_amount}
            """

            message += f"""

            You can track your order status on our website.

            If you have any questions, please contact our support team.

            Best regards,
            HealthBridge 360 Team
            """

            # HTML message
            html_message = render_to_string('notifications/customer_order_verification_email.html', {
                'customer': customer,
                'order_type': order_type,
                'order_id': order_id,
                'pharmacy': pharmacy,
                'order_obj': order_obj,
                'items': items,
                'order_tracking_url': f"{settings.SITE_URL}/orders/{order_id}/"
            })

            # Send HTML email with retry
            email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [customer.email])
            email.attach_alternative(html_message, "text/html")
            success = NotificationService._send_email_with_retry(email)

            if success:
                logger.info(f"Verification code email sent to customer for {order_type.lower()} {order_id}")
                return True
            else:
                logger.error(f"Failed to send verification code email to customer for {order_type.lower()} {order_id}")
                return False
        except Exception as e:
            logger.error(f"Error sending verification code email to customer: {e}")
            return False

    @staticmethod
    def send_advance_order_notification(advance_order):
        """Send advance order notification email to pharmacist"""
        try:
            from users.models import User
            pharmacy = advance_order.pharmacy
            pharmacist_emails = []

            # Add pharmacy owner email if exists
            if hasattr(pharmacy, 'owner') and pharmacy.owner.email:
                pharmacist_emails.append(pharmacy.owner.email)
                logger.info(f"Added pharmacy owner email for advance order: {pharmacy.owner.email}")

            # Add emails of all users (pharmacists) associated with this pharmacy
            pharmacists = User.objects.filter(pharmacy=pharmacy, is_pharmacist=True)
            for pharmacist in pharmacists:
                if pharmacist.email and pharmacist.email not in pharmacist_emails:
                    pharmacist_emails.append(pharmacist.email)
                    logger.info(f"Added pharmacist user email for advance order: {pharmacist.email}")

            if not pharmacist_emails:
                logger.warning(f"No pharmacist emails found for pharmacy {pharmacy.id} for advance order.")
                return False

            user = advance_order.user
            from datetime import timedelta
            collect_datetime = advance_order.created_at + timedelta(days=1)
            collect_date_str = collect_datetime.strftime('%Y-%m-%d')
            collect_time_str = collect_datetime.strftime('%H:%M')

            subject = f"New Advance Order - HealthBridge 360"

            # Plain text message for fallback
            message = f"""
            Dear Pharmacist,

            A new advance order has been placed!

            Order Details:
            Order ID: {advance_order.id}
            Customer: {user.first_name} {user.last_name}
            Customer Email: {user.email}
            Order Type: {advance_order.get_order_type_display()}
            Status: {advance_order.get_status_display()}

            Items:
            """
            for item in advance_order.items.all():
                message += f"- {item.medicine_name} ({item.dosage}) x {item.quantity_requested}\n"

            message += f"""

            Please take your order after 1 day on {collect_date_str} at {collect_time_str} for collection or delivery.

            Please process this advance order as soon as possible.

            Best regards,
            HealthBridge 360 Team
            """

            # HTML message
            html_message = render_to_string('notifications/advance_order_notification.html', {
                'advance_order': advance_order,
                'user': user,
                'collect_date_str': collect_date_str,
                'collect_time_str': collect_time_str,
                'order_detail_url': f"{settings.SITE_URL}/orders/advance/{advance_order.id}/",
                'update_status_url': f"{settings.SITE_URL}/orders/advance/{advance_order.id}/update-status/"
            })

            # Send HTML email with retry
            success_count = 0
            for email_addr in pharmacist_emails:
                email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [email_addr])
                email.attach_alternative(html_message, "text/html")
                if NotificationService._send_email_with_retry(email):
                    success_count += 1

            if success_count > 0:
                logger.info(f"Advance order notification sent to {success_count}/{len(pharmacist_emails)} pharmacists for advance order {advance_order.id}")
                return True
            else:
                logger.error(f"Failed to send advance order notification email for advance order {advance_order.id}")
                return False

        except Exception as e:
            logger.error(f"Error sending advance order notification email: {e}")
            return False

    @staticmethod
    def send_order_status_notification_to_pharmacist(order):
        """Send order status update email to pharmacist"""
        try:
            from users.models import User

            # Send to pharmacist - check both owner and pharmacists
            pharmacist_emails = []

            # Add pharmacy owner email if exists
            if hasattr(order.pharmacy, 'owner') and order.pharmacy.owner.email:
                pharmacist_emails.append(order.pharmacy.owner.email)
            
            # Add emails of all users (pharmacists) associated with this pharmacy
            pharmacists = User.objects.filter(pharmacy=order.pharmacy, is_pharmacist=True)
            for pharmacist in pharmacists:
                if pharmacist.email and pharmacist.email not in pharmacist_emails:
                    pharmacist_emails.append(pharmacist.email)

            if not pharmacist_emails:
                logger.warning(f"No pharmacist emails found for pharmacy {order.pharmacy.id}")
                return False

            user = order.user
            subject = f"Order Status Update - HealthBridge 360"

            # Plain text message for fallback
            message = f"""
            Dear Pharmacist,

            Order #{order.id} status has been updated!

            Order Details:
            Order ID: #{order.id}
            Customer: {user.first_name} {user.last_name}
            Customer Email: {user.email}
            Customer Phone: {user.phone_number}
            Current Status: {order.get_status_display()}
            Pharmacy: {order.pharmacy.name}
            Payment Method: {order.get_payment_method_display()}
            Delivery Method: {order.get_delivery_method_display()}

            Items Ordered:
            """
            for item in order.items.all():
                message += f"- {item.medicine.name} ({item.medicine.strength}) x {item.quantity} = ₹{item.price * item.quantity}\n"

            message += f"""

            Order Total: ₹{order.total_amount}
            Delivery Charges: ₹{order.delivery_charges}
            """

            if order.delivery_address:
                message += f"Delivery Address: {order.delivery_address}\n"

            if order.notes:
                message += f"Customer Notes: {order.notes}\n"

            message += f"""

            Please take appropriate action based on the new status.

            Best regards,
            HealthBridge 360 Team
            """

            # HTML message
            # Fix: Pass order and user as context variables correctly for template rendering
            html_message = render_to_string('notifications/order_status_pharmacist_email.html', {
                'order': order,
                'user': user,
                'order_detail_url': f"{settings.SITE_URL}/orders/pharmacy/{order.id}/",
                'update_status_url': f"{settings.SITE_URL}/orders/pharmacy/{order.id}/update-status/"
            })

            # Send HTML email to all pharmacists with retry
            success_count = 0
            for email_addr in pharmacist_emails:
                email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [email_addr])
                email.attach_alternative(html_message, "text/html")
                if NotificationService._send_email_with_retry(email):
                    success_count += 1
                else:
                    logger.error(f"Failed to send order status update to pharmacist {email_addr} for order {order.id}")

            if success_count > 0:
                logger.info(f"Order status update HTML email sent to {success_count}/{len(pharmacist_emails)} pharmacists for order {order.id}")
                return True
            else:
                logger.error(f"Failed to send order status update to any pharmacists for order {order.id}")
                return False
        except Exception as e:
            logger.error(f"Error sending order status notification email to pharmacist: {e}")
            return False

    @staticmethod
    def send_advance_order_status_notification(advance_order):
        """Send advance order status update email to customer"""
        try:
            user = advance_order.user
            subject = f"Advance Order Status Update - HealthBridge 360"

            # Plain text message for fallback
            message = f"""
            Hello {user.first_name},

            Your advance order #{advance_order.id} status has been updated!

            Current Status: {advance_order.get_status_display()}
            Pharmacy: {advance_order.pharmacy.name}
            Order Type: {advance_order.get_order_type_display()}

            Items Ordered:
            """
            for item in advance_order.items.all():
                message += f"- {item.medicine_name} ({item.dosage}) x {item.quantity_requested}\n"

            message += f"""

            You can track your advance order status on our website.

            Best regards,
            HealthBridge 360 Team
            """

            # HTML message
            html_message = render_to_string('notifications/advance_order_status_email.html', {
                'user': user,
                'advance_order': advance_order,
                'order_tracking_url': f"{settings.SITE_URL}/orders/advance/{advance_order.id}/"
            })

            recipient_email = user.email

            # Send HTML email with retry
            email = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
            email.attach_alternative(html_message, "text/html")
            success = NotificationService._send_email_with_retry(email)

            if success:
                logger.info(f"Advance order status email sent for advance order {advance_order.id}")
                return True
            else:
                logger.error(f"Failed to send advance order status email for advance order {advance_order.id}")
                return False
        except Exception as e:
            logger.error(f"Error sending advance order status email: {e}")
            return False
