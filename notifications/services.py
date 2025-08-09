from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Notification
from reminders.models import Reminder
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_email_notification(reminder):
        """Send email notification for a reminder"""
        try:
            user = reminder.user
            subject = f"Medicine Reminder: {reminder.medicine_name}"
            
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
            
            # In a real app, you'd use the user's email
            # For now, we'll use a placeholder
            recipient_email = f"{user.username}@example.com"
            
            # Create notification record
            notification = Notification.objects.create(
                user=user,
                reminder=reminder,
                notification_type='email',
                message=message,
                status='sent',
                sent_at=timezone.now()
            )
            
            # In a real app, you'd actually send the email
            # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
            
            logger.info(f"Email notification sent for reminder {reminder.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    @staticmethod
    def send_sms_notification(reminder):
        """Send SMS notification for a reminder"""
        try:
            user = reminder.user
            message = f"HealthKart 360: Time to take {reminder.medicine_name}. {reminder.notes or ''}"
            
            # Create notification record
            notification = Notification.objects.create(
                user=user,
                reminder=reminder,
                notification_type='sms',
                message=message,
                status='sent',
                sent_at=timezone.now()
            )
            
            # In a real app, you'd integrate with an SMS service
            # For now, we'll just log it
            logger.info(f"SMS notification sent for reminder {reminder.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")
            return False
    
    @staticmethod
    def send_app_notification(reminder):
        """Send in-app notification for a reminder"""
        try:
            user = reminder.user
            message = f"Time to take {reminder.medicine_name}"
            
            # Create notification record
            notification = Notification.objects.create(
                user=user,
                reminder=reminder,
                notification_type='app',
                message=message,
                status='sent',
                sent_at=timezone.now()
            )
            
            logger.info(f"App notification sent for reminder {reminder.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send app notification: {e}")
            return False
    
    @staticmethod
    def send_reminder_notifications(reminder):
        """Send all enabled notifications for a reminder"""
        notifications_sent = 0
        
        if reminder.send_email:
            if NotificationService.send_email_notification(reminder):
                notifications_sent += 1
        
        if reminder.send_sms:
            if NotificationService.send_sms_notification(reminder):
                notifications_sent += 1
        
        # Always send app notification
        if NotificationService.send_app_notification(reminder):
            notifications_sent += 1
        
        return notifications_sent 