from django import forms
from django.contrib.auth.models import User
from .models import DocumentCustody

class DocumentCustodyForm(forms.ModelForm):
    class Meta:
        model = DocumentCustody
        fields = [
            'document_type',
            'storage_reason',
            'document_description',
            'next_of_kin_name',
            'next_of_kin_phone',
            'next_of_kin_relationship',
        ]
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'storage_reason': forms.Select(attrs={'class': 'form-select'}),
            'document_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'next_of_kin_name': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_relationship': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_next_of_kin_phone(self):
        phone = self.cleaned_data.get('next_of_kin_phone')
        if phone and not phone.replace('+', '').isdigit():
            raise forms.ValidationError("Phone number must contain only digits and an optional '+' prefix.")
        return phone

class ReleaseDocumentForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'passwordInput'}),
        label="Confirm Password"
    )
    collected_by = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        required=True,
        label="Collected By",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'collectedByInput'})
    )