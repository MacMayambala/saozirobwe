from django.urls import path
from . import views

urlpatterns = [
    path("documents/", views.document_list, name="document_list"),
    path("admins/documents/", views.admin_document_list, name="admin_document_list"),
   # path("user/documents/", views.admin_document_list, name="document_list"),
    path("active/", views.active_list, name="active_list"),
    path("active/<int:pk>/", views.document_detail, name="document_detail"),
 
    path("active/<int:pk>/request/", views.request_document, name="request_document"),
    path("active/<int:pk>/acknowledge/", views.acknowledge_document, name="acknowledge_document"),
    path("document/<int:pk>/approve/", views.approve_document, name="approve_document"),
    path("document/<int:pk>/authorise/", views.authorise_document, name="authorise_document"),
    path("document/<int:pk>/release/", views.release_document, name="release_document"),
    path("active/<int:pk>/deliver/", views.deliver_document, name="deliver_document"),
    path("active/<int:pk>/return/", views.return_document, name="return_document"),
    path("document/<int:pk>/reverse/", views.reverse_action, name="reverse_action"),
    path("register/<int:cus_id>/", views.register_document, name="register_document"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("muno/", views.muno, name="muno"),
]