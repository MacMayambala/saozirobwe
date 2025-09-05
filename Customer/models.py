from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from datetime import datetime
import os

class Customer(models.Model):
    cus_id = models.CharField(max_length=9, primary_key=True, unique=True, editable=False)

    def upload_to_profile(instance, filename):
        return os.path.join('profiles', instance.cus_id, filename)
    
    def upload_to_signature(instance, filename):
        return os.path.join('signatures', instance.cus_id, filename)
    
    def upload_to_id_scan(instance, filename):
        return os.path.join('id_scans', instance.cus_id, filename)

    profile_picture = models.ImageField(
        upload_to=upload_to_profile,
        blank=True,
        null=True,
        verbose_name="Profile Photo"
    )
    signature_photo = models.ImageField(
        upload_to=upload_to_signature,
        blank=True,
        null=True,
        verbose_name="Signature Photo"
    )
    id_scan = models.ImageField(
        upload_to=upload_to_id_scan,
        blank=True,
        null=True,
        verbose_name="Identity Card Photo"
    )

    @property
    def age(self):
        if self.dob:
            today = datetime.now().date()
            age = today.year - self.dob.year
            if today.month < self.dob.month or (today.month == self.dob.month and today.day < self.dob.day):
                age -= 1
            return age
        return None

    branch = models.ForeignKey('staff_management.Branch', on_delete=models.CASCADE, related_name='customers')
    mem_reg_date = models.DateField()
    member_number = models.CharField(max_length=14, unique=True)
    email = models.EmailField(max_length=254, blank=True, null=True)

    SALUTATION_CHOICES = [('Mr', 'Mr'), ('Miss', 'Miss'), ('Mrs', 'Mrs')]
    salutation = models.CharField(max_length=4, choices=SALUTATION_CHOICES)
    first_name = models.CharField(max_length=50, validators=[MinLengthValidator(2)])
    middle_name1 = models.CharField(max_length=50, blank=True, null=True)
    middle_name2 = models.CharField(max_length=50, blank=True, null=True)
    surname = models.CharField(max_length=50, validators=[MinLengthValidator(2)])
    GENDER_CHOICES = [('Female', 'Female'), ('Male', 'Male')]
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    MARITAL_STATUS_CHOICES = [('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced')]
    marital_status = models.CharField(max_length=8, choices=MARITAL_STATUS_CHOICES)
    is_pwd = models.BooleanField(default=False)
    dob = models.DateField()
    HOME_OWNERSHIP_CHOICES = [('Owned', 'Owned'), ('Rented', 'Rented')]
    home_ownership = models.CharField(max_length=6, choices=HOME_OWNERSHIP_CHOICES)
    id_number = models.CharField(max_length=12, blank=True, null=True)

    # id_number = models.CharField(
    #     max_length=14,
    #     unique=True,
    #     validators=[
    #         RegexValidator(
    #             regex=r'^(CF|CM)[A-Z0-9]{11}[A-Z]$',
    #             message="ID number must be exactly 14 characters, start with 'CF' or 'CM', and end with a letter."
    #         )
    #     ]
    # )
    card_number = models.CharField(max_length=20, unique=True)
    nin_village = models.CharField(max_length=100, blank=True, null=True)
    nin_parish = models.CharField(max_length=100, blank=True, null=True)
    nin_s_county = models.CharField(max_length=100, blank=True, null=True)
    nin_county = models.CharField(max_length=100, blank=True, null=True)
    nin_district = models.CharField(max_length=100, blank=True, null=True)

    # phone = models.CharField(
    #     max_length=12,
    #     validators=[
    #         RegexValidator(
    #             regex=r'^256\d{9}$',
    #             message="Phone number must be exactly 12 digits, starting with '256'."
    #         )
    #     ]
    # )
    phone = models.CharField(max_length=12, blank=True, null=True)
    phone_number2 = models.CharField(max_length=12, blank=True, null=True)
    # phone_number2 = models.CharField(
    #     max_length=12,
    #     blank=True,
    #     null=True,
    #     validators=[
    #         RegexValidator(
    #             regex=r'^256\d{9}$',
    #             message="Phone number must be exactly 12 digits, starting with '256'."
    #         )
    #     ]
    # )

    village = models.CharField(max_length=100, blank=True, null=True)
    parish = models.CharField(max_length=100, blank=True, null=True)
    s_county = models.CharField(max_length=100, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    SAO_ZONE_CHOICES = [
        ('Bamunanika', 'Bamunanika'), ('Bukimu', 'Bukimu'), ('Busiika-Main', 'Busiika-Main'),
        ('Collective-A', 'Collective-A'), ('Collective-B', 'Collective-B'),
        ('Kabulanaka-Ngalonkalu', 'Kabulanaka_Ngalonkalu'), ('Kakakala', 'Kakakala'),
        ('Kikyusa', 'Kikyusa'), ('Kyetume-Bubbuubi', 'Kyetume-Bubbuubi'),
        ('Namawojja', 'Namawojja'), ('Sekamuli', 'Sekamuli'),
    ]
    sao_zone = models.CharField(max_length=50, choices=SAO_ZONE_CHOICES)

    kin_sname = models.CharField(max_length=50, validators=[MinLengthValidator(2)])
    kin_fname = models.CharField(max_length=50, validators=[MinLengthValidator(2)])
    kin_sname2 = models.CharField(max_length=50, blank=True, null=True)
    kin_phone = models.CharField(max_length=12, blank=True, null=True)
    # kin_phone = models.CharField(
    #     max_length=12,
    #     validators=[
    #         RegexValidator(
    #             regex=r'^256\d{9}$',
    #             message="Phone number must be exactly 12 digits, starting with '256'."
    #         )
    #     ]
    # )
    kin_address = models.CharField(max_length=200, blank=True, null=True)
    kin_relationship = models.CharField(max_length=50, blank=True, null=True)

    employment = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    employer_name = models.CharField(max_length=100, blank=True, null=True)
    employer_address = models.CharField(max_length=200, blank=True, null=True)
    employer_phone1 = models.CharField(max_length=15, blank=True, null=True)
    employer_phone2 = models.CharField(max_length=15, blank=True, null=True)
    income_frequency = models.CharField(max_length=50, blank=True, null=True)
    income_per_month = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.cus_id} - {self.first_name} {self.surname}"

    def save(self, *args, **kwargs):
        # Auto-generate cus_id if not set
        if not self.cus_id:
            branch_code = self.branch.code.strip() if self.branch and self.branch.code else '0'
            if len(branch_code) > 1:
                branch_code = branch_code[0]
            year_suffix = datetime.now().year % 100
            last_customer = Customer.objects.filter(
                cus_id__startswith=f"{branch_code}{year_suffix:02d}"
            ).order_by('-cus_id').first()
            if last_customer:
                last_number = int(last_customer.cus_id[-5:]) + 1
            else:
                last_number = 1
            self.cus_id = f"{branch_code}{year_suffix:02d}{str(last_number).zfill(5)}"
        # ✅ ID number validation: only accept 14 characters, otherwise NULL
        if self.id_number and len(str(self.id_number)) != 14:
           self.id_number = None

        # ✅ Phone validation: only accept 12 characters, otherwise NULL
        for field in ['phone', 'phone_number2', 'kin_phone']:
            value = getattr(self, field)
            if value and len(str(value)) != 12:
                setattr(self, field, None)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cus_id} - {self.first_name} {self.surname}"