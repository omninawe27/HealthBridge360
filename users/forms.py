from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re
from .models import User

def validate_phone_number(value):
    """Validate Indian phone number format"""
    if not re.match(r'^[6-9]\d{9}$', value):
        raise ValidationError('Phone number must be 10 digits starting with 6-9.')

def validate_username(value):
    """Validate username for security"""
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError('Username can only contain letters, numbers, and underscores.')
    if len(value) < 3:
        raise ValidationError('Username must be at least 3 characters long.')

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'First name can only contain letters and spaces.')]
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Last name can only contain letters and spaces.')]
    )
    phone_number = forms.CharField(
        max_length=10,
        required=True,
        validators=[validate_phone_number]
    )
    email = forms.EmailField(required=True)
    preferred_language = forms.ChoiceField(choices=User.LANGUAGE_CHOICES, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'preferred_language', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].validators.append(validate_username)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        return username

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
