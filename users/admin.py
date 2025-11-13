from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_pharmacist', 'is_staff', 'is_active')
    list_filter = ('is_pharmacist', 'is_staff', 'is_active', 'preferred_language', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'preferred_language', 'profile_picture', 'is_pharmacist', 'pharmacy')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'preferred_language', 'profile_picture', 'is_pharmacist', 'pharmacy')
        }),
    )
