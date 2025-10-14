#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')

# Set environment variables for production database
os.environ['SECRET_KEY'] = 'test-key-for-debug'
os.environ['DATABASE_URL'] = 'postgresql://healthkart360_user:UgRZhXcuQ8uGfYvGTe1zyR2UJXkBTpBQ@dpg-d3minpe3jp1c7380f10g-a/healthkart360'

django.setup()

from orders.models import Order
from pharmacy.models import Pharmacy
from users.models import User

# Check if there are any orders
orders = Order.objects.all()
print(f'Total orders: {orders.count()}')

# Check if there are any pharmacies
pharmacies = Pharmacy.objects.all()
print(f'Total pharmacies: {pharmacies.count()}')

# Check if there are any pharmacists
pharmacists = User.objects.filter(is_pharmacist=True)
print(f'Total pharmacists: {pharmacists.count()}')

# Check pharmacy emails
for pharmacy in pharmacies:
    print(f'Pharmacy: {pharmacy.name}, Email: {pharmacy.email}, Owner: {pharmacy.owner.email if pharmacy.owner else None}')

# Check pharmacist emails
for pharmacist in pharmacists:
    print(f'Pharmacist: {pharmacist.username}, Email: {pharmacist.email}, Pharmacy: {pharmacist.pharmacy.name if pharmacist.pharmacy else None}')
