from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Position, Staff, Target

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_per_page = 20

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_per_page = 20



# staff_management/admin.py

from django.contrib import admin
from .models import Branch

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at')
    search_fields = ('code', 'name')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = (
         'full_name', 'email', 'phone',
        'gender', 'department', 'position', 'created_at', 'photo_preview'
    )
    list_filter = ('department', 'position', 'gender', 'marital_status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'employee_code')
    list_per_page = 20
    readonly_fields = ('created_at', 'photo_preview')

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'

    def photo_preview(self, obj):
        if obj.passport_photo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />',
                obj.passport_photo.url
            )
        return "No photo"
    photo_preview.short_description = 'Passport Photo'

    fieldsets = (
        (None, {
            'fields': (
                'user', 'employee_code', 'first_name', 'last_name', 'email', 'phone_number'
            )
        }),
        ('Personal Details', {
            'fields': (
                'date_of_birth', 'gender', 'marital_status', 'nationality', 'religion'
            )
        }),
        ('Employment Info', {
            'fields': ('position', 'department', 'contract_type', 'date_hired', 'workstation')
        }),
        ('Photo', {'fields': ('passport_photo',)}),
        ('Metadata', {
            'fields': ('created_at', 'photo_preview'),
            'classes': ('collapse',)
        }),
    )

# staff_management/admin.py


# staff_management/admin.py
from django.contrib import admin
from .models import Target, Staff, StaffTargetType, TargetTransaction

@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = (
        'staff', 'get_target_type_description', 'goal_value', 'current_value',
        'completion_percentage_display', 'start_date', 'end_date', 'created_at'
    )
    list_filter = ('staff', 'target_type', 'start_date', 'end_date')
    search_fields = ('target_type__stname', 'target_type__description', 'staff__first_name', 'staff__last_name', 'staff__employee_code')
    list_per_page = 20
    readonly_fields = ('created_at', 'completion_percentage_display')

    def get_target_type_description(self, obj):
        return obj.target_type.description if obj.target_type.description else "N/A"
    get_target_type_description.short_description = 'Description'

    def completion_percentage_display(self, obj):
        return f"{obj.completion_percentage:.1f}%"
    completion_percentage_display.short_description = 'Progress'

    fieldsets = (
        (None, {'fields': ('staff', 'target_type')}),
        ('Target Details', {
            'fields': ('goal_value', 'current_value', 'start_date', 'end_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'completion_percentage_display'),
            'classes': ('collapse',)
        }),
    )


# admin.py
from django.contrib import admin
from .models import Leave, SystemSetting

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('staff', 'leave_type', 'start_date', 'end_date', 'status')

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('allow_backdate',)
