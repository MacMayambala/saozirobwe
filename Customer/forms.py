from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
            "mem_reg_date": forms.DateInput(attrs={"type": "date"}),
            "is_pwd": forms.CheckboxInput(),
        }
        fields = '__all__'


    # Custom validation for phone number
    def clean_phone_number1(self):
        phone = self.cleaned_data['phone_number1']
        if not phone.startswith("256") or len(phone) != 12:
            raise forms.ValidationError("Phone number must be 12 digits and start with 256.")
        return phone

    # Custom validation for ID Number
    def clean_id_number(self):
        id_number = self.cleaned_data['id_number']
        if not id_number.startswith(("CF", "CM")) or len(id_number) != 14:
            raise forms.ValidationError("ID number must start with CF or CM and be 14 characters long.")
        return id_number
    


    # yourapp/forms.py
from django import forms
from .models import Customer

class CustomerEditForm(forms.ModelForm):
    class Meta:
        model = Customer
        # Exclude cus_id since it’s auto-generated and should not be editable
        exclude = ['cus_id', 'created_at', 'updated_at']
        widgets = {
            'branch': forms.TextInput(attrs={'readonly': 'readonly'}),  # Make branch read-only
            'mem_reg_date': forms.DateInput(attrs={'type': 'date'}),
            'dob': forms.DateInput(attrs={'type': 'date'}),
            # Add other widgets for better UI if needed
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure branch is not editable in the form
        self.fields['branch'].disabled = True
