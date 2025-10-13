from django import forms
from .models import Order, Prescription, PrescriptionMedicine, MedicineReminder
from medicines.models import Medicine

class PrescriptionUploadForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['image', 'notes']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'prescription-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional notes for the pharmacist...'
            })
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file size must be less than 5MB")

            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if image.content_type not in allowed_types:
                raise forms.ValidationError("Please upload a valid image file (JPEG, PNG, GIF)")

            # Check file extension
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = image.name.lower().split('.')[-1] if '.' in image.name else ''
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError("Invalid file extension")

            # Basic security check - read first few bytes to ensure it's an image
            image.seek(0)
            file_header = image.read(10)
            image.seek(0)  # Reset file pointer

            # Check for common image signatures
            if not any(file_header.startswith(sig) for sig in [b'\xff\xd8', b'\x89PNG', b'GIF87a', b'GIF89a']):
                raise forms.ValidationError("Uploaded file is not a valid image")

        return image

class PrescriptionMedicineForm(forms.ModelForm):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1'
        })
    )
    
    class Meta:
        model = PrescriptionMedicine
        fields = ['quantity']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.matched_medicine:
            self.fields['quantity'].max_value = self.instance.matched_medicine.quantity

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['pharmacy', 'notes']
        widgets = {
            'pharmacy': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special instructions or notes...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter pharmacies to only show active ones
        self.fields['pharmacy'].queryset = self.fields['pharmacy'].queryset.filter(is_active=True)

class CheckoutForm(forms.ModelForm):
    delivery_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your delivery address...'
        })
    )

    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )

    class Meta:
        model = Order
        fields = ['payment_method', 'delivery_method', 'delivery_address', 'notes']
        widgets = {
            'payment_method': forms.RadioSelect,
            'delivery_method': forms.RadioSelect,
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any special instructions...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default phone number if user has one
        if 'initial' in kwargs and 'user' in kwargs['initial']:
            user = kwargs['initial']['user']
            if hasattr(user, 'phone_number') and user.phone_number:
                self.fields['phone_number'].initial = user.phone_number

        # Set default delivery method to pickup if not already set
        if not self.initial.get('delivery_method'):
            self.initial['delivery_method'] = 'pickup'
    
    def clean(self):
        cleaned_data = super().clean()
        delivery_method = cleaned_data.get('delivery_method')
        delivery_address = cleaned_data.get('delivery_address')
        
        if delivery_method == 'home_delivery' and not delivery_address:
            raise forms.ValidationError("Delivery address is required for home delivery")
        
        return cleaned_data

class MedicineSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        medicines = kwargs.pop('medicines', Medicine.objects.none())
        super().__init__(*args, **kwargs)
        
        for medicine in medicines:
            field_name = f'medicine_{medicine.id}'
            self.fields[field_name] = forms.IntegerField(
                required=False,
                min_value=0,
                max_value=medicine.quantity,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control',
                    'placeholder': '0',
                    'data-medicine-id': medicine.id,
                    'data-medicine-price': str(medicine.price)
                }),
                label=f'{medicine.name} ({medicine.brand}) - ₹{medicine.price}'
            )

class ReminderForm(forms.ModelForm):
    class Meta:
        model = MedicineReminder
        fields = ['frequency', 'start_date', 'end_date', 'custom_schedule']
        widgets = {
            'frequency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'custom_schedule': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter custom schedule (e.g., "8:00 AM, 2:00 PM, 8:00 PM")'
            })
        }

class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Add notes about status update...'
            })
        }
