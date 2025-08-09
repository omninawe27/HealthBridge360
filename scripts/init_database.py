#!/usr/bin/env python
"""
Database initialization script for HealthKart 360
Creates sample data for testing and demonstration
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import User
from pharmacy.models import Pharmacy
from medicines.models import Medicine, MedicineAlternative
from orders.models import Order, OrderItem
from reminders.models import Reminder

User = get_user_model()

def create_sample_users():
    """Create sample users"""
    print("Creating sample users...")
    
    # Create regular users
    users_data = [
        {
            'username': 'john_doe',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone_number': '9876543210',
            'password': 'password123',
            'preferred_language': 'en'
        },
        {
            'username': 'jane_smith',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone_number': '9876543211',
            'password': 'password123',
            'preferred_language': 'hi'
        },
        {
            'username': 'raj_patel',
            'first_name': 'Raj',
            'last_name': 'Patel',
            'email': 'raj@example.com',
            'phone_number': '9876543212',
            'password': 'password123',
            'preferred_language': 'mr'
        }
    ]
    
    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            users.append(user)
            print(f"Created user: {user.first_name} {user.last_name}")
        else:
            users.append(user)
            print(f"User already exists: {user.first_name} {user.last_name}")
    
    return users

def create_sample_pharmacies():
    """Create sample pharmacies"""
    print("Creating sample pharmacies...")
    
    pharmacies_data = [
        {
            'name': 'City Medical Store',
            'address': '123 Main Street, Mumbai, Maharashtra',
            'phone_number': '022-12345678',
            'license_number': 'MUM001',
            'latitude': 19.0760,
            'longitude': 72.8777,
            'is_24x7': True,
            'owner_username': 'pharmacy1',
            'owner_first_name': 'Dr. Amit',
            'owner_last_name': 'Sharma',
            'owner_email': 'amit@citymedical.com',
            'owner_phone': '9876543201'
        },
        {
            'name': 'Health Plus Pharmacy',
            'address': '456 Park Avenue, Delhi, Delhi',
            'phone_number': '011-87654321',
            'license_number': 'DEL001',
            'latitude': 28.7041,
            'longitude': 77.1025,
            'is_24x7': False,
            'owner_username': 'pharmacy2',
            'owner_first_name': 'Dr. Priya',
            'owner_last_name': 'Verma',
            'owner_email': 'priya@healthplus.com',
            'owner_phone': '9876543202'
        },
        {
            'name': 'Rural Care Pharmacy',
            'address': '789 Village Road, Pune, Maharashtra',
            'phone_number': '020-11223344',
            'license_number': 'PUN001',
            'latitude': 18.5204,
            'longitude': 73.8567,
            'is_24x7': True,
            'owner_username': 'pharmacy3',
            'owner_first_name': 'Dr. Rajesh',
            'owner_last_name': 'Kumar',
            'owner_email': 'rajesh@ruralcare.com',
            'owner_phone': '9876543203'
        }
    ]
    
    pharmacies = []
    for pharm_data in pharmacies_data:
        # Create pharmacy owner
        owner, created = User.objects.get_or_create(
            username=pharm_data['owner_username'],
            defaults={
                'first_name': pharm_data['owner_first_name'],
                'last_name': pharm_data['owner_last_name'],
                'email': pharm_data['owner_email'],
                'phone_number': pharm_data['owner_phone'],
                'is_pharmacist': True
            }
        )
        if created:
            owner.set_password('password123')
            owner.save()
        
        # Create pharmacy
        pharmacy, created = Pharmacy.objects.get_or_create(
            license_number=pharm_data['license_number'],
            defaults={
                'owner': owner,
                'name': pharm_data['name'],
                'address': pharm_data['address'],
                'phone_number': pharm_data['phone_number'],
                'latitude': pharm_data['latitude'],
                'longitude': pharm_data['longitude'],
                'is_24x7': pharm_data['is_24x7']
            }
        )
        
        if created:
            pharmacies.append(pharmacy)
            print(f"Created pharmacy: {pharmacy.name}")
        else:
            pharmacies.append(pharmacy)
            print(f"Pharmacy already exists: {pharmacy.name}")
    
    return pharmacies

def create_sample_medicines(pharmacies):
    """Create sample medicines"""
    print("Creating sample medicines...")
    
    medicines_data = [
        # Diabetes medicines
        {
            'name': 'Metformin',
            'generic_name': 'Metformin Hydrochloride',
            'brand': 'Glycomet',
            'medicine_type': 'tablet',
            'strength': '500mg',
            'price': Decimal('15.00'),
            'quantity': 100,
            'is_essential': True,
            'is_prescription_required': True
        },
        {
            'name': 'Glimepiride',
            'generic_name': 'Glimepiride',
            'brand': 'Amaryl',
            'medicine_type': 'tablet',
            'strength': '1mg',
            'price': Decimal('25.00'),
            'quantity': 50,
            'is_essential': True,
            'is_prescription_required': True
        },
        {
            'name': 'Insulin',
            'generic_name': 'Insulin Regular',
            'brand': 'Humulin R',
            'medicine_type': 'injection',
            'strength': '10ml',
            'price': Decimal('450.00'),
            'quantity': 20,
            'is_essential': True,
            'is_prescription_required': True
        },
        
        # Asthma medicines
        {
            'name': 'Salbutamol',
            'generic_name': 'Salbutamol Sulphate',
            'brand': 'Asthalin',
            'medicine_type': 'inhaler',
            'strength': '100mcg',
            'price': Decimal('120.00'),
            'quantity': 30,
            'is_essential': True,
            'is_prescription_required': True
        },
        {
            'name': 'Budesonide',
            'generic_name': 'Budesonide',
            'brand': 'Pulmicort',
            'medicine_type': 'inhaler',
            'strength': '200mcg',
            'price': Decimal('180.00'),
            'quantity': 25,
            'is_essential': True,
            'is_prescription_required': True
        },
        
        # Pain relievers
        {
            'name': 'Paracetamol',
            'generic_name': 'Paracetamol',
            'brand': 'Crocin',
            'medicine_type': 'tablet',
            'strength': '500mg',
            'price': Decimal('5.00'),
            'quantity': 200,
            'is_essential': False,
            'is_prescription_required': False
        },
        {
            'name': 'Ibuprofen',
            'generic_name': 'Ibuprofen',
            'brand': 'Brufen',
            'medicine_type': 'tablet',
            'strength': '400mg',
            'price': Decimal('8.00'),
            'quantity': 150,
            'is_essential': False,
            'is_prescription_required': False
        },
        
        # Vitamins
        {
            'name': 'Vitamin D3',
            'generic_name': 'Cholecalciferol',
            'brand': 'Calcirol',
            'medicine_type': 'tablet',
            'strength': '1000IU',
            'price': Decimal('12.00'),
            'quantity': 80,
            'is_essential': False,
            'is_prescription_required': False
        },
        {
            'name': 'Vitamin B12',
            'generic_name': 'Cyanocobalamin',
            'brand': 'Neurobion',
            'medicine_type': 'tablet',
            'strength': '500mcg',
            'price': Decimal('18.00'),
            'quantity': 60,
            'is_essential': False,
            'is_prescription_required': False
        },
        
        # Antibiotics
        {
            'name': 'Amoxicillin',
            'generic_name': 'Amoxicillin Trihydrate',
            'brand': 'Novamox',
            'medicine_type': 'capsule',
            'strength': '500mg',
            'price': Decimal('35.00'),
            'quantity': 40,
            'is_essential': True,
            'is_prescription_required': True
        },
        
        # Syrups
        {
            'name': 'Cough Syrup',
            'generic_name': 'Dextromethorphan',
            'brand': 'Benadryl',
            'medicine_type': 'syrup',
            'strength': '100ml',
            'price': Decimal('85.00'),
            'quantity': 35,
            'is_essential': False,
            'is_prescription_required': False
        },
        {
            'name': 'Iron Syrup',
            'generic_name': 'Ferrous Sulphate',
            'brand': 'Feronia-XT',
            'medicine_type': 'syrup',
            'strength': '200ml',
            'price': Decimal('95.00'),
            'quantity': 25,
            'is_essential': False,
            'is_prescription_required': False
        }
    ]
    
    medicines = []
    for med_data in medicines_data:
        # Create medicine for each pharmacy
        for pharmacy in pharmacies:
            medicine, created = Medicine.objects.get_or_create(
                name=med_data['name'],
                pharmacy=pharmacy,
                defaults={
                    'generic_name': med_data['generic_name'],
                    'brand': med_data['brand'],
                    'medicine_type': med_data['medicine_type'],
                    'strength': med_data['strength'],
                    'price': med_data['price'],
                    'quantity': med_data['quantity'],
                    'expiry_date': date.today() + timedelta(days=365),
                    'batch_number': f'BATCH-{pharmacy.id}-{med_data["name"][:3].upper()}',
                    'is_essential': med_data['is_essential'],
                    'is_prescription_required': med_data['is_prescription_required']
                }
            )
            
            if created:
                medicines.append(medicine)
                print(f"Created medicine: {medicine.name} at {pharmacy.name}")
    
    return medicines

def create_sample_orders(users, pharmacies, medicines):
    """Create sample orders"""
    print("Creating sample orders...")
    
    # Create some sample orders
    orders_data = [
        {
            'user': users[0],
            'pharmacy': pharmacies[0],
            'status': 'delivered',
            'medicines': [
                {'medicine': medicines[0], 'quantity': 2, 'price': Decimal('15.00')},
                {'medicine': medicines[5], 'quantity': 1, 'price': Decimal('5.00')}
            ]
        },
        {
            'user': users[1],
            'pharmacy': pharmacies[1],
            'status': 'confirmed',
            'medicines': [
                {'medicine': medicines[3], 'quantity': 1, 'price': Decimal('120.00')},
                {'medicine': medicines[7], 'quantity': 1, 'price': Decimal('18.00')}
            ]
        },
        {
            'user': users[2],
            'pharmacy': pharmacies[2],
            'status': 'pending',
            'medicines': [
                {'medicine': medicines[2], 'quantity': 1, 'price': Decimal('450.00')}
            ]
        }
    ]
    
    for order_data in orders_data:
        # Create order
        order = Order.objects.create(
            user=order_data['user'],
            pharmacy=order_data['pharmacy'],
            status=order_data['status'],
            total_amount=sum(item['price'] * item['quantity'] for item in order_data['medicines'])
        )
        
        # Create order items
        for item_data in order_data['medicines']:
            OrderItem.objects.create(
                order=order,
                medicine=item_data['medicine'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
        
        print(f"Created order: {order.id} for {order.user.first_name}")

def create_sample_reminders(users):
    """Create sample reminders"""
    print("Creating sample reminders...")
    
    reminders_data = [
        {
            'user': users[0],
            'medicine_name': 'Metformin',
            'time_slot': 'morning',
            'notes': 'Take after breakfast'
        },
        {
            'user': users[0],
            'medicine_name': 'Metformin',
            'time_slot': 'evening',
            'notes': 'Take after dinner'
        },
        {
            'user': users[1],
            'medicine_name': 'Salbutamol',
            'time_slot': 'morning',
            'notes': 'Inhaler - use as needed'
        },
        {
            'user': users[2],
            'medicine_name': 'Insulin',
            'time_slot': 'morning',
            'notes': 'Before breakfast'
        },
        {
            'user': users[2],
            'medicine_name': 'Insulin',
            'time_slot': 'night',
            'notes': 'Before dinner'
        }
    ]
    
    for reminder_data in reminders_data:
        reminder = Reminder.objects.create(
            user=reminder_data['user'],
            medicine_name=reminder_data['medicine_name'],
            time_slot=reminder_data['time_slot'],
            notes=reminder_data['notes'],
            is_active=True
        )
        print(f"Created reminder: {reminder.medicine_name} for {reminder.user.first_name}")

def create_medicine_alternatives(medicines):
    """Create medicine alternatives"""
    print("Creating medicine alternatives...")
    
    # Group medicines by generic name
    generic_groups = {}
    for medicine in medicines:
        if medicine.generic_name not in generic_groups:
            generic_groups[medicine.generic_name] = []
        generic_groups[medicine.generic_name].append(medicine)
    
    # Create alternatives for medicines with same generic name
    for generic_name, meds in generic_groups.items():
        if len(meds) > 1:
            for i, medicine in enumerate(meds):
                for j, alternative in enumerate(meds):
                    if i != j:
                        MedicineAlternative.objects.get_or_create(
                            original_medicine=medicine,
                            alternative_medicine=alternative
                        )
    
    print("Medicine alternatives created")

def main():
    """Main function to initialize database"""
    print("Starting HealthKart 360 database initialization...")
    
    try:
        # Create sample data
        users = create_sample_users()
        pharmacies = create_sample_pharmacies()
        medicines = create_sample_medicines(pharmacies)
        create_sample_orders(users, pharmacies, medicines)
        create_sample_reminders(users)
        create_medicine_alternatives(medicines)
        
        print("\nDatabase initialization completed successfully!")
        print("\nSample data created:")
        print(f"- {len(users)} users")
        print(f"- {len(pharmacies)} pharmacies")
        print(f"- {len(medicines)} medicines")
        print(f"- Sample orders and reminders")
        
        print("\nDefault login credentials:")
        print("Regular users: username/password123")
        print("Pharmacy owners: pharmacy1/password123, pharmacy2/password123, pharmacy3/password123")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
