from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('mr', 'Marathi'),
    ]
    
    phone_number = models.CharField(max_length=15, unique=True)
    preferred_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    is_pharmacist = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"
