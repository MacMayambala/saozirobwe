# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Module

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    modules = forms.ModelMultipleChoiceField(
        queryset=Module.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Modules"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "is_staff", "is_active")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # assign modules
            for module in self.cleaned_data.get("modules", []):
                user.usermoduleaccess_set.create(module=module)
        return user

class CustomUserEditForm(UserChangeForm):
    password = None  # hide password field
    email = forms.EmailField(required=True)
    modules = forms.ModelMultipleChoiceField(
        queryset=Module.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Modules"
    )

    class Meta:
        model = User
        fields = ("username", "email", "is_staff", "is_active")

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)
        if user_instance:
            self.fields["modules"].initial = [m.module for m in user_instance.usermoduleaccess_set.all()]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # update modules
            user.usermoduleaccess_set.all().delete()
            for module in self.cleaned_data.get("modules", []):
                user.usermoduleaccess_set.create(module=module)
        return user
################################################################################################################
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
