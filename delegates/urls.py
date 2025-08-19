from django.urls import path
from . import views

urlpatterns = [
    path('delegates/', views.delegate_list, name='delegate_list'),
    path('delegate/<int:delegate_id>/', views.delegate_detail, name='delegate_detail'),
    path('register-delegate/', views.register_delegate, name='register_delegate'),
    path('register-target/', views.register_target, name='register_target'),
    path('add-target-type/', views.add_target_type, name='add_target_type'),
    path('expire-delegate/<int:delegate_id>/', views.expire_delegate, name='expire_delegate'),
    path('renew-delegate/<int:delegate_id>/', views.renew_delegate, name='renew_delegate'),
    path('add-term-details/', views.add_term_details, name='add_term_details'),
    path('term-details/', views.term_details_list, name='term_details_list'),
    path('edit-term-details/<int:term_id>/', views.edit_term_details, name='edit_term_details'),
    path('delegates/export-delegates-to-excel/', views.delegate_list, name='export_delegates_to_excel'),
    path('delegates/export-delegates-to-pdf/', views.delegate_list, name='export_delegates_to_pdf'),
]