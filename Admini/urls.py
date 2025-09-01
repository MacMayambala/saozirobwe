from django.contrib import admin
from django.urls import include, path
from users.views import user_list
from django.contrib.auth import views as auth_views
from . import views
from django.urls import path
from .views import custom_logout

urlpatterns = [
    path('dashboard/', views.home, name='home'),  # Added trailing slash for consistency
    path('reports/', views.reports, name='reports'),
    path('audit-trails/', views.audit_trails, name='audit_trails'),
    #path('settings/', views.settings, name='settings'),
    path('cron-management/', views.cron_management, name='cron_management'),
    
    
    
    
    # Test URL to verify routing
    #path('test/', views.test_view, name='test_view'),
]

from django.conf.urls import handler404
from .views import custom_404_view

handler404 = 'Admini.custom_404_view'
