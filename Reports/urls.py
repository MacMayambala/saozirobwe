from django.urls import path
from .views import (
    members_in_date_range, 
    active_subscriptions, 
    expired_subscriptions, 
    all_members_with_subscription_status, export_members_to_excel,export_members_to_pdf, user_activity_report,member,search_activities
)

urlpatterns = [
    path('reports/members-in-date-range/', members_in_date_range, name="member_list"),
    path('reports/active-subscriptions/', active_subscriptions, name="active_subscriptions"),
    path('reports/expired-subscriptions/', expired_subscriptions, name="expired_subscriptions"),
    path('reports/all-members/', all_members_with_subscription_status, name="all_members"),
    
    path('user-activity/', user_activity_report, name='user_activity_report'),
    path('search-activities/', search_activities, name='search_activities'),
    
    
]
