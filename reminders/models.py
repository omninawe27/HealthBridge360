from django.db import models
from django.contrib.auth import get_user_model
from medicines.models import Medicine
from datetime import datetime, time, timedelta

User = get_user_model()

class Reminder(models.Model):
    TIME_CHOICES = [
        ('morning', '🌅 Morning (6 AM - 12 PM)'),
        ('afternoon', '☀️ Afternoon (12 PM - 6 PM)'),
        ('evening', '🌆 Evening (6 PM - 9 PM)'),
        ('night', '🌙 Night (9 PM - 6 AM)'),
    ]
    
    ALERT_TYPES = [
        ('tone', '🔊 Tone'),
        ('vibrate', '📳 Vibrate'),
        ('visual', '👁️ Visual'),
        ('email', '📧 Email'),
        ('all', '🔔 All (Email + App)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=200)
    time_slot = models.CharField(max_length=20, choices=TIME_CHOICES)
    specific_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)  # e.g., "after lunch"
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='all')
    is_active = models.BooleanField(default=True)
    send_email = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    taken = models.BooleanField(default=False)
    taken_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.medicine_name} - {self.get_time_slot_display()} ({self.user.first_name})"
    
    class Meta:
        ordering = ['time_slot', 'specific_time']
    
    @property
    def notification_time(self):
        """Get the actual notification time based on time slot and specific time"""
        if self.specific_time:
            return self.specific_time
        else:
            # Default times for each slot
            default_times = {
                'morning': '07:00',
                'afternoon': '14:00', 
                'evening': '18:00',
                'night': '21:00'
            }
            time_str = default_times.get(self.time_slot, '07:00')
            hour, minute = map(int, time_str.split(':'))
            return time(hour, minute)
    
    def toggle_taken_status(self):
        """Toggle the taken status of the reminder"""
        self.taken = not self.taken
        if self.taken:
            self.taken_at = datetime.now()
        else:
            self.taken_at = None
        self.save()
