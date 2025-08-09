from django import forms
from .models import Medicine

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name', 'generic_name', 'brand', 'medicine_type', 'strength',
            'price', 'quantity', 'expiry_date', 'batch_number',
            'is_essential', 'is_prescription_required'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter medicine name'
            }),
            'generic_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter generic name'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter brand name'
            }),
            'medicine_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'strength': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 500mg, 10ml'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'batch_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter batch number'
            }),
            'is_essential': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_prescription_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        if not self.instance.pk:
            self.fields['is_essential'].initial = False
            self.fields['is_prescription_required'].initial = True
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        price = cleaned_data.get('price')
        expiry_date = cleaned_data.get('expiry_date')
        
        # Validate quantity
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative")
        
        # Validate price
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative")
        
        # Validate expiry date
        if expiry_date:
            from django.utils import timezone
            if expiry_date <= timezone.now().date():
                raise forms.ValidationError("Expiry date cannot be in the past")
        
        return cleaned_data

class MedicineSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search medicines...'
        })
    )
    
    medicine_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Medicine.MEDICINE_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    price_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '0.01',
            'min': '0'
        })
    )
    
    price_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '0.01',
            'min': '0'
        })
    )
    
    in_stock_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

class BulkStockUpdateForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx'
        }),
        help_text='Upload CSV or Excel file with columns: Medicine ID, Quantity, Price'
    )
    
    def clean_file(self):
        file = self.cleaned_data['file']
        if file:
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 5MB")
            
            # Check file extension
            allowed_extensions = ['.csv', '.xlsx', '.xls']
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError("Only CSV and Excel files are allowed")
        
        return file
