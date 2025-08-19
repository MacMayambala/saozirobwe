from django import forms  # Add this import
from .models import Staff, Branch, Position, Department, StaffTargetType
class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class StaffForm(forms.ModelForm):
    # Custom field definitions to match template names
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    other_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(required=False)
    gender = forms.ChoiceField(choices=[('', 'Gender *'), ('Male', 'Male'), ('Female', 'Female')], required=True)
    marital_status = forms.ChoiceField(choices=[('', 'Marital Status'), ('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced')], required=False)

    id_type = forms.ChoiceField(
        choices=[('', 'Identification Type *'), ('National ID', 'National ID'), ('Passport', 'Passport'), ("Driver's License", "Driver's License")],
        required=True,
        label="Identification Type"
    )
    id_number = forms.CharField(max_length=50, required=True, label="Identification Number")
    phone = forms.CharField(max_length=15, required=True, label="Telephone Number")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label="Physical Address")

    next_of_kin_name = forms.CharField(max_length=100, required=True)
    next_of_kin_phone = forms.CharField(max_length=15, required=True)
    next_of_kin_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    relationship = forms.ChoiceField(choices=[('', 'Relationship *'), ('Spouse', 'Spouse'), ('Sibling', 'Sibling'), ('Parent', 'Parent'), ('Child', 'Child'), ('Other', 'Other')], required=True)

    date_appointed = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    basic_salary = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    payment_method = forms.ChoiceField(choices=[('', 'Payment Method *'), ('Bank', 'Bank'), ('Mobile Money', 'Mobile Money'), ('Cash', 'Cash')], required=True)

    tax_id = forms.CharField(max_length=100, required=False, label="Tax Identification Number")
    ssn = forms.CharField(max_length=100, required=False, label="Social Security Number")
    
    # Updated fields to use DecimalField
    ssf = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="SSF Contribution")
    lst = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="LST Deduction")
    paye = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="PAYE Deduction")

    contract_file = forms.FileField(required=False, label="Employment Contract")
    signature_file = forms.ImageField(required=False, label="Signature")
    id_attachment = forms.FileField(required=False, label="ID Attachment")
    profile_photo = forms.ImageField(required=False, label="Profile Photo")

    class Meta:
        model = Staff
        fields = [
            'staff_id', 'first_name', 'last_name', 'other_name', 'email', 'gender',
            'marital_status', 'id_type', 'id_number', 'phone', 'address',
            'next_of_kin_name', 'next_of_kin_phone', 'next_of_kin_address', 'relationship',
            'date_appointed', 'basic_salary', 'payment_method', 'tax_id', 'ssn',
            'branch', 'position', 'department', 'ssf', 'lst', 'paye',
            'contract_file', 'signature_file', 'id_attachment', 'profile_photo'
        ]
        exclude = ['employee_id']  # Exclude auto-generated field


        
    # Mapping form field names to model field names
    model_field_mapping = {
        'id_type': 'identification_type',
        'id_number': 'identification_number',
        'phone': 'phone_number',
        'address': 'physical_address',
        'relationship': 'next_of_kin_relationship',
        'tax_id': 'tax_identification_number',
        'ssn': 'social_security_number',
        'contract_file': 'employment_contract',
        'signature_file': 'signature',
        'id_attachment': 'identification_upload',
        'profile_photo': 'photo',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make related fields required
        self.fields['branch'].required = True
        self.fields['position'].required = True
        self.fields['department'].required = False

        # Style form fields with Bootstrap and placeholders
        for name, field in self.fields.items():
            if name not in ['date_appointed', 'contract_file', 'signature_file', 'id_attachment', 'profile_photo']:
                field.widget.attrs['class'] = 'form-control'
            if field.required and name not in ['gender', 'marital_status', 'id_type', 'relationship', 'payment_method', 'branch', 'position', 'department']:
                field.widget.attrs['placeholder'] = f"{field.label} *"

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('256') or len(phone) != 12:
            raise forms.ValidationError("Phone number must be in the format 256XXXXXXXXX.")
        return phone

    def clean_next_of_kin_phone(self):
        phone = self.cleaned_data.get('next_of_kin_phone')
        if not phone.startswith('256') or len(phone) != 12:
            raise forms.ValidationError("Next of kin phone number must be in the format 256XXXXXXXXX.")
        return phone

    # Clean decimal fields to handle empty inputs
    def clean_ssf(self):
        ssf = self.cleaned_data.get('ssf')
        return ssf if ssf is not None else None

    def clean_lst(self):
        lst = self.cleaned_data.get('lst')
        return lst if lst is not None else None

    def clean_paye(self):
        paye = self.cleaned_data.get('paye')
        return paye if paye is not None else None

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Map fields from form to model field names
        for form_field, model_field in self.model_field_mapping.items():
            value = self.cleaned_data.get(form_field)
            if value is not None:
                setattr(instance, model_field, value)

        if commit:
            instance.save()
            self.save_m2m()

        return instance
    

# Munomukabi/forms.py
class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['code', 'name']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '1'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_code(self):
        code = self.cleaned_data['code']
        if len(code) != 1:
            raise forms.ValidationError("Code must be exactly 1 character.")
        return code

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        return name

#####Staff Target Type Form#####################################

class StaffTargetTypeForm(forms.ModelForm):
    class Meta:
        model = StaffTargetType
        fields = ['stname', 'description']
        widgets = {
            'stname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter target type name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter description (optional)'}),
        }
        labels = {
            'stname': 'Target Type Name',
            'description': 'Description',
        }
        
    def clean_stname(self):
        stname = self.cleaned_data.get('stname')
        if stname:
            # Additional validation can go here if needed
            return stname.strip()
        return stname
    




###################################################
# staff_management/forms.py
from django import forms
from django.utils import timezone
from .models import Target, StaffTargetType

class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ['target_type',  'goal_value', 'current_value', 'start_date', 'end_date']
        widgets = {
            'target_type': forms.Select(attrs={'class': 'form-control'}),
            
            'goal_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g., 10.00'}),
            'current_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g., 2.00'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        staff = self.instance.staff if self.instance.pk else None
        target_type = cleaned_data.get('target_type')
        end_date = cleaned_data.get('end_date')

        if staff and target_type:
            today = timezone.now().date()
            if Target.objects.filter(
                staff=staff,
                target_type=target_type,
                end_date__gte=today
            ).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(
                    f"An active target of type '{target_type.stname}' already exists for this staff member. "
                    f"Wait until the end date is reached to assign this type again."
                )
        return cleaned_data