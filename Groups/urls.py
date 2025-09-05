# group_lending/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create-group/', views.create_group, name='create_group'),
    path('group-list/', views.group_list, name='group_list'),
    path('<int:group_id>/', views.group_detail, name='group_detail'),
    path('customer/search/', views.customer_search, name='customer_search'),
    path('<int:group_id>/add-members/', views.add_group_members, name='add_group_members'),
    
]