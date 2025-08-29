from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from staff_management.models import Branch  # Assuming you have a Branch model

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from staff_management.models import Branch
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=True,
        label="Branch",
        help_text="Select the branch where the user is assigned."
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Groups",
        help_text="Select the groups to assign roles to the user."
    )

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'branch', 'groups', 'password1', 'password2'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        # Save base User first
        user = super().save(commit=commit)

        # Save branch into CustomUser
        branch = self.cleaned_data.get('branch')
        customuser, created = CustomUser.objects.get_or_create(user=user)
        customuser.branch = branch
        if commit:
            customuser.save()

        # Save groups into User.groups
        groups = self.cleaned_data.get('groups')
        if groups:
            user.groups.set(groups)

        return user

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User, Group
from staff_management.models import Branch
from .models import CustomUser

class CustomUserEditForm(UserChangeForm):
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=True,
        label="Branch",
        help_text="Select the branch where the user is assigned."
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Groups",
        help_text="Select the groups to assign roles to the user."
    )

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 
            'branch', 'groups', 'is_active', 'is_staff'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        # Remove password field from edit form
        self.fields.pop('password', None)

        # Pre-fill branch and groups from instance
        if self.instance:
            if hasattr(self.instance, 'customuser'):
                self.fields['branch'].initial = self.instance.customuser.branch
            self.fields['groups'].initial = self.instance.groups.all()

    def save(self, commit=True):
        user = super().save(commit=commit)

        # Update CustomUser branch
        branch = self.cleaned_data.get('branch')
        customuser, created = CustomUser.objects.get_or_create(user=user)
        customuser.branch = branch
        if commit:
            customuser.save()

        # Update User groups
        groups = self.cleaned_data.get('groups')
        if groups is not None:
            user.groups.set(groups)

        return user
########################################################################################
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your email"
    }))

class SetNewPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


# users/forms.py
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from .models import PasswordHistory

class CustomSetPasswordForm(SetPasswordForm):
    def clean_new_password1(self):
        new_password = self.cleaned_data.get("new_password1")
        user = self.user

        # Check against previous passwords
        previous_passwords = PasswordHistory.objects.filter(user=user)
        for old in previous_passwords:
            if user.check_password(new_password):  # hashed comparison
                raise ValidationError("You cannot reuse a previous password.")

        return new_password
#############################################################################################################
