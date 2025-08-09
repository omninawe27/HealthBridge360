from django import forms
from .models import Reminder

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['medicine_name', 'time_slot', 'specific_time', 'notes', 'alert_type', 'send_email', 'send_sms']
        widgets = {
            'medicine_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter medicine name'
            }),
            'time_slot': forms.Select(attrs={
                'class': 'form-select'
            }),
            'specific_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., Take after lunch, with water, etc.'
            }),
            'alert_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'send_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'send_sms': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        if not self.instance.pk:
            self.fields['alert_type'].initial = 'tone'
    
    def clean(self):
        cleaned_data = super().clean()
        time_slot = cleaned_data.get('time_slot')
        specific_time = cleaned_data.get('specific_time')
        
        # Validate that specific time is within the time slot
        if specific_time and time_slot:
            hour = specific_time.hour
            
            if time_slot == 'morning' and not (6 <= hour < 12):
                raise forms.ValidationError("Morning time should be between 6 AM and 12 PM")
            elif time_slot == 'afternoon' and not (12 <= hour < 17):
                raise forms.ValidationError("Afternoon time should be between 12 PM and 5 PM")
            elif time_slot == 'evening' and not (17 <= hour < 21):
                raise forms.ValidationError("Evening time should be between 5 PM and 9 PM")
            elif time_slot == 'night' and not (21 <= hour or hour < 6):
                raise forms.ValidationError("Night time should be between 9 PM and 6 AM")
        
        return cleaned_data

class QuickReminderForm(forms.Form):
    """Quick reminder form for adding reminders on the go"""
    medicine_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Medicine name'
        })
    )
    
    time_slot = forms.ChoiceField(
        choices=Reminder.TIME_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    notes = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Notes (optional)'
        })
    )

class ReminderSearchForm(forms.Form):
    """Form for searching and filtering reminders"""
    query = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search reminders...'
        })
    )
    
    time_slot = forms.ChoiceField(
        choices=[('', 'All Times')] + Reminder.TIME_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    alert_type = forms.ChoiceField(
        choices=[('', 'All Alerts')] + Reminder.ALERT_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

class BulkReminderForm(forms.Form):
    """Form for creating multiple reminders at once"""
    medicine_names = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter medicine names, one per line'
        }),
        help_text='Enter each medicine name on a separate line'
    )
    
    time_slots = forms.MultipleChoiceField(
        choices=Reminder.TIME_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        help_text='Select all time slots for these medicines'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Common notes for all reminders'
        })
    )
    
    alert_type = forms.ChoiceField(
        choices=Reminder.ALERT_TYPES,
        initial='tone',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    def clean_medicine_names(self):
        medicine_names = self.cleaned_data['medicine_names']
        if medicine_names:
            # Split by lines and clean up
            names = [name.strip() for name in medicine_names.split('\n') if name.strip()]
            if not names:
                raise forms.ValidationError("Please enter at least one medicine name")
            return names
        return []
    
    def clean_time_slots(self):
        time_slots = self.cleaned_data['time_slots']
        if not time_slots:
            raise forms.ValidationError("Please select at least one time slot")
        return time_slots
