from django.contrib import admin
from .models import Customer, DocumentCustody

@admin.register(DocumentCustody)
class DocumentCustodyAdmin(admin.ModelAdmin):
    list_display = ('customer', 'document_type', 'storage_reason', 'status', 'date_received')
    list_filter = ('status', 'document_type', 'storage_reason')
    search_fields = ('customer__member_number', 'customer__first_name', 'customer__surname')