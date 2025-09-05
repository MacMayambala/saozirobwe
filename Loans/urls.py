# loans/urls.py
from django.urls import path
from . import views

urlpatterns = [
   # path('create/', views.create_loan, name='create_loan'),
   # path('repay/', views.add_repayment, name='add_repayment'),
    path('portfolio/', views.loan_portfolio, name='loan_portfolio'),
]

