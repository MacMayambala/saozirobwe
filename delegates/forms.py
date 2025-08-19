from django import forms
from .models import Delegate, Target, Transaction, TargetType
from Customer.models import Customer  # Ensure this import is correct

# Form for Registering a Delegate
class DelegateRegistrationForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        label="Select Customer",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Delegate
        fields = ['customer', 'is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

from django import forms
from .models import Delegate, Target

from django import forms
from .models import Target, Delegate

class TargetCreationForm(forms.ModelForm):
    delegate = forms.ModelChoiceField(
        queryset=Delegate.objects.all(),
        label="Select Delegate",
        widget=forms.HiddenInput()  # Hidden input, populated via JavaScript
    )

    class Meta:
        model = Target
        fields = ['delegate', 'description', 'target_type', 'target_value', 'start_date', 'end_date']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter target description'}),
            'target_type': forms.Select(attrs={'class': 'form-control'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# Form for Creating a Target Type
class TargetTypeCreationForm(forms.ModelForm):
    class Meta:
        model = TargetType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Savings, Shares, Membership'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
        }

# Form for Assigning a Target in Delegate Detail
class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ['target_type', 'description', 'target_value', 'start_date', 'end_date']
        widgets = {
            'target_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter target description'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# Form for Recording a Transaction in Delegate Detail
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['target', 'transaction_type', 'actual_value', 'channel',  'transaction_date']
        widgets = {
            'target': forms.Select(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'actual_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            
            'channel': forms.Select(attrs={'class': 'form-control'}),
            
            'transaction_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


###############################################################################################################
# forms.py
from django import forms
from .models import Term_details
from django import forms
from datetime import datetime
import re
from .models import Term_details

class TermDetailsForm(forms.ModelForm):
    class Meta:
        model = Term_details
        fields = [
            'termId', 'date_range', 'expiry_date', 'description',
            'chairperson', 'secretary', 'vice_chairperson', 'treasurer'
        ]
        widgets = {
            'date_range': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #
