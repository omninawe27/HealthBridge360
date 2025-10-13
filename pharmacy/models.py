from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Pharmacy(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owned_pharmacy')
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone_number = models.CharField(max_length=10)
    email = models.EmailField(blank=True, null=True)
    license_number = models.CharField(max_length=50, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_24x7 = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Pharmacies"
