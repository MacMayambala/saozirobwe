from django.contrib import admin
from .models import Delegate, Target, Transaction, TargetType

@admin.register(TargetType)
class TargetTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)

@admin.register(Delegate)
class DelegateAdmin(admin.ModelAdmin):
    list_display = ('customer', 'assigned_date', 'is_active')
    list_filter = ('is_active', 'customer__branch')
    search_fields = ('customer__first_name', 'customer__surname', 'customer__cus_id')

@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('delegate', 'description', 'target_type', 'target_value', 'start_date', 'end_date')
    list_filter = ('target_type', 'delegate__customer__branch')
    search_fields = ('description',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('delegate', 'actual_value', 'transaction_date', 'target')
    list_filter = ('transaction_date', 'delegate__customer__branch')
    search_fields = ('description',)