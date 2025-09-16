from django.db import models

# Create your models here.

from django.db import models
from Customer.models import Customer

class Loan(models.Model):
    LOAN_STATUS = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('arrears', 'In Arrears'),
        ('defaulted', 'Defaulted'),
    ]

    borrower = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='loans', null=True, blank=True
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()
    disbursement_date = models.DateField(null=True, blank=True)
    maturity_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='pending')
    created_on = models.DateTimeField(auto_now_add=True)

    def outstanding_balance(self):
        paid = sum(p.amount for p in self.repayments.all())
        return max(0, self.amount - paid)

    def days_in_arrears(self):
        from django.utils.timezone import now
        if self.status in ['arrears', 'defaulted'] and self.maturity_date and self.outstanding_balance() > 0:
            return (now().date() - self.maturity_date).days
        return 0

    def __str__(self):
        return f"Loan {self.id} - {self.amount} ({self.status})"

class Repayment(models.Model):
    loan = models.ForeignKey(Loan, related_name='repayments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    received_by = models.CharField(max_length=255, null=True, blank=True)
    member = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"Repayment {self.amount} for Loan {self.loan.id}"