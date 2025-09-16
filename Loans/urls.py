from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('portfolio/', views.loan_portfolio, name='loan_portfolio'),
    path('export-par/', views.export_par, name='export_par'),
]