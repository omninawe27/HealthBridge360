import re
import json
from typing import List, Dict, Optional
from django.db.models import Q
from medicines.models import Medicine
from .models import Prescription, PrescriptionMedicine

class PrescriptionProcessor:
    """Service class for processing prescription images and extracting medicine information"""
    
    def __init__(self, prescription: Prescription):
        self.prescription = prescription
    
    def extract_medicines_from_text(self, text: str) -> List[Dict]:
        """
        Extract medicine information from prescription text
        This is a simplified version - in production, you'd use OCR + NLP
        """
        medicines = []

        # Common medicine patterns
        medicine_patterns = [
            r'(\w+(?:\s+\w+)*)\s*(\d+mg|\d+ml|\d+g)\s*(?:tablet|capsule|syrup|injection|cream|drops)?\s*(?:(\d+)\s*(?:times|x)\s*(?:daily|per day|a day))?',
            r'(\w+(?:\s+\w+)*)\s*(?:(\d+mg|\d+ml|\d+g))\s*(?:(\d+)\s*(?:times|x)\s*(?:daily|per day|a day))?',
            r'(\w+(?:\s+\w+)*)\s*(?:(\d+)\s*(?:times|x)\s*(?:daily|per day|a day))?',
        ]

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            for pattern in medicine_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    medicine_name = groups[0].strip() if groups[0] else ''
                    dosage = groups[1] if len(groups) > 1 and groups[1] else ''
                    frequency = groups[2] if len(groups) > 2 and groups[2] else ''

                    if medicine_name and len(medicine_name) > 2:
                        medicines.append({
                            'name': medicine_name,
                            'dosage': dosage,
                            'frequency': frequency,
                            'quantity_required': self._calculate_quantity(frequency)
                        })
                    break  # Stop after first match for this line

        return medicines
    
    def _calculate_quantity(self, frequency: str) -> int:
        """Calculate required quantity based on frequency"""
        if not frequency:
            return 1
        
        # Extract number from frequency
        numbers = re.findall(r'\d+', frequency)
        if numbers:
            return int(numbers[0]) * 7  # Assume 1 week supply
        return 1
    
    def match_medicines(self, extracted_medicines: List[Dict]) -> List[PrescriptionMedicine]:
        """Match extracted medicines with available medicines in database"""
        prescription_medicines = []
        
        for medicine_info in extracted_medicines:
            # Search for exact match first
            matched_medicine = self._find_exact_match(medicine_info['name'])
            
            # If no exact match, search for similar medicines
            if not matched_medicine:
                matched_medicine = self._find_similar_medicine(medicine_info['name'])
            
            # Create PrescriptionMedicine object
            prescription_medicine = PrescriptionMedicine.objects.create(
                prescription=self.prescription,
                medicine_name=medicine_info['name'],
                dosage=medicine_info.get('dosage', ''),
                frequency=medicine_info.get('frequency', ''),
                quantity_required=medicine_info.get('quantity_required', 1),
                is_available=matched_medicine is not None,
                matched_medicine=matched_medicine
            )
            
            prescription_medicines.append(prescription_medicine)
        
        return prescription_medicines
    
    def _find_exact_match(self, medicine_name: str) -> Optional[Medicine]:
        """Find exact match for medicine name"""
        try:
            return Medicine.objects.get(
                Q(name__iexact=medicine_name) | 
                Q(generic_name__iexact=medicine_name),
                quantity__gt=0
            )
        except Medicine.DoesNotExist:
            return None
    
    def _find_similar_medicine(self, medicine_name: str) -> Optional[Medicine]:
        """Find similar medicine using improved fuzzy matching"""
        medicine_name_lower = medicine_name.lower().strip()

        # Skip common words that would cause false matches
        skip_words = {'tablet', 'capsule', 'syrup', 'injection', 'cream', 'drops', 'once', 'daily', 'twice', 'thrice', 'morning', 'evening', 'night', 'before', 'after', 'meals', 'food', 'breakfast', 'lunch', 'dinner', 'week', 'month', 'day', 'days', 'week', 'weeks', 'month', 'months'}

        # Split medicine name into meaningful words (skip numbers and common words)
        words = []
        for word in medicine_name_lower.split():
            # Skip if it's a number, too short, or a common word
            if len(word) > 2 and not word.isdigit() and word not in skip_words:
                # Remove dosage units
                if not any(unit in word for unit in ['mg', 'ml', 'g', 'mcg', 'iu', 'units']):
                    words.append(word)

        if not words:
            return None

        # Try different matching strategies
        # Strategy 1: Match medicines that contain the first significant word
        first_word = words[0]
        medicines = Medicine.objects.filter(
            (Q(name__icontains=first_word) | Q(generic_name__icontains=first_word)),
            quantity__gt=0
        )

        if medicines.exists():
            # Return the first match for now - in production, you might want to rank by similarity
            return medicines.first()

        # Strategy 2: If no match with first word, try second word if available
        if len(words) > 1:
            second_word = words[1]
            medicines = Medicine.objects.filter(
                (Q(name__icontains=second_word) | Q(generic_name__icontains=second_word)),
                quantity__gt=0
            )
            if medicines.exists():
                return medicines.first()

        return None

class CartService:
    """Service class for cart operations"""
    
    @staticmethod
    def get_or_create_cart(user):
        """Get or create cart for user"""
        from .models import Cart
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    @staticmethod
    def add_to_cart(user, medicine_id: int, quantity: int = 1, is_advance_order: bool = False):
        """Add medicine to cart"""
        from .models import Cart, CartItem
        from medicines.models import Medicine

        try:
            # For advance orders, allow medicines with quantity = 0
            if is_advance_order:
                medicine = Medicine.objects.get(id=medicine_id)
            else:
                medicine = Medicine.objects.get(id=medicine_id, quantity__gt=0)

            if not is_advance_order and quantity > medicine.quantity:
                raise ValueError(f"Only {medicine.quantity} units available")

            cart = CartService.get_or_create_cart(user)

            # Check if medicine already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                medicine=medicine,
                defaults={'quantity': quantity, 'is_advance_order': is_advance_order}
            )

            if not created:
                new_quantity = cart_item.quantity + quantity
                if not is_advance_order and new_quantity > medicine.quantity:
                    raise ValueError(f"Only {medicine.quantity} units available")
                cart_item.quantity = new_quantity
                # Update is_advance_order flag if it's different
                if cart_item.is_advance_order != is_advance_order:
                    cart_item.is_advance_order = is_advance_order
                cart_item.save()

            return cart_item

        except Medicine.DoesNotExist:
            raise ValueError("Medicine not found or out of stock")
    
    @staticmethod
    def update_cart_item(user, medicine_id: int, quantity: int):
        """Update cart item quantity"""
        from .models import CartItem

        try:
            cart_item = CartItem.objects.get(
                cart__user=user,
                medicine_id=medicine_id
            )

            if quantity <= 0:
                cart_item.delete()
                return None
            else:
                # Check stock availability if not advance order
                if not cart_item.is_advance_order and quantity > cart_item.medicine.quantity:
                    raise ValueError(f"Only {cart_item.medicine.quantity} units available")
                cart_item.quantity = quantity
                cart_item.save()
                return cart_item

        except CartItem.DoesNotExist:
            raise ValueError("Item not found in cart")
    
    @staticmethod
    def remove_from_cart(user, medicine_id: int):
        """Remove item from cart"""
        from .models import CartItem
        
        try:
            cart_items = CartItem.objects.filter(
                cart__user=user,
                medicine_id=medicine_id
            )
            if not cart_items.exists():
                return False
            # Delete all matching cart items (should normally be one)
            cart_items.delete()
            return True
        except Exception:
            return False
    
    @staticmethod
    def clear_cart(user):
        """Clear user's cart"""
        from .models import Cart
        
        try:
            cart = Cart.objects.get(user=user)
            cart.items.all().delete()
            return True
        except Cart.DoesNotExist:
            return False

class ReminderService:
    """Service class for medicine reminders"""
    
    @staticmethod
    def create_reminders_from_order(order):
        """Create reminders for medicines in an order"""
        from .models import MedicineReminder
        from datetime import date, timedelta
        
        reminders = []
        
        for item in order.items.all():
            if item.prescription_medicine:
                # Create reminder based on prescription information
                reminder = MedicineReminder.objects.create(
                    user=order.user,
                    order_item=item,
                    medicine_name=item.medicine.name,
                    dosage=item.prescription_medicine.dosage or "As prescribed",
                    frequency=ReminderService._determine_frequency(item.prescription_medicine.frequency),
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=30),  # Default 30 days
                    is_active=True
                )
                reminders.append(reminder)
        
        return reminders
    
    @staticmethod
    def _determine_frequency(frequency_text: str) -> str:
        """Determine frequency from text"""
        frequency_text = frequency_text.lower()
        
        if 'once' in frequency_text or '1' in frequency_text:
            return 'once_daily'
        elif 'twice' in frequency_text or '2' in frequency_text:
            return 'twice_daily'
        elif 'thrice' in frequency_text or '3' in frequency_text:
            return 'thrice_daily'
        elif 'before' in frequency_text:
            return 'before_meals'
        elif 'after' in frequency_text:
            return 'after_meals'
        else:
            return 'once_daily'
