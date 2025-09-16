from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .forms import LoanGroupForm, GroupLoanForm, GroupSavingsForm, RepaymentForm, AddGroupMembersForm
from .models import AuditLog, LoanGroup, GroupLoan, MemberLoanAllocation
from Customer.models import Customer
from Loans.models import Repayment

def create_group(request):
    if request.method == 'POST':
        form = LoanGroupForm(request.POST, request=request)
        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} created successfully!")
            return redirect('group_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoanGroupForm()
    return render(request, 'group_lending/create_group.html', {'form': form})

def group_list(request):
    groups = LoanGroup.objects.all()
    return render(request, 'group_lending/list.html', {'groups': groups})

def group_detail(request, group_id):
    group = get_object_or_404(LoanGroup, id=group_id)
    active_loan = group.active_loan()
    repayments = Repayment.objects.filter(loan=active_loan.loan) if active_loan else []
    members = group.members.all()
    allocations = MemberLoanAllocation.objects.filter(group_loan=active_loan) if active_loan else []

    loan_form = GroupLoanForm(request.POST or None, group=group, request=request)
    repayment_form = RepaymentForm(request.POST or None, initial={'loan': active_loan.loan if active_loan else None})
    add_members_form = AddGroupMembersForm(request.POST or None, group=group, request=request)

    if request.method == 'POST':
        if 'create_loan' in request.POST and loan_form.is_valid():
            loan_form.save()
            messages.success(request, "Loan created successfully!")
            return redirect('group_lending:group_detail', group_id=group.id)
        elif 'add_repayment' in request.POST and repayment_form.is_valid():
            repayment = repayment_form.save()
            if repayment.member:
                allocation = MemberLoanAllocation.objects.filter(
                    group_loan=active_loan, member=repayment.member
                ).first()
                if allocation:
                    allocation.repaid_amount += repayment.amount
                    allocation.status = 'performing' if allocation.outstanding_balance() == 0 else 'arrears'
                    allocation.save()
                    AuditLog.objects.create(
                        action=f'Repayment of {repayment.amount} recorded for {repayment.member.first_name} {repayment.member.surname}',
                        user=request.user,
                        group=group,
                        loan=active_loan.loan
                    )
            messages.success(request, "Repayment recorded successfully!")
            return redirect('group_detail', group_id=group.id)
        elif 'add_members' in request.POST and add_members_form.is_valid():
            add_members_form.save()
            messages.success(request, "Members added successfully!")
            return redirect('group_detail', group_id=group.id)
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'group_lending/group_detail.html', {
        'group': group,
        'active_loan': active_loan.loan if active_loan else None,
        'repayments': repayments,
        'members': members,
        'allocations': allocations,
        'loan_form': loan_form,
        'repayment_form': repayment_form,
        'add_members_form': add_members_form,
    })

from django.http import JsonResponse
from Customer.models import Customer
from django.db.models import Q

def customer_search(request):
    query = request.GET.get('q', '')
    group_id = request.GET.get('group_id')

    customers = Customer.objects.filter(
        Q(first_name__icontains=query) |
        Q(surname__icontains=query) |
        Q(member_number__icontains=query)
    )

    if group_id:
        customers = customers.exclude(groupmember__group__id=group_id)

    customers = customers[:10]
    
    results = [
        {
            'id': customer.cus_id,   # always use cus_id here
            'text': f'{customer.first_name} {customer.surname} ({customer.member_number})',
            'member_number': customer.member_number
        }
        for customer in customers
    ]
    return JsonResponse({'results': results})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import LoanGroup, GroupMember
from .forms import AddGroupMembersForm
from Customer.models import Customer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import LoanGroup, GroupMember
from Customer.models import Customer
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import LoanGroup, GroupMember

from django.contrib.auth.decorators import login_required

@login_required
def add_group_members(request, group_id):
    group = get_object_or_404(LoanGroup, id=group_id)
    
    if request.method == 'POST':
        member_ids = request.POST.get('members', '').split(',')
        member_ids = [id.strip() for id in member_ids if id.strip()]
        
        if not member_ids:
            messages.error(request, 'No members selected.')
            return render(request, 'group_lending/add_group_members.html', {
                'group': group,
            })
        
        # Compare with cus_id (to match search results)
        existing_members = GroupMember.objects.filter(group=group).values_list('customer__cus_id', flat=True)
        added = False

        for member_id in member_ids:
            try:
                customer = Customer.objects.get(cus_id=member_id)
                if customer.cus_id not in existing_members:
                    GroupMember.objects.get_or_create(group=group, customer=customer)
                    added = True
                else:
                    messages.warning(request, f'{customer.first_name} {customer.surname} is already a member.')
            except Customer.DoesNotExist:
                messages.error(request, f'Customer with ID {member_id} not found.')
        
        if added:
            messages.success(request, 'Members added successfully.')
        return redirect('group_lending:group_detail', group_id=group.id)
    
    return render(request, 'group_lending/add_group_members.html', {
        'group': group,
    })
