# Add URL configuration in urls.py
from django.urls import path
from django.conf.urls.static import static

from django.conf import settings
from . import views
#
urlpatterns = [
   
   path('registermember/', views.registermember, name='member_registration'),
   path('customers/import/', views.excel_import, name='excel_import'),
   path('customers/template/download/', views.download_template, name='download_template'),
 
   #path('memberSum/', views.memberSum, name='memberSum'),
   path('customer/edit/<str:cus_id>/', views.edit_customer, name='edit_customer'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)