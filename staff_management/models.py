import re
from django.db import models
from django.core.exceptions import ValidationError
from django.db import models
from django.core.exceptions import ValidationError

from django.db import models
from django.core.exceptions import ValidationError

class Branch(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Branch Code")
    name = models.CharField(max_length=100, unique=True, verbose_name="Branch Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name="Location")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    def clean(self):
        if self.code and not self.code.strip():
            raise ValidationError({"code": "Branch code cannot be empty or just whitespace."})
        if self.name and not self.name.strip():
            raise ValidationError({"name": "Branch name cannot be empty or just whitespace."})
        self.code = self.code.strip()
        self.name = self.name.strip()
        if self.description:
            self.description = self.description.strip()
        if self.location:
            self.location = self.location.strip()

    def save(self, *args, **kwargs):
        self.code = self.code.strip()
        self.name = self.name.strip()
        if self.description:
            self.description = self.description.strip()
        if self.location:
            self.location = self.location.strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
        ordering = ["code"]

class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Position(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
from django.db import models






# staff_management/models.py
from django.db import models
from django.contrib.auth.models import User


class Staff(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)    
    employee_id = models.CharField(max_length=20, unique=False, editable=False)
    staff_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    marital_status = models.CharField(max_length=20, choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed')])
    id_type = models.CharField(max_length=50, choices=[('National ID', 'National ID'), ('Passport', 'Passport')])
    id_number = models.CharField(max_length=50)
    address = models.TextField()
    next_of_kin_name = models.CharField(max_length=100)
    next_of_kin_phone = models.CharField(max_length=20)
    next_of_kin_address = models.TextField()
    relationship = models.CharField(max_length=50, choices=[('Spouse', 'Spouse'), ('Parent', 'Parent'), ('Sibling', 'Sibling'), ('Child', 'Child'), ('Other', 'Other')])
    date_appointed = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[('Bank', 'Bank'), ('Mobile Money', 'Mobile Money'), ('Cash', 'Cash')])
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    ssn = models.CharField(max_length=50, blank=True, null=True)
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    ssf = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    lst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    paye = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    contract_file = models.FileField(upload_to='contracts/', blank=True, null=True)
    signature_file = models.ImageField(upload_to='signatures/', blank=True, null=True)
    id_attachment = models.FileField(upload_to='id_attachments/', blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Added field

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last_staff = Staff.objects.order_by('-id').first()
            if last_staff and last_staff.employee_id and last_staff.employee_id.startswith('Emp'):
                last_number = int(last_staff.employee_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.employee_id = f"Emp{new_number:03d}"
        super().save(*args, **kwargs)
    
##New Staff Taget Type###############################################
class StaffTargetType(models.Model):
    code = models.CharField(max_length=10, unique=True, editable=False, help_text="Auto-generated code in format stt_01")
    stname = models.CharField(max_length=50, unique=True, help_text="e.g., Savings, Shares, Membership")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True, help_text="Last modification timestamp")
    
    class Meta:
        verbose_name = "Target Type"
        verbose_name_plural = "Target Types"
    
    def __str__(self):
        return self.stname
    
    def save(self, *args, **kwargs):
        if not self.code:
            # Get the highest existing code
            last_obj = StaffTargetType.objects.all().order_by('-code').first()
            if last_obj and last_obj.code and re.match(r'stt_\d+', last_obj.code):
                # Extract the number part and increment
                last_num = int(last_obj.code.split('_')[1])
                self.code = f'stt_{last_num+1:02d}'
            else:
                # Start with stt_01 if no existing records or invalid format
                self.code = 'stt_01'
        super().save(*args, **kwargs)




# staff_management/models.py
# staff_management/models.py
from django.db import models
from django.utils import timezone

# staff_management/models.py
from django.db import models
from django.utils import timezone

from django.db import models
from django.utils import timezone

class Target(models.Model):
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, related_name="targets")
    target_type = models.ForeignKey('StaffTargetType', on_delete=models.CASCADE, related_name="targets")
    goal_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    PERIOD_CHOICES = [
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Yearly', 'Yearly'),
    ]
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='Monthly')

    def __str__(self):
        return f"{self.target_type.stname} - {self.staff}"

    @property
    def completion_percentage(self):
        if not self.goal_value or self.goal_value <= 0:
            return 0
        return min((self.current_value / self.goal_value) * 100, 100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['staff', 'target_type'],
                condition=models.Q(end_date__gte=timezone.now().date()),
                name='unique_active_target_per_staff_and_type'
            )
        ]


class TargetTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
    )
    target = models.ForeignKey(Target, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='Deposit')
    actual_value = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField()  # User-specified date
    transdescription = models.CharField(max_length=25, null=False, blank=False)  # Renamed from description
    created_at = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.actual_value} for {self.target} - {self.transdescription} on {self.transaction_date}"



################################################################################################################
# staff_management/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Leave(models.Model):
    staff = models.ForeignKey('Staff', on_delete=models.CASCADE, related_name='leaves')

    leave_type = models.CharField(max_length=50, choices=[
        ('Annual', 'Annual'),
        ('Sick', 'Sick'),
        ('Maternity', 'Maternity'),
        ('Paternity', 'Paternity'),
        ('Other', 'Other')
    ])

    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Reviewed', 'Manager Reviewed'),
        ('HR_Reviewed', 'HR Reviewed'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')

    manager_reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='manager_reviews')
    hr_reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hr_reviews')
    gm_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='gm_approvals')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff.full_name} - {self.leave_type} ({self.status})"

    @property
    def duration(self):
        return (self.end_date - self.start_date).days + 1

    @property
    def remaining_days(self):
        from datetime import date
        today = date.today()
        if self.status == 'Approved' and today <= self.end_date:
            return (self.end_date - today).days + 1
        return 0

    class Meta:
        verbose_name = "Leave"
        verbose_name_plural = "Leaves"
