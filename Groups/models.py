from django.db import models


##############################################################################################################################################
# group_lending/models.py
from django.db import models
from Customer.models import Customer
from Loans.models import Loan

# group_lending/models.py
from django.db import models
from django.db.models import Sum


class LoanGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateField(auto_now_add=True)
    leader = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='leds_groups'
    )
    meeting_day = models.CharField(max_length=20, choices=[
        ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')
    ], null=True, blank=True)
    meeting_frequency = models.CharField(max_length=20, choices=[
        ('weekly', 'Weekly'), ('biweekly', 'Biweekly'), ('monthly', 'Monthly')
    ], default='weekly')
    location = models.CharField(max_length=255, null=True, blank=True)

    def active_loan(self):
        return self.group_loans.filter(loan__status__in=['active', 'arrears']).first()

    def portfolio_value(self):
        loan = self.active_loan()
        return loan.loan.outstanding_balance() if loan else 0

    def arrears_days(self):
        loan = self.active_loan()
        return loan.loan.days_in_arrears() if loan else 0

    def total_savings(self):
        result = self.savings.aggregate(total=Sum('amount'))
        return result['total'] or 0

    def __str__(self):
        return self.name
class GroupMember(models.Model):
    group = models.ForeignKey(LoanGroup, related_name='members', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[
        ('chairperson', 'Chairperson'), ('treasurer', 'Treasurer'), ('member', 'Member')
    ], default='member')
    joined_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('group', 'customer')

    def __str__(self):
        return f"{self.customer.first_name} {self.customer.surname}({self.role})"

class GroupLoan(models.Model):
    group = models.ForeignKey(LoanGroup, related_name='group_loans', on_delete=models.CASCADE)
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE)

    def __str__(self):
        return f"Loan {self.loan.id} for {self.group.name}"

class MemberLoanAllocation(models.Model):
    group_loan = models.ForeignKey(GroupLoan, related_name='allocations', on_delete=models.CASCADE)
    member = models.ForeignKey(Customer, on_delete=models.CASCADE)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2)
    repaid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[
        ('performing', 'Performing'), ('arrears', 'In Arrears')
    ], default='performing')

    def outstanding_balance(self):
        return max(0, self.allocated_amount - self.repaid_amount)

    def __str__(self):
        return f"{self.member.first_name} {self.member.surname}  - {self.allocated_amount} ({self.status})"

class GroupSavings(models.Model):
    group = models.ForeignKey(LoanGroup, related_name='savings', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    contribution_date = models.DateField()
    contributor = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"Savings {self.amount} for {self.group.name}"
    
####################################################################################################################
class AuditLog(models.Model):
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(LoanGroup, on_delete=models.CASCADE, null=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.action} at {self.timestamp}"
    

# Groups/models.py
from django.db import models
from Customer.models import Customer

class Group(models.Model):
    name = models.CharField(max_length=100)
    leader = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='led_groups')
    members = models.ManyToManyField(Customer, related_name='groups', blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"

    def __str__(self):
        return self.name