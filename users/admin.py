from django.contrib import admin

# Register your models here.from .models import Registration

from .models import UserModuleAccess,Module

# Register your models here.
admin.site.register(UserModuleAccess)
admin.site.register(Module)