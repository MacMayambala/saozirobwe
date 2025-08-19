from django.urls import path
from . import views

app_name = 'staff_management'

urlpatterns = [
    #path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/add/', views.add_staff, name='add_staff'),
    # path('staff/<int:staff_id>/add_target/', views.add_target, name='add_target'),
    # path('staff/<int:staff_id>/performance/', views.view_performance, name='view_performance'),
   
    path('staff/add_department/', views.add_department, name='add_department'),
    path('add-branch/', views.add_branch, name='add_branch'),
    
    path('position/add/', views.add_position, name='add_position'),
    path('department/add/', views.add_department, name='add_department'),
    path('target/<int:target_id>/update/', views.update_target, name='update_target'),
    path('target/<int:target_id>/delete/', views.delete_target, name='delete_target'),

    # Staff target type URLs - with proper views. prefix
    
    path('target-types/', views.staff_target_type_list, name='staff_target_type_list'),
    path('target-types/create/', views.staff_target_type_create, name='staff_target_type_create'),
    path('target-types/<int:pk>/', views.staff_target_type_detail, name='staff_target_type_detail'),
    path('target-types/<int:pk>/update/', views.staff_target_type_update, name='staff_target_type_update'),
    path('target-types/<int:pk>/delete/', views.staff_target_type_delete, name='staff_target_type_delete'),

    path('staff/', views.staff_dashboard, name='staff_dashboard'),  # Root URL for dashboard
    path('search/', views.search_staff, name='search_staff'),
    path('add/', views.add_staff, name='add_staff'),
    path('add-target/<int:staff_id>/', views.add_target, name='add_target'),
    path('performance/<int:staff_id>/', views.view_performance, name='view_performance'),
    path('update/<int:staff_id>/', views.update_staff, name='update_staff'),
    path('target/<int:target_id>/edit_goal/', views.edit_target_goal, name='edit_target_goal'),
    path('staff/<int:staff_id>/leave-management/', views.leave_management, name='leave_management'),
    
   
]