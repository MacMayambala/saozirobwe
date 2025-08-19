from django.db import models
from django.db import models
from datetime import timedelta
from django.utils import timezone
import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
#
from Customer.models import Customer 




# Munomukabi/models.py
from django.db import models
import django.utils.timezone as timezone
from django.contrib.auth.models import User  # Import User model




class Zone(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Parish(models.Model):
    name = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Village(models.Model):
    name = models.CharField(max_length=100)
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


def validate_future_date(value):
    if value < timezone.localdate():  # Ensure date is today or later
        raise ValidationError("Subscription start date cannot be in the past.")




# munomukabitemp/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

def validate_future_date(value):
    if value > timezone.localdate():
        raise ValidationError("Date cannot be in the future.")

from django.db import models
from django.utils import timezone
from datetime import timedelta

class Member(models.Model):
    customer = models.ForeignKey(
        'Customer.Customer',
        on_delete=models.CASCADE,
        related_name='members',  # Plural to reflect multiple Member records
    )
    # If Customer is in another app (e.g., 'accounts'), use:
    # customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, related_name='members')

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('archived', 'Archived'),  # Added for tracking old records
    )
    LIFE_CHOICES = (
        ('dd', 'Deceased'),
        ('LV', 'Alive'),
    )

    # Existing fields
    subscription_start = models.DateField(blank=True, null=True, validators=[validate_future_date])
    subscription_end = models.DateField(blank=True, null=True)
    renewal_count = models.PositiveIntegerField(default=1)
    last_renewal_date = models.DateField(blank=True, null=True)  # Corrected: removed redundant blank=True

    spouse_name = models.CharField(max_length=100, blank=True, null=True)
    spouse_status = models.CharField(max_length=10, choices=LIFE_CHOICES, blank=True, null=True)  # Added blank/null
    spouse_address = models.CharField(max_length=200, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    mother_village = models.CharField(max_length=100, blank=True, null=True)
    mother_status = models.CharField(max_length=10, choices=LIFE_CHOICES, blank=True, null=True)  # Added blank/null
    mother_guardian = models.CharField(max_length=100, blank=True, null=True)  # Corrected: changed model to models
    mother_guardian_address = models.CharField(max_length=200, blank=True, null=True)  # Corrected: changed model to models
    father_name = models.CharField(max_length=100, blank=True, null=True)  # Corrected: removed duplicate definitions
    father_village = models.CharField(max_length=100, blank=True, null=True)  # Corrected: fixed invalid assignment
    father_status = models.CharField(max_length=10, choices=LIFE_CHOICES, blank=True, null=True)  # Added blank/null
    father_guardian = models.CharField(max_length=100, blank=True, null=True)
    father_guardian_address = models.CharField(max_length=200, blank=True, null=True)
    child1_name = models.CharField(max_length=100, blank=True, null=True)
    child2_name = models.CharField(max_length=100, blank=True, null=True)
    next_of_kin_Name = models.CharField(max_length=100)  # Consider renaming to next_of_kin_name for consistency
    next_of_kin_relationship = models.CharField(max_length=50)
    next_of_kin_village = models.CharField(max_length=100)
    next_of_kin_phone = models.CharField(max_length=20, blank=True, null=True)
    sao_officer = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    # New fields
    payment_date = models.DateField(blank=False, null=False)  # Date of payment
    payment_number = models.CharField(max_length=50, unique=True, blank=False, null=False)  # Unique payment identifier
    booklet_number = models.CharField(max_length=50, unique=True, blank=False, null=False)  # Unique booklet identifier
    teller = models.CharField(max_length=100, blank=False, null=False)  # Name or ID of the teller
    creation_date = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    modification_date = models.DateTimeField(auto_now=True)  # Automatically updated on modification

    def save(self, *args, **kwargs):
        if self.subscription_start and not self.subscription_end:
            self.subscription_end = self.subscription_start + timedelta(days=365)
        self.update_status()
        super().save(*args, **kwargs)

    def is_active_subscription(self):
        return (
            self.subscription_start 
            and self.subscription_end 
            and self.subscription_start <= timezone.localdate() <= self.subscription_end
        )

    def update_status(self):
        if self.subscription_end and timezone.localdate() > self.subscription_end:
            self.status = 'expired'
        elif self.is_active_subscription():
            self.status = 'active'

    def can_renew(self, user):
        if user.is_superuser:
            return True
        if not self.last_renewal_date:
            return True
        one_year_ago = timezone.localdate() - timedelta(days=365)
        return self.last_renewal_date <= one_year_ago

    def __str__(self):
        return f"{self.customer.first_name} {self.customer.surname} - {self.customer.member_number}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['customer'],
                condition=models.Q(status='active'),
                name='unique_active_member_per_customer'
            )
        ]
#################################################################
# Munomukabi/models.py
from django.db import models
from django.utils import timezone

class CronJobStatus(models.Model):
    last_run = models.DateTimeField(null=True, blank=True)
    running = models.BooleanField(default=False)

    def start(self):
        self.running = True
        self.save()

    def finish(self):
        self.running = False
        self.last_run = timezone.now()
        self.save()

    def __str__(self):
        return f"Cron Status: {'Running' if self.running else 'Idle'} (Last: {self.last_run})"




# Munomukabi/models.py
from django.db import models
import django.utils.timezone as timezone
from django.contrib.auth.models import User  # Import User model

class ServedMember(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount_given = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    date_served = models.DateTimeField(default=timezone.now)
    served_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='served_members')

    def __str__(self):
        return f"{self.member.customer.first_name} {self.member.customer.surname} - {self.amount_given} UGX ({self.date_served.date()})"