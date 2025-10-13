from django import forms
from .models import Pharmacy
from users.models import User

class PharmacyRegistrationForm(forms.ModelForm):
    owner_first_name = forms.CharField(max_length=30, required=True)
    owner_last_name = forms.CharField(max_length=30, required=True)
    owner_username = forms.CharField(max_length=150, required=True)
    owner_email = forms.EmailField(required=True)
    owner_phone = forms.CharField(max_length=10, required=True)
    owner_password = forms.CharField(widget=forms.PasswordInput, required=True)
    owner_password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)
    
    class Meta:
        model = Pharmacy
        fields = ['name', 'address', 'phone_number','license_number', 'is_24x7']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # Make address field smaller
        if 'address' in self.fields:
            self.fields['address'].widget.attrs.update({
                'rows': 5,
                'style': 'height: 100px;'
            })
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('owner_password')
        password_confirm = cleaned_data.get('owner_password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data
