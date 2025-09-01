from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from staff_management.models import Branch
from .models import CustomUser, Module, UserModuleAccess

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from staff_management.models import Branch
from .models import CustomUser, Module, UserModuleAccess

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
    modules = forms.ModelMultipleChoiceField(
        queryset=Module.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Modules",
        help_text="Select the modules this user can access."
    )

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'branch', 'groups', 'modules', 'password1', 'password2'
        )

    def save(self, commit=True):
        user = super().save(commit=commit)  # Save user if commit=True, otherwise return unsaved user

        if commit:
            # Save branch
            branch = self.cleaned_data.get('branch')
            customuser, created = CustomUser.objects.get_or_create(user=user)
            customuser.branch = branch
            customuser.save()

            # Save groups
            groups = self.cleaned_data.get('groups')
            if groups:
                user.groups.set(groups)

            # Save modules
            modules = self.cleaned_data.get('modules')
            UserModuleAccess.objects.filter(user=user).delete()
            for module in modules:
                UserModuleAccess.objects.create(user=user, module=module)

        return user


class CustomUserEditForm(UserChangeForm):
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=True,
        label="Branch"
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Groups"
    )
    modules = forms.ModelMultipleChoiceField(
        queryset=Module.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Modules"
    )

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'branch', 'groups', 'modules', 'is_active', 'is_staff'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password', None)

        if self.instance:
            if hasattr(self.instance, 'customuser'):
                self.fields['branch'].initial = self.instance.customuser.branch
            self.fields['groups'].initial = self.instance.groups.all()
            self.fields['modules'].initial = UserModuleAccess.objects.filter(
                user=self.instance
            ).values_list('module', flat=True)

    def save(self, commit=True):
        user = super().save(commit=commit)

        # Save branch
        branch = self.cleaned_data.get('branch')
        customuser, created = CustomUser.objects.get_or_create(user=user)
        customuser.branch = branch
        if commit:
            customuser.save()

        # Save groups
        groups = self.cleaned_data.get('groups')
        if groups is not None:
            user.groups.set(groups)

        # Save modules
        modules = self.cleaned_data.get('modules')
        if modules is not None:
            UserModuleAccess.objects.filter(user=user).delete()
            for module in modules:
                UserModuleAccess.objects.create(user=user, module=module)

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
