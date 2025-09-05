# group_lending/forms.py
from django import forms
from .models import GroupMember, GroupSavings, LoanGroup, GroupLoan, MemberLoanAllocation
from Loans.models import Loan, Repayment

# Groups/forms.py
from django import forms
from .models import LoanGroup
from Customer.models import Customer

# Groups/forms.py
from django import forms
from django.db import models
from .models import LoanGroup
from Customer.models import Customer

class LoanGroupForm(forms.ModelForm):
    leader = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control select2-leader', 'placeholder': 'Search by name or member number'})
    )
    members = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control select2-members', 'placeholder': 'Search members by name or member number'})
    )

    class Meta:
        model = LoanGroup
        fields = ['name', 'leader', 'members', 'meeting_day', 'meeting_frequency', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter group name'}),
            'meeting_day': forms.Select(attrs={'class': 'form-select'}),
            'meeting_frequency': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter meeting location'}),
        }

    def clean_leader(self):
        leader_query = self.cleaned_data.get('leader')
        if not leader_query:
            return None
        try:
            leader = Customer.objects.filter(
                models.Q(first_name__icontains=leader_query) |
                models.Q(surname__icontains=leader_query) |
                models.Q(member_number__icontains=leader_query)
            ).first()
            if not leader:
                raise forms.ValidationError("No customer found matching the provided name or member number.")
            return leader
        except Customer.DoesNotExist:
            raise forms.ValidationError("Invalid customer selected.")

    def clean_members(self):
        members_query = self.cleaned_data.get('members')
        if not members_query:
            return []
        try:
            member_ids = members_query.split(',')
            members = Customer.objects.filter(id__in=[id.strip() for id in member_ids if id.strip().isdigit()])
            if not members:
                raise forms.ValidationError("No valid members selected.")
            return members
        except Exception:
            raise forms.ValidationError("Invalid member selection.")
class GroupMemberForm(forms.ModelForm):
    class Meta:
        model = GroupMember
        fields = ['group', 'customer', 'role']

class GroupLoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['amount', 'interest_rate', 'term_months', 'disbursement_date', 'maturity_date']
        widgets = {
            'disbursement_date': forms.DateInput(attrs={'type': 'date'}),
            'maturity_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, group, commit=True):
        loan = super().save(commit=False)
        loan.status = 'active'
        if commit:
            loan.save()
            GroupLoan.objects.create(group=group, loan=loan)
            members = group.members.filter(is_active=True)
            if members:
                per_member = loan.amount / members.count()
                for member in members:
                    MemberLoanAllocation.objects.create(
                        group_loan=GroupLoan.objects.get(loan=loan),
                        member=member.customer,
                        allocated_amount=per_member
                    )
        return loan

class GroupSavingsForm(forms.ModelForm):
    class Meta:
        model = GroupSavings
        fields = ['amount', 'contribution_date', 'contributor']
        widgets = {'contribution_date': forms.DateInput(attrs={'type': 'date'})}

class RepaymentForm(forms.ModelForm):
    class Meta:
        model = Repayment
        fields = ['loan', 'amount', 'payment_date', 'member', 'received_by']
        widgets = {'payment_date': forms.DateInput(attrs={'type': 'date'})}



# Groups/forms.py
from django import forms
from Customer.models import Customer

class AddGroupMembersForm(forms.Form):
    members = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean_members(self):
        member_ids = self.data.getlist('members')
        if member_ids:
            try:
                members = Customer.objects.filter(cus_id__in=member_ids)
                if len(members) != len(member_ids):
                    raise forms.ValidationError("One or more selected members are invalid.")
                return member_ids
            except Customer.DoesNotExist:
                raise forms.ValidationError("Invalid members selected.")
        return []

    def clean(self):
        cleaned_data = super().clean()
        member_ids = cleaned_data.get('members')
        if member_ids and hasattr(self, 'group'):
            if self.group.leader and self.group.leader.cus_id in member_ids:
                raise forms.ValidationError("The group leader cannot be added as a member.")
        return cleaned_data

    def save(self, group, commit=True):
        self.group = group  # Store group for clean method
        member_ids = self.cleaned_data.get('members')
        if member_ids and commit:
            members = Customer.objects.filter(cus_id__in=member_ids)
            group.members.add(*members)
        return group