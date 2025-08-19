from django.db import models
from django.core.validators import MinValueValidator
import uuid
from datetime import datetime, timedelta

class TargetType(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="e.g., Savings, Shares, Membership")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Target Type"
        verbose_name_plural = "Target Types"

    def __str__(self):
        return self.name

class Delegate(models.Model):
    customer = models.ForeignKey('Customer.Customer', on_delete=models.CASCADE, related_name='delegates')
    assigned_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)  # New field for expiration
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Delegate"
        verbose_name_plural = "Delegates"

    def __str__(self):
        return f"Delegate: {self.customer.first_name} {self.customer.surname} ({self.customer.cus_id})"

    def save(self, *args, **kwargs):
        # Set expiry_date to 1 year from assigned_date if not set
        if not self.expiry_date:
            self.expiry_date = self.assigned_date + timedelta(days=365)

        # Update is_active based on expiry_date
        if self.expiry_date and self.expiry_date < datetime.now().date():
            self.is_active = False

        super().save(*args, **kwargs)

class Target(models.Model):
    delegate = models.ForeignKey(Delegate, on_delete=models.CASCADE, related_name='targets')
    description = models.CharField(max_length=200)
    target_type = models.ForeignKey(TargetType, on_delete=models.PROTECT, related_name='targets')
    target_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Target value (e.g., amount in currency, number of shares, or memberships)"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Target"
        verbose_name_plural = "Targets"

    def __str__(self):
        return f"{self.description} ({self.target_type.name}) - {self.delegate.customer.cus_id}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
    ]

    CHANNEL_CHOICES = [
        ('Counter', 'Counter'),
        ('Mobile', 'Mobile Money'),
        ('Bank', 'Bank Transfer'),
        ('Other', 'Other'),
    ]

    delegate = models.ForeignKey('Delegate', on_delete=models.CASCADE, related_name='transactions')
    target = models.ForeignKey('Target', on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)

    actual_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Actual value achieved (e.g., amount, shares, or memberships)"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        default='Deposit'
    )

    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        default='Counter'
    )

    reference = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique transaction reference number"
    )

    balance_after = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Running balance after this transaction"
    )

    transaction_date = models.DateField()
    description = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-transaction_date', '-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.actual_value} for {self.delegate.customer.cus_id}"

    @property
    def achievement_percentage(self):
        if self.target and self.target.target_value > 0:
            return (self.actual_value / self.target.target_value) * 100
        return 0

    def save(self, *args, **kwargs):
        # Generate a unique reference if not set
        if not self.reference:
            self.reference = str(uuid.uuid4()).split('-')[0].upper()

        # Get the latest previous balance
        previous_transaction = Transaction.objects.filter(
            delegate=self.delegate,
            transaction_date__lte=self.transaction_date
        ).exclude(id=self.id).order_by('-transaction_date', '-created_at').first()

        current_balance = previous_transaction.balance_after if previous_transaction and previous_transaction.balance_after else 0

        # Update running balance
        if self.transaction_type == 'Deposit':
            self.balance_after = current_balance + self.actual_value
        elif self.transaction_type == 'Withdrawal':
            self.balance_after = current_balance - self.actual_value

        super().save(*args, **kwargs)


########################################################################################################
from django.db import models

class Term_details(models.Model):
    termId = models.CharField(max_length=50, unique=True, help_text="e.g., Term start year 2023, Q2 2023")
    date_range = models.DateField(help_text="Date range for the term")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    expiry_date = models.DateField(null=False, blank=False, help_text="Expiration date of the term")
    chairperson = models.CharField(max_length=50, help_text="Name of the chairperson")
    secretary = models.CharField(max_length=50, help_text="Name of the secretary")
    vice_chairperson = models.CharField(max_length=50, help_text="Name of the vice chairperson")
    treasurer = models.CharField(max_length=50, help_text="Name of the treasurer")

    class Meta:
        verbose_name = "Term Detail"
        verbose_name_plural = "Term Details"

    def __str__(self):
        return self.termId