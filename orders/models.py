from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from pharmacy.models import Pharmacy
import uuid
from medicines.models import Medicine

User = get_user_model()

class Prescription(models.Model):
    STATUS_CHOICES = [
        ('uploaded', _('Uploaded')),
        ('processing', _('Processing')),
        ('processed', _('Processed')),
        ('verified', _('Verified')),
        ('failed', _('Failed')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='prescriptions/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    extracted_text = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Prescription #{self.id} - {self.user.first_name}"

class PrescriptionMedicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    medicine_name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    dosage = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    quantity_required = models.IntegerField(default=1)
    is_available = models.BooleanField(default=False)
    matched_medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.medicine_name} - {self.prescription.id}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart - {self.user.first_name}"
    
    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def item_count(self):
        return self.items.count()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    is_advance_order = models.BooleanField(default=False, help_text="Whether this cart item is for an advance order")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'medicine')
    
    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.quantity * self.medicine.price

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('preparing', _('Preparing')),
        ('ready', _('Ready for Pickup')),
        ('out_for_delivery', _('Out for Delivery')),
        ('delivered', _('Delivered')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    PAYMENT_METHODS = [
        ('cod', _('Cash on Delivery')),
        ('online', _('Online Payment')),
        ('card', _('Card Payment')),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    ]

    DELIVERY_METHODS = [
        ('pickup', _('Store Pickup')),
        ('home_delivery', _('Home Delivery')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS, default='pickup')
    delivery_address = models.TextField(blank=True)
    delivery_email = models.EmailField(blank=True, help_text="Email for delivery notifications (optional)")
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_advance_order = models.BooleanField(default=False, help_text="Whether this is an advance order")
    advance_order_type = models.CharField(max_length=20, choices=[('prescription', 'Prescription Order'), ('restock', 'Inventory Restock')], blank=True, null=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True, help_text="Verification code for pharmacist")
    is_verified = models.BooleanField(default=False, help_text="Whether the order has been verified by pharmacist")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.first_name} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Only calculate totals if the order already has a primary key (i.e., it's been saved)
        if self.pk:
            self.subtotal = sum(item.total_price for item in self.items.all())
            self.total_amount = self.subtotal + self.delivery_charges
        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculate and update order totals"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.total_amount = self.subtotal + self.delivery_charges
        self.save(update_fields=['subtotal', 'total_amount'])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    prescription_medicine = models.ForeignKey(PrescriptionMedicine, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.quantity * self.price

class MedicineReminder(models.Model):
    FREQUENCY_CHOICES = [
        ('once_daily', _('Once Daily')),
        ('twice_daily', _('Twice Daily')),
        ('thrice_daily', _('Thrice Daily')),
        ('before_meals', _('Before Meals')),
        ('after_meals', _('After Meals')),
        ('custom', _('Custom')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    custom_schedule = models.TextField(blank=True)  # JSON field for custom schedules
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.medicine_name} - {self.user.first_name}"

class AdvanceOrder(models.Model):
    ORDER_TYPE_CHOICES = [
        ('prescription', _('Prescription Order')),
        ('restock', _('Inventory Restock')),
    ]

    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('ordered', _('Ordered from Supplier')),
        ('received', _('Received')),
        ('ready', _('Ready for Customer')),
        ('cancelled', _('Cancelled')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True, blank=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, null=True, blank=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='prescription')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_delivery = models.DateField(null=True, blank=True)
    supplier_name = models.CharField(max_length=200, blank=True, help_text="Supplier name for restock orders")
    supplier_contact = models.CharField(max_length=200, blank=True, help_text="Supplier contact for restock orders")
    notes = models.TextField(blank=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True, help_text="Verification code for pharmacist")
    is_verified = models.BooleanField(default=False, help_text="Whether the advance order has been verified by pharmacist")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.order_type == 'restock':
            return f"Restock Order #{self.id} - {self.pharmacy.name}"
        return f"Advance Order #{self.id} - {self.user.first_name}"

class AdvanceOrderItem(models.Model):
    advance_order = models.ForeignKey(AdvanceOrder, on_delete=models.CASCADE, related_name='items')
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    quantity_requested = models.IntegerField()
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.medicine_name} x {self.quantity_requested}"
