from django.contrib import admin
from .models import Order, OrderItem, Prescription, PrescriptionMedicine, Cart, CartItem, MedicineReminder, AdvanceOrder, AdvanceOrderItem

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'processed_at']

@admin.register(PrescriptionMedicine)
class PrescriptionMedicineAdmin(admin.ModelAdmin):
    list_display = ['medicine_name', 'prescription', 'is_available', 'matched_medicine', 'quantity_required']
    list_filter = ['is_available', 'created_at']
    search_fields = ['medicine_name', 'generic_name', 'prescription__user__first_name']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_count', 'total_amount', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'medicine', 'quantity', 'total_price', 'added_at']
    list_filter = ['added_at']
    search_fields = ['medicine__name', 'cart__user__first_name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'pharmacy', 'status', 'payment_method', 'delivery_method', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_method', 'delivery_method', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'pharmacy__name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'pharmacy', 'prescription', 'status')
        }),
        ('Payment & Delivery', {
            'fields': ('payment_method', 'delivery_method', 'delivery_address', 'delivery_charges')
        }),
        ('Financial', {
            'fields': ('subtotal', 'total_amount')
        }),
        ('Additional', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'medicine', 'quantity', 'price', 'total_price']
    list_filter = ['order__status']
    search_fields = ['medicine__name', 'order__user__first_name']

@admin.register(MedicineReminder)
class MedicineReminderAdmin(admin.ModelAdmin):
    list_display = ['user', 'medicine_name', 'frequency', 'start_date', 'end_date', 'is_active']
    list_filter = ['frequency', 'is_active', 'start_date', 'end_date']
    search_fields = ['user__first_name', 'medicine_name']
    readonly_fields = ['created_at']

@admin.register(AdvanceOrder)
class AdvanceOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'prescription', 'status', 'created_at', 'estimated_delivery']
    list_filter = ['status', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'prescription__id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AdvanceOrderItem)
class AdvanceOrderItemAdmin(admin.ModelAdmin):
    list_display = ['advance_order', 'medicine_name', 'quantity_requested', 'estimated_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['medicine_name', 'advance_order__user__first_name']
