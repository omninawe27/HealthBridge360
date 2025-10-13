from django.db import models
from pharmacy.models import Pharmacy

class Medicine(models.Model):
    MEDICINE_TYPES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream'),
        ('drops', 'Drops'),
    ]
    
    STOCK_STATUS = [
        ('in_stock', '🟢 In Stock'),    
        ('out_of_stock', '🔴 Out of Stock'),    
        ('expiring_soon', '⚠️ Expiring Soon'),  
    ]
    
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    medicine_type = models.CharField(max_length=20, choices=MEDICINE_TYPES)
    strength = models.CharField(max_length=50)  # e.g., "500mg", "10ml"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    expiry_date = models.DateField()
    batch_number = models.CharField(max_length=50)
    is_essential = models.BooleanField(default=False)
    is_prescription_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.brand}) - {self.pharmacy.name}"
    
    @property
    def stock_status(self):
        from django.utils import timezone
        from datetime import timedelta
        
        if self.quantity == 0:
            return 'out_of_stock'
        elif self.expiry_date <= timezone.now().date() + timedelta(days=30):
            return 'expiring_soon'
        else:
            return 'in_stock'
    
    @property
    def status_display(self):
        status_map = {
            'in_stock': '🟢 In Stock',
            'out_of_stock': '🔴 Out of Stock',
            'expiring_soon': '⚠️ Expiring Soon',
        }
        return status_map.get(self.stock_status, '🟢 In Stock')

class MedicineAlternative(models.Model):
    original_medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='alternatives')
    alternative_medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='alternative_for')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.original_medicine.name} -> {self.alternative_medicine.name}"
