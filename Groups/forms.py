from django import forms
from django.db.models import Q
from .models import AuditLog, LoanGroup, GroupMember, GroupLoan, MemberLoanAllocation, GroupSavings
from Customer.models import Customer
from Loans.models import Loan, Repayment
from decimal import Decimal

from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import AuditLog, LoanGroup, GroupMember
from Customer.models import Customer

class LoanGroupForm(forms.ModelForm):
    group_leader = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'groupLeaderInput'})
    )
    members = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'membersInput'})
    )

    class Meta:
        model = LoanGroup
        fields = ['name', 'group_leader', 'members', 'meeting_day', 'meeting_frequency', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter group name'}),
            'meeting_day': forms.Select(attrs={'class': 'form-select'}),
            'meeting_frequency': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter meeting location'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_group_leader(self):
        group_leader_id = self.cleaned_data.get('group_leader')
        if group_leader_id:
            try:
                group_leader = Customer.objects.get(cus_id=group_leader_id)
                return group_leader
            except Customer.DoesNotExist:
                raise ValidationError("Selected group leader does not exist.")
        return None

    def clean_members(self):
        members_str = self.cleaned_data.get('members')
        if not members_str:
            return []

        member_ids = members_str.split(',')
        member_ids = [id.strip() for id in member_ids if id.strip()]
        try:
            members = Customer.objects.filter(cus_id__in=member_ids)
            if len(members) != len(member_ids):
                raise ValidationError("One or more selected members do not exist.")
            return list(members)
        except ValueError:
            raise ValidationError("Invalid member IDs provided.")

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        group_leader = cleaned_data.get('group_leader')
        members = cleaned_data.get('members')

        if LoanGroup.objects.filter(name=name).exclude(id=self.instance.id).exists():
            self.add_error('name', 'A group with this name already exists.')

        if group_leader and members and group_leader in members:
            self.add_error('members', 'The group leader cannot be added as a regular member.')

        if members:
            member_ids = set(m.cus_id for m in members)
            if len(member_ids) != len(members):
                self.add_error('members', 'Duplicate members selected.')

        return cleaned_data

    def save(self, commit=True):
        group = super().save(commit=False)
        group_leader = self.cleaned_data.get('group_leader')
        if group_leader:
            group.group_leader = group_leader
        if commit:
            group.save()
            for member in self.cleaned_data['members']:
                GroupMember.objects.create(group=group, customer=member, role='member')
                AuditLog.objects.create(
                    action=f'Added member {member.first_name} {member.surname} to group {group.name}',
                    user=self.request.user if self.request else None,
                    group=group
                )
        return group

class AddGroupMembersForm(forms.Form):
    members = forms.ModelMultipleChoiceField(
        queryset=Customer.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2', 'multiple': 'multiple'}),
        to_field_name='cus_id'
    )

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_members(self):
        members = self.cleaned_data.get('members')
        if not members:
            return []

        existing_members = set(self.group.members.values_list('customer__cus_id', flat=True))
        new_member_ids = set(m.cus_id for m in members)
        if existing_members.intersection(new_member_ids):
            raise forms.ValidationError("One or more selected members are already in the group.")

        if self.group.leader and self.group.leader.cus_id in new_member_ids:
            raise forms.ValidationError("The group leader cannot be added as a regular member.")

        return members

    def save(self, commit=True):
        members = self.cleaned_data.get('members')
        if members and commit:
            for member in members:
                GroupMember.objects.create(group=self.group, customer=member, role='member')
                AuditLog.objects.create(
                    action=f'Added member {member.first_name} {member.surname} to group {self.group.name}',
                    user=self.request.user if self.request else None,
                    group=self.group
                )
        return self.group

class GroupLoanForm(forms.ModelForm):
    allocations = forms.JSONField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Loan
        fields = ['amount', 'interest_rate', 'term_months', 'disbursement_date', 'maturity_date']
        widgets = {
            'disbursement_date': forms.DateInput(attrs={'type': 'date'}),
            'maturity_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_allocations(self):
        allocations = self.cleaned_data.get('allocations')
        total_amount = self.cleaned_data.get('amount')

        if not allocations:
            raise forms.ValidationError("Loan allocations must be provided.")

        total_allocated = sum(Decimal(str(alloc['amount'])) for alloc in allocations)
        if abs(total_allocated - Decimal(str(total_amount))) > Decimal('0.01'):
            raise forms.ValidationError("Total allocated amount must equal the loan amount.")

        member_ids = [alloc['member_id'] for alloc in allocations]
        members = Customer.objects.filter(
    cus_id__in=member_ids,
    group_memberships__group=self.group,
    group_memberships__is_active=True
)

        if len(members) != len(member_ids):
            raise forms.ValidationError("One or more selected members are not active in this group.")

        return allocations
    

    def save(self, commit=True):
        loan = super().save(commit=False)
        loan.status = 'active'
        if commit:
            loan.save()
            group_loan = GroupLoan.objects.create(group=self.group, loan=loan)
            for alloc in self.cleaned_data['allocations']:
                member = Customer.objects.get(cus_id=alloc['member_id'])
                MemberLoanAllocation.objects.create(
                    group_loan=group_loan,
                    member=member,
                    allocated_amount=alloc['amount'],
                    status='performing'
                )
                AuditLog.objects.create(
                    action=f'Allocated {alloc["amount"]} to {member.first_name} {member.surname} for loan {loan.id}',
                    user=self.request.user if self.request else None,
                    group=self.group,
                    loan=loan
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