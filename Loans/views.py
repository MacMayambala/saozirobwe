from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils.timezone import now
from datetime import timedelta
from .models import Loan
from Groups.models import LoanGroup
import csv
from django.http import HttpResponse

def loan_portfolio(request):
    summary = Loan.objects.aggregate(
        total_loans=Count('id'),
        total_amount=Sum('amount'),
        total_outstanding=Sum('amount') - Sum('repayments__amount')
    )

    today = now().date()
    par_0 = Loan.objects.filter(status='arrears').aggregate(
        total=Sum('amount') - Sum('repayments__amount')
    )['total'] or 0
    par_30 = Loan.objects.filter(
        status='arrears',
        maturity_date__lte=today - timedelta(days=30)
    ).aggregate(total=Sum('amount') - Sum('repayments__amount'))['total'] or 0
    par_90 = Loan.objects.filter(
        status='arrears',
        maturity_date__lte=today - timedelta(days=90)
    ).aggregate(total=Sum('amount') - Sum('repayments__amount'))['total'] or 0

    total_outstanding = summary['total_outstanding'] or 0
    par_0_pct = (par_0 / total_outstanding * 100) if total_outstanding > 0 else 0
    par_30_pct = (par_30 / total_outstanding * 100) if total_outstanding > 0 else 0
    par_90_pct = (par_90 / total_outstanding * 100) if total_outstanding > 0 else 0

    status_counts = Loan.objects.values('status').annotate(count=Count('id'))

    return render(request, 'loans/portfolio.html', {
        'summary': summary,
        'par_0': par_0,
        'par_30': par_30,
        'par_90': par_90,
        'par_0_pct': par_0_pct,
        'par_30_pct': par_30_pct,
        'par_90_pct': par_90_pct,
        'status_counts': status_counts,
    })

def export_par(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="par_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Group', 'Loan ID', 'Outstanding', 'Days in Arrears'])
    for group in LoanGroup.objects.all():
        loan = group.active_loan()
        if loan and loan.loan.status == 'arrears':
            writer.writerow([group.name, loan.loan.id, loan.loan.outstanding_balance(), loan.loan.days_in_arrears()])
    return response