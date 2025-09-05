# Groups/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoanGroupForm, GroupLoanForm, GroupSavingsForm, RepaymentForm
from .models import LoanGroup, GroupLoan, MemberLoanAllocation
from Loans.models import Repayment

# Groups/views.py
from django.shortcuts import render, redirect
from .forms import LoanGroupForm
from .models import LoanGroup, GroupMember
from django.contrib import messages

def create_group(request):
    if request.method == 'POST':
        form = LoanGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            # Add members to the group
            members = form.cleaned_data['members']
            for member in members:
                GroupMember.objects.create(group=group, customer=member, role='member')
            messages.success(request, f"Group {group.name} created successfully!")
            return redirect('group_list')
    else:
        form = LoanGroupForm()
    return render(request, 'Groups/create_group.html', {'form': form})



def group_list(request):
    groups = LoanGroup.objects.all()
    return render(request, 'Groups/list.html', {'groups': groups})

def group_detail(request, group_id):
    group = get_object_or_404(LoanGroup, id=group_id)
    active_loan = group.active_loan()
    repayments = Repayment.objects.filter(loan=active_loan.loan) if active_loan else []
    members = group.members.all()
    allocations = MemberLoanAllocation.objects.filter(group_loan=active_loan) if active_loan else []

    loan_form = GroupLoanForm(request.POST or None)
    repayment_form = RepaymentForm(request.POST or None, initial={'loan': active_loan.loan if active_loan else None})

    if request.method == 'POST':
        if 'create_loan' in request.POST and loan_form.is_valid():
            loan_form.save(group=group)
            return redirect('group_detail', group_id=group.id)
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
            return redirect('group_detail', group_id=group.id)

    return render(request, 'Groups/group_detail.html', {
        'group': group,
        'active_loan': active_loan.loan if active_loan else None,
        'repayments': repayments,
        'members': members,
        'allocations': allocations,
        'loan_form': loan_form,
        'repayment_form': repayment_form,
    })

# customer/views.py
from django.http import JsonResponse
from django.db.models import Q
from Customer.models import Customer

# Groups/views.py
from django.http import JsonResponse
from django.db.models import Q
from Customer.models import Customer  # Import from customer app

# Groups/views.py
from django.http import JsonResponse
from django.db.models import Q
from Customer.models import Customer

def customer_search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)
    
    customers = Customer.objects.filter(
        Q(first_name__icontains=query) |
        Q(surname__icontains=query) |
        Q(member_number__icontains=query)
    )[:10]
    
    results = [
        {
            'id': customer.cus_id,
            'full_name': f"{customer.first_name} {customer.surname}".strip(),
            'member_number': customer.member_number
        }
        for customer in customers
    ]
    
    return JsonResponse(results, safe=False)



# Groups/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import  AddGroupMembersForm
from .models import Group
from Customer.models import Customer
from django.http import JsonResponse
from django.db.models import Q

def add_group_members(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        form = AddGroupMembersForm(request.POST)
        if form.is_valid():
            form.save(group)
            messages.success(request, f'Members added to "{group.name}" successfully.')
            return redirect('group_detail', group_id=group.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddGroupMembersForm()
    
    return render(request, 'Groups/group_detail.html', {
        'group': group,
        'form': form,
        'members': group.members.all(),
        # Add other context variables (e.g., active_loan, allocations, repayments, loan_form, repayment_form)
    })

# Groups/views.py
from django.http import JsonResponse
from django.db.models import Q
from Customer.models import Customer

def customer_search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)
    
    customers = Customer.objects.filter(
        Q(first_name__icontains=query) |
        Q(surname__icontains=query) |
        Q(member_number__icontains=query)
    )[:10]
    
    results = [
        {
            'id': customer.cus_id,
            'text': f"{customer.first_name} {customer.surname} ({customer.member_number})"
        }
        for customer in customers
    ]
    
    return JsonResponse(results, safe=False)