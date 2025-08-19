from django import forms
from .models import Member
from django import forms
from django.utils.timezone import localdate
from .models import Member
from django import forms
from .models import Member
from django import forms
from .models import ServedMember

class ServeMemberForm(forms.ModelForm):
    account_number = forms.CharField(max_length=9, required=True, help_text="Enter Account Number")

    class Meta:
        model = ServedMember
        fields = ['account_number', 'amount_given', 'reason']


class MemberForm(forms.ModelForm):
    spouse_name_status = forms.BooleanField(
        required=False,  # Not mandatory
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})  # Bootstrap class for styling
    )

    class Meta:
        model = Member
        fields = ['spouse_name_status', 'spouse_name']


class MemberForm(forms.ModelForm):
    subscription_start = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'min': localdate()}  # HTML5 date input
        )
    )

    class Meta:
        model = Member
        fields = '__all__'  # Include all fields or specify the required ones


class MemberRegistrationForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = '__all__'  # Include all fields from the model
        widgets = {
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'subscription_start': forms.DateInput(attrs={'type': 'date'}),
            'subscription_end': forms.DateInput(attrs={'type': 'date'}),
        }


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = '__all__'  # Include all fields from the model
        widgets = {
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'profile_picture': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'id_scan': forms.ClearableFileInput(attrs={'accept': 'application/pdf,image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
    # Optionally, you can add some custom validation
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Member.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email




from django import forms
from .models import Customer, Member

class MemberRegistrationForm(forms.ModelForm):
    # Customer fields
    surname = forms.CharField(max_length=100)
    member_number = forms.CharField(max_length=50, disabled=True)  # Read-only
    phone = forms.CharField(max_length=15, required=False)
    dob = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    branch = forms.CharField(max_length=100, disabled=True)  # Read-only

    class Meta:
        model = Member
        fields = ['subscription_start', 'subscription_end', 'status']
        widgets = {
            'subscription_start': forms.DateInput(attrs={'type': 'date'}),
            'subscription_end': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=[('active', 'Active'), ('expired', 'Expired')]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Pre-fill Customer fields if Member exists
            self.fields['surname'].initial = self.instance.customer.surname
            self.fields['first_name'].initial = self.instance.customer.first_name
            self.fields['member_number'].initial = self.instance.customer.member_number
            self.fields['phone'].initial = self.instance.customer.phone
            self.fields['dob'].initial = self.instance.customer.dob
            self.fields['branch'].initial = self.instance.customer.branch



#######################################################################################################################################
# munomukabitemp/forms.py
from django import forms
from .models import Member
from staff_management.models import Staff, Position

class MunoMemberForm(forms.ModelForm):
    teller = forms.ChoiceField(
        choices=(),  # Populated dynamically in __init__
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Member
        fields = [
            'subscription_start', 'payment_date', 'payment_number', 'booklet_number', 'teller',
            'spouse_name', 'spouse_status', 'spouse_address',
            'mother_name', 'mother_village', 'mother_status', 'mother_guardian', 'mother_guardian_address',
            'father_name', 'father_village', 'father_status', 'father_guardian', 'father_guardian_address',
            'child1_name', 'child2_name',
            'next_of_kin_Name', 'next_of_kin_relationship', 'next_of_kin_village', 'next_of_kin_phone',
            'sao_officer',
        ]
        widgets = {
            'subscription_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_number': forms.TextInput(attrs={'class': 'form-control'}),
            'booklet_number': forms.TextInput(attrs={'class': 'form-control'}),
            'spouse_name': forms.TextInput(attrs={'class': 'form-control'}),
            'spouse_status': forms.Select(attrs={'class': 'form-control'}),
            'spouse_address': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_village': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_status': forms.Select(attrs={'class': 'form-control'}),
            'mother_guardian': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_guardian_address': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_village': forms.TextInput(attrs={'class': 'form-control'}),
            'father_status': forms.Select(attrs={'class': 'form-control'}),
            'father_guardian': forms.TextInput(attrs={'class': 'form-control'}),
            'father_guardian_address': forms.TextInput(attrs={'class': 'form-control'}),
            'child1_name': forms.TextInput(attrs={'class': 'form-control'}),
            'child2_name': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_Name': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_village': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'sao_officer': forms.TextInput(attrs={'class': 'form-control'}),
            'creation_date': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'modification_date': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, customer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer = customer
        if customer and not self.instance.pk:  # Set customer for new instances
            self.instance.customer = customer

        # Populate teller choices
        try:
            teller_position = Position.objects.get(name="Teller")
            tellers = Staff.objects.filter(position=teller_position).order_by('first_name', 'last_name')
            self.fields['teller'].choices = [('', 'Select a Teller')] + [
                (f"{staff.first_name} {staff.last_name}", f"{staff.first_name} {staff.last_name}") for staff in tellers
            ]
            if self.instance.teller:
                self.fields['teller'].initial = self.instance.teller
        except Position.DoesNotExist:
            self.fields['teller'].choices = [('', 'No tellers available')]
            self.add_error('teller', 'Teller position not found. Please ensure it exists in the system.')

        # Make status read-only if updating an existing active member
        if self.instance.pk and self.instance.status == 'active':
            self.fields['status'] = forms.CharField(
                initial=self.instance.status,
                disabled=True,
                widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
            )
        else:
            self.fields['status'] = forms.ChoiceField(
                choices=Member.STATUS_CHOICES,
                initial='active',
                widget=forms.Select(attrs={'class': 'form-control'})
            )

    def clean_payment_number(self):
        payment_number = self.cleaned_data.get('payment_number')
        if payment_number:
            queryset = Member.objects.filter(payment_number=payment_number)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("This payment number is already in use.")
        return payment_number

    def clean_booklet_number(self):
        booklet_number = self.cleaned_data.get('booklet_number')
        if booklet_number:
            queryset = Member.objects.filter(booklet_number=booklet_number)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("This booklet number is already in use.")
        return booklet_number

    def clean_teller(self):
        teller = self.cleaned_data.get('teller')
        if teller:
            try:
                teller_position = Position.objects.get(name="Teller")
                names = teller.split()
                if len(names) >= 2:
                    first_name, last_name = names[0], ' '.join(names[1:])
                    if not Staff.objects.filter(position=teller_position, first_name=first_name, last_name=last_name).exists():
                        raise forms.ValidationError("Invalid teller selected.")
                else:
                    raise forms.ValidationError("Invalid teller name format.")
            except Position.DoesNotExist:
                raise forms.ValidationError("Teller position not found.")
        return teller

    def clean(self):
        cleaned_data = super().clean()
        mother_status = cleaned_data.get('mother_status')
        father_status = cleaned_data.get('father_status')
        mother_guardian = cleaned_data.get('mother_guardian')
        mother_guardian_address = cleaned_data.get('mother_guardian_address')
        father_guardian = cleaned_data.get('father_guardian')
        father_guardian_address = cleaned_data.get('father_guardian_address')
        subscription_start = cleaned_data.get('subscription_start')
        payment_date = cleaned_data.get('payment_date')

        # Validate guardian fields for deceased parents
        if mother_status == 'dd':
            if not mother_guardian:
                self.add_error('mother_guardian', 'Mother guardian is required if mother is deceased.')
            if not mother_guardian_address:
                self.add_error('mother_guardian_address', 'Mother guardian address is required if mother is deceased.')
        if father_status == 'dd':
            if not father_guardian:
                self.add_error('father_guardian', 'Father guardian is required if father is deceased.')
            if not father_guardian_address:
                self.add_error('father_guardian_address', 'Father guardian address is required if father is deceased.')

        # Validate required fields
        for field in ['next_of_kin_Name', 'next_of_kin_relationship', 'next_of_kin_village', 'sao_officer', 'teller']:
            if not cleaned_data.get(field):
                self.add_error(field, f"{field.replace('_', ' ').title()} is required.")

        # Validate subscription_start and payment_date
        if subscription_start and payment_date and payment_date > subscription_start:
            self.add_error('payment_date', 'Payment date cannot be after subscription start date.')

        return cleaned_data
####################################################################################
# munomukabitemp/views.py
# Munomukabi/forms.py
from django import forms
from .models import Member
from staff_management.models import Staff, Position
from datetime import date

class RenewalForm(forms.Form):
    subscription_start = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        help_text="Select the start date for the new subscription."
    )
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        help_text="Enter the date of payment."
    )
    payment_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        help_text="Enter a unique payment number."
    )
    booklet_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
        help_text="Enter a unique booklet number."
    )
    teller = forms.ChoiceField(
        choices=(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        help_text="Select the teller who processed the renewal."
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        # Populate teller choices
        try:
            teller_position = Position.objects.get(name="Teller")
            tellers = Staff.objects.filter(position=teller_position).order_by('first_name', 'last_name')
            self.fields['teller'].choices = [('', 'Select a Teller')] + [
                (f"{staff.first_name} {staff.last_name}", f"{staff.first_name} {staff.last_name}") for staff in tellers
            ]
        except Position.DoesNotExist:
            self.fields['teller'].choices = [('', 'No tellers available')]
            self.add_error('teller', 'Teller position not found. Please ensure it exists in the system.')

    def clean_payment_number(self):
        payment_number = self.cleaned_data.get('payment_number')
        if payment_number and Member.objects.filter(payment_number=payment_number).exists():
            raise forms.ValidationError("This payment number is already in use.")
        return payment_number

    def clean_booklet_number(self):
        booklet_number = self.cleaned_data.get('booklet_number')
        if booklet_number and Member.objects.filter(booklet_number=booklet_number).exists():
            raise forms.ValidationError("This booklet number is already in use.")
        return booklet_number

    def clean_teller(self):
        teller = self.cleaned_data.get('teller')
        if teller:
            try:
                teller_position = Position.objects.get(name="Teller")
                names = teller.split()
                if len(names) >= 2:
                    first_name, last_name = names[0], ' '.join(names[1:])
                    if not Staff.objects.filter(position=teller_position, first_name=first_name, last_name=last_name).exists():
                        raise forms.ValidationError("Invalid teller selected.")
                else:
                    raise forms.ValidationError("Invalid teller name format.")
            except Position.DoesNotExist:
                raise forms.ValidationError("Teller position not found.")
        return teller

    def clean(self):
        cleaned_data = super().clean()
        subscription_start = cleaned_data.get('subscription_start')
        payment_date = cleaned_data.get('payment_date')

        if subscription_start and payment_date and payment_date > subscription_start:
            self.add_error('payment_date', 'Payment date cannot be after subscription start date.')
        if subscription_start and subscription_start > date.today() and (not self.user or not self.user.is_superuser):
            self.add_error('subscription_start', 'Subscription start date cannot be in the future unless you are an admin.')

        return cleaned_data

class MunoMemberForm(forms.ModelForm):
    teller = forms.ChoiceField(
        choices=(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Member
        fields = [
            'subscription_start', 'payment_date', 'payment_number', 'booklet_number', 'teller',
            'spouse_name', 'spouse_status', 'spouse_address',
            'mother_name', 'mother_village', 'mother_status', 'mother_guardian', 'mother_guardian_address',
            'father_name', 'father_village', 'father_status', 'father_guardian', 'father_guardian_address',
            'child1_name', 'child2_name',
            'next_of_kin_Name', 'next_of_kin_relationship', 'next_of_kin_village', 'next_of_kin_phone',
            'sao_officer',
        ]
        widgets = {
            'subscription_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_number': forms.TextInput(attrs={'class': 'form-control'}),
            'booklet_number': forms.TextInput(attrs={'class': 'form-control'}),
            'spouse_name': forms.TextInput(attrs={'class': 'form-control'}),
            'spouse_status': forms.Select(attrs={'class': 'form-control'}),
            'spouse_address': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_village': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_status': forms.Select(attrs={'class': 'form-control'}),
            'mother_guardian': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_guardian_address': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_village': forms.TextInput(attrs={'class': 'form-control'}),
            'father_status': forms.Select(attrs={'class': 'form-control'}),
            'father_guardian': forms.TextInput(attrs={'class': 'form-control'}),
            'father_guardian_address': forms.TextInput(attrs={'class': 'form-control'}),
            'child1_name': forms.TextInput(attrs={'class': 'form-control'}),
            'child2_name': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_Name': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_village': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'sao_officer': forms.TextInput(attrs={'class': 'form-control'}),
            'creation_date': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'modification_date': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, customer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer = customer
        if customer and not self.instance.pk:
            self.instance.customer = customer
        try:
            teller_position = Position.objects.get(name="Teller")
            tellers = Staff.objects.filter(position=teller_position).order_by('first_name', 'last_name')
            self.fields['teller'].choices = [('', 'Select a Teller')] + [
                (f"{staff.first_name} {staff.last_name}", f"{staff.first_name} {staff.last_name}") for staff in tellers
            ]
            if self.instance.teller:
                self.fields['teller'].initial = self.instance.teller
        except Position.DoesNotExist:
            self.fields['teller'].choices = [('', 'No tellers available')]
            self.add_error('teller', 'Teller position not found. Please ensure it exists in the system.')
        if self.instance.pk and self.instance.status == 'active':
            self.fields['status'] = forms.CharField(
                initial=self.instance.status,
                disabled=True,
                widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
            )
        else:
            self.fields['status'] = forms.ChoiceField(
                choices=Member.STATUS_CHOICES,
                initial='active',
                widget=forms.Select(attrs={'class': 'form-control'})
            )

    def clean_payment_number(self):
        payment_number = self.cleaned_data.get('payment_number')
        if payment_number:
            queryset = Member.objects.filter(payment_number=payment_number)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("This payment number is already in use.")
        return payment_number

    def clean_booklet_number(self):
        booklet_number = self.cleaned_data.get('booklet_number')
        if booklet_number:
            queryset = Member.objects.filter(booklet_number=booklet_number)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("This booklet number is already in use.")
        return booklet_number

    def clean_teller(self):
        teller = self.cleaned_data.get('teller')
        if teller:
            try:
                teller_position = Position.objects.get(name="Teller")
                names = teller.split()
                if len(names) >= 2:
                    first_name, last_name = names[0], ' '.join(names[1:])
                    if not Staff.objects.filter(position=teller_position, first_name=first_name, last_name=last_name).exists():
                        raise forms.ValidationError("Invalid teller selected.")
                else:
                    raise forms.ValidationError("Invalid teller name format.")
            except Position.DoesNotExist:
                raise forms.ValidationError("Teller position not found.")
        return teller

    def clean(self):
        cleaned_data = super().clean()
        mother_status = cleaned_data.get('mother_status')
        father_status = cleaned_data.get('father_status')
        mother_guardian = cleaned_data.get('mother_guardian')
        mother_guardian_address = cleaned_data.get('mother_guardian_address')
        father_guardian = cleaned_data.get('father_guardian')
        father_guardian_address = cleaned_data.get('father_guardian_address')
        subscription_start = cleaned_data.get('subscription_start')
        payment_date = cleaned_data.get('payment_date')
        if mother_status == 'dd':
            if not mother_guardian:
                self.add_error('mother_guardian', 'Mother guardian is required if mother is deceased.')
            if not mother_guardian_address:
                self.add_error('mother_guardian_address', 'Mother guardian address is required if mother is deceased.')
        if father_status == 'dd':
            if not father_guardian:
                self.add_error('father_guardian', 'Father guardian is required if father is deceased.')
            if not father_guardian_address:
                self.add_error('father_guardian_address', 'Father guardian address is required if father is deceased.')
        for field in ['next_of_kin_Name', 'next_of_kin_relationship', 'next_of_kin_village', 'sao_officer', 'teller']:
            if not cleaned_data.get(field):
                self.add_error(field, f"{field.replace('_', ' ').title()} is required.")
        if subscription_start and payment_date and payment_date > subscription_start:
            self.add_error('payment_date', 'Payment date cannot be after subscription start date.')
        return cleaned_data