from django import forms
from .models import Order
from medicines.models import Medicine

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['pharmacy', 'notes', 'prescription_image']
        widgets = {
            'pharmacy': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special instructions or notes...'
            }),
            'prescription_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter pharmacies to only show active ones
        self.fields['pharmacy'].queryset = self.fields['pharmacy'].queryset.filter(is_active=True)

class PrescriptionUploadForm(forms.Form):
    prescription_image = forms.ImageField(
        label='Upload Prescription',
        help_text='Upload a clear image of your prescription',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'prescription-input'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any additional notes for the pharmacist...'
        })
    )
    
    def clean_prescription_image(self):
        image = self.cleaned_data.get('prescription_image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file size must be less than 5MB")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if image.content_type not in allowed_types:
                raise forms.ValidationError("Please upload a valid image file (JPEG, PNG, GIF)")
        
        return image

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

class CheckoutForm(forms.Form):
    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your delivery address...'
        })
    )
    
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=[
            ('cod', 'Cash on Delivery'),
            ('online', 'Online Payment'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Any special instructions...'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default phone number if user has one
        if 'initial' in kwargs and 'user' in kwargs['initial']:
            user = kwargs['initial']['user']
            if user.phone_number:
                self.fields['phone_number'].initial = user.phone_number

class OrderStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(
        choices=Order.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Add notes about status update...'
        })
    )
