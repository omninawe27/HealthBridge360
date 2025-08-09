from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('register/', views.pharmacy_register, name='register'),
    path('dashboard/', views.pharmacy_dashboard, name='dashboard'),
    path('inventory/', views.manage_inventory, name='inventory'),
    path('profile/', views.pharmacy_profile, name='profile'),
]
