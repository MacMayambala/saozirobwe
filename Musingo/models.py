from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from Customer.models import Customer




class DocumentCustody(models.Model):
    DOCUMENT_TYPES = [
        ('ID', 'Identification Document'),
        ('Land TITLE', 'Land Title'),
        ('Plot Agreement', 'Plot Agreement'),
        ('Will', 'Will'),
        ('Academic Document', 'Academic Document'),
        ('OTHER', 'Other'),
    ]
    STORAGE_REASONS = [
        ('COLLATERAL', 'Collateral'),
        ('DOCUMENT CUSTODY', 'Document Custody'),
        ('OTHER', 'Other'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('available', 'Available'),
        ('requested', 'Requested'),
        ('released', 'Released'),
        ('branch', 'At Branch'),
        ('authorised', 'Authorised'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    storage_reason = models.CharField(max_length=20, choices=STORAGE_REASONS)
    document_description = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey(User, related_name='received_documents', on_delete=models.SET_NULL, null=True)
    date_received = models.DateTimeField(default=timezone.now)
    next_of_kin_name = models.CharField(max_length=200, blank=True, null=True)
    next_of_kin_phone = models.CharField(max_length=20, blank=True, null=True)
    next_of_kin_relationship = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    acknowledged_by = models.ForeignKey(User, related_name='acknowledged_documents', on_delete=models.SET_NULL, null=True, blank=True)
    date_acknowledged = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, related_name='approved_documents', on_delete=models.SET_NULL, null=True, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)
    requested_by = models.ForeignKey(User, related_name='requested_documents', on_delete=models.SET_NULL, null=True, blank=True)
    date_requested = models.DateTimeField(null=True, blank=True)
    authorised_by = models.ForeignKey(User, related_name='authorised_documents', on_delete=models.SET_NULL, null=True, blank=True)
    date_authorised = models.DateTimeField(null=True, blank=True)
    released_by = models.ForeignKey(User, related_name='released_documents', on_delete=models.SET_NULL, null=True, blank=True)
    date_released = models.DateTimeField(null=True, blank=True)
    collected_by = models.ForeignKey(User, related_name='collected_documents', on_delete=models.SET_NULL, null=True, blank=True)
    delivered_by = models.ForeignKey(User, related_name='delivered_documents', on_delete=models.SET_NULL, null=True, blank=True)
    date_delivered = models.DateTimeField(null=True, blank=True)
    returned_to_name = models.CharField(max_length=200, blank=True, null=True)
    returned_to_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.get_document_type_display()} for {self.customer}"
    


###########################################################################################
class DocumentActionLog(models.Model):
    ACTION_TYPES = [
        ('REQUEST', 'Request'),
        ('ACKNOWLEDGE', 'Acknowledge'),
        ('APPROVE', 'Approve'),
        ('AUTHORISE', 'Authorise'),
        ('RELEASE', 'Release'),
        ('DELIVER', 'Deliver'),
        ('RETURN', 'Return'),
        ('REVERSE', 'Reverse'),
    ]
    document = models.ForeignKey(DocumentCustody, on_delete=models.CASCADE, related_name='action_logs')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    comment = models.TextField()
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    performed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.get_action_type_display()} for {self.document} by {self.performed_by} at {self.performed_at}"