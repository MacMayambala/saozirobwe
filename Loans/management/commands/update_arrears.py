# loans/management/commands/update_arrears.py
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from Loans.models import Loan
from Groups.models import MemberLoanAllocation

class Command(BaseCommand):
    def handle(self, *args, **options):
        today = now().date()
        for loan in Loan.objects.filter(status__in=['active', 'arrears']):
            if loan.outstanding_balance() > 0 and loan.maturity_date < today:
                loan.status = 'arrears'
                loan.save()
                # Update member allocations
                for allocation in MemberLoanAllocation.objects.filter(group_loan__loan=loan):
                    if allocation.outstanding_balance() > 0:
                        allocation.status = 'arrears'
                        allocation.save()