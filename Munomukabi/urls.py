from django.contrib import admin
from django.urls import path
from .views import register_member

from . import views  # Import views from the same app
from django.urls import path
from .views import serve_member, served_members_report
from .views import member_list,update_member,search_member

urlpatterns = [
    path('members/', views.member_list, name='members'),
    path('search-members/', views.search_members, name='search_members'), # Search for members
    path('members/<int:member_id>/', views.memberSum, name='memberSum'),
    #path('serve-member/<str:customer_id>/', serve_member, name='serve_member'),
    #path("search_member/", search_member, name="search_member"),  # Search for a member by account number
    path('serve-member/<int:member_id>/', views.serve_member, name='serve_member'),
    path('served-members-report/', served_members_report, name='served_members_report'),
    path("register/", register_member, name="registermunomukabi"),  # Register a member
    path("update_member/", update_member, name="update_member"),
    path('search-members/', search_member, name='search_members'),
    #path("filter-members/", views.filter_members, name="filter_members"),
    #path("export-members-excel/",views. export_members_to_excel, name="export_members_to_excel"),
    #path("export-members-pdf/", views.export_members_to_pdf, name="export_members_to_pdf"),
    path('munomukabi/',views.members_list, name='members_lists'),
    path('registermuno/', views.member_register, name='member_register'),  # For new registrations
    path('registermuno/<int:cus_id>/', views.register_muno, name='register_muno'),  # For existing customers
    path('cron-status/', views.cron_status_view, name='cron_status'),
    path('start-cron/', views.start_cron_job, name='start_cron'),
    path('cron-status-api/', views.cron_status_api, name='cron_status_api'),
     path('served-members-report/export-csv/', served_members_report, name='served_members_export_csv'),
    path('served-members-report/export-pdf/', served_members_report, name='served_members_export_pdf'),

    path('muno/', views.munolist, name='mono_list'),
    #path('filter-members/', views.filter_members, name='filter_members'),
    path('munomukabi/<int:member_id>/', views.view_member_details, name='mun_detail'),
    path('member/<int:member_id>/renew/', views.renew_sub, name='renew_sub'),
    path('filter-members/', views.members_list, name='members_list'),
    path('export-members-to-excel/', views.members_list, name='export_members_to_excel'),
    path('export-members-to-pdf/', views.members_list, name='export_members_to_pdf'),
     
]



