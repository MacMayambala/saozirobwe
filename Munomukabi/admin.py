# admin.py
from django.contrib import admin
from .models import Member,Village,Parish,Zone,ServedMember


# Register your models here.
admin.site.register(Village)
admin.site.register(Parish)
admin.site.register(Zone)
admin.site.register(Member)
admin.site.register(ServedMember)


