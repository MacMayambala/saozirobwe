from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib import messages
from .models import Delegate, Target, Transaction, TargetType
from Customer.models import Customer
from .forms import DelegateRegistrationForm, TargetCreationForm, TargetTypeCreationForm, TargetForm, TransactionForm

def delegate_list(request):
    query = request.GET.get('q', '')
    date_range = request.GET.get('date_range', '')
    
    delegates = Delegate.objects.all()
    if query:
        delegates = delegates.filter(
            Q(customer__first_name__icontains=query) |
            Q(customer__surname__icontains=query) |
            Q(customer__cus_id__icontains=query)
        )
    
    if date_range:
        try:
            start_date, end_date = date_range.split(' to ')
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            delegates = delegates.filter(assigned_date__range=[start_date, end_date])
        except (ValueError, AttributeError):
            pass
    
    paginator = Paginator(delegates, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'delegates/delegate_list.html', {
        'page_obj': page_obj,
        'query': query,
        'date_range': date_range
    })

def delegate_detail(request, delegate_id):
    delegate = get_object_or_404(Delegate, id=delegate_id)
    targets = delegate.targets.all()
    transactions = delegate.transactions.all()

    transaction_date_range = request.GET.get('transaction_date_range', '')
    if transaction_date_range:
        try:
            start_date, end_date = transaction_date_range.split(' to ')
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            transactions = transactions.filter(transaction_date__range=[start_date, end_date])
        except (ValueError, AttributeError):
            pass

    target_performance = []
    for target in targets:
        total_actual = sum(tx.actual_value for tx in target.transactions.all())
        percentage = (total_actual / target.target_value * 100) if target.target_value > 0 else 0
        target_performance.append({
            'target': target,
            'total_actual': total_actual,
            'percentage': percentage,
            'unit': target.target_type.name,
        })

    target_form = TargetForm(request.POST if 'add_target' in request.POST else None)
    transaction_form = TransactionForm(request.POST if 'add_transaction' in request.POST else None)

    if request.method == 'POST':
        if 'add_target' in request.POST and target_form.is_valid():
            new_target = target_form.save(commit=False)
            new_target.delegate = delegate
            new_target.save()
            messages.success(request, "Target added successfully.")
            return redirect('delegate_detail', delegate_id=delegate.id)
        elif 'add_transaction' in request.POST and transaction_form.is_valid():
            new_tx = transaction_form.save(commit=False)
            new_tx.delegate = delegate
            new_tx.target = transaction_form.cleaned_data.get('target')
            new_tx.save()
            messages.success(request, "Transaction recorded successfully.")
            return redirect('delegate_detail', delegate_id=delegate.id)
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'delegates/delegate_detail.html', {
        'delegate': delegate,
        'target_performance': target_performance,
        'transactions': transactions,
        'target_form': target_form,
        'transaction_form': transaction_form,
        'transaction_date_range': transaction_date_range
    })

def register_delegate(request):
    # Handle customer search
    search_query = request.GET.get('search_query', '')
    search_results = None
    if search_query:
        search_results = Customer.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(surname__icontains=search_query) |
            Q(cus_id__icontains=search_query)
        )
        # Add is_delegate, delegate_is_active, and delegate attributes to each customer
        for customer in search_results:
            delegate = Delegate.objects.filter(customer=customer).first()
            customer.is_delegate = delegate is not None
            customer.delegate_is_active = delegate.is_active if delegate else False
            customer.delegate = delegate  # Attach the delegate object for accessing expiry_date
            print(f"Customer {customer.cus_id}: is_delegate={customer.is_delegate}, delegate_is_active={customer.delegate_is_active}, expiry_date={delegate.expiry_date if delegate else 'N/A'}")  # Debug log

    # Handle delegate registration or renewal
    if request.method == 'POST':
        print("Received POST request:", request.POST)  # Debug log
        form = DelegateRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.cleaned_data['customer']
            action = request.POST.get('action', 'register')
            delegate = Delegate.objects.filter(customer=customer).first()

            if action == 'register':
                if delegate:
                    messages.error(request, "This customer is already registered as a delegate.")
                else:
                    new_delegate = form.save(commit=False)
                    new_delegate.assigned_date = datetime.now().date()
                    new_delegate.expiry_date = new_delegate.assigned_date + timedelta(days=365)
                    new_delegate.is_active = True
                    new_delegate.save()
                    messages.success(request, "Delegate registered successfully.")
                    return redirect('delegate_list')
            elif action == 'renew':
                if delegate:
                    delegate.is_active = True
                    delegate.assigned_date = datetime.now().date()
                    delegate.expiry_date = delegate.assigned_date + timedelta(days=365)
                    delegate.save()
                    messages.success(request, "Delegate status renewed successfully.")
                    return redirect('delegate_list')
                else:
                    messages.error(request, "Customer is not a delegate. Please register first.")
        else:
            print("Form errors:", form.errors)  # Debug log
            messages.error(request, "Please correct the errors below.")
            # Re-run the search to display results again
            if search_query:
                search_results = Customer.objects.filter(
                    Q(first_name__icontains=search_query) |
                    Q(surname__icontains=search_query) |
                    Q(cus_id__icontains=search_query)
                )
                for customer in search_results:
                    delegate = Delegate.objects.filter(customer=customer).first()
                    customer.is_delegate = delegate is not None
                    customer.delegate_is_active = delegate.is_active if delegate else False
                    customer.delegate = delegate
                    print(f"Customer {customer.cus_id}: is_delegate={customer.is_delegate}, delegate_is_active={customer.delegate_is_active}, expiry_date={delegate.expiry_date if delegate else 'N/A'}")  # Debug log
    else:
        form = DelegateRegistrationForm()

    return render(request, 'delegates/register_delegate.html', {
        'form': form,
        'search_query': search_query,
        'search_results': search_results
    })

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Delegate, Target
from .forms import TargetCreationForm

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Delegate, Target
from .forms import TargetCreationForm

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .forms import TargetCreationForm
from .models import Delegate, Target

def register_target(request):
    search_query = request.GET.get('search_query', '')
    search_results = None
    form_errors = None

    # Handle delegate search (GET request)
    if search_query:
        search_results = Delegate.objects.filter(
            Q(customer__first_name__icontains=search_query) |
            Q(customer__surname__icontains=search_query) |
            Q(customer__cus_id__icontains=search_query)
            # Optional: Filter for active delegates only
            # Q(is_active=True)
        )
        for delegate in search_results:
            print(f"Delegate {delegate.customer.cus_id}: id={delegate.id}, is_active={delegate.is_active}, expiry_date={delegate.expiry_date}")

    # Handle target registration (POST request)
    if request.method == 'POST':
        print("Received POST request:", request.POST)
        form = TargetCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Target registered successfully.")
            return redirect('delegate_list')  # Ensure 'target_list' URL is defined
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Please correct the errors below.")
            form_errors = form.errors
            # Re-run search to preserve results on form error
            if search_query:
                search_results = Delegate.objects.filter(
                    Q(customer__first_name__icontains=search_query) |
                    Q(customer__surname__icontains=search_query) |
                    Q(customer__cus_id__icontains=search_query)
                    # Optional: Q(is_active=True)
                )
                for delegate in search_results:
                    print(f"Delegate {delegate.customer.cus_id}: id={delegate.id}, is_active={delegate.is_active}, expiry_date={delegate.expiry_date}")
    else:
        form = TargetCreationForm()

    return render(request, 'delegates/register_target.html', {
        'form': form,
        'search_query': search_query,
        'search_results': search_results,
        'form_errors': form_errors
    })


def add_target_type(request):
    if request.method == 'POST':
        form = TargetTypeCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Target type added successfully.")
            return redirect('delegate_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TargetTypeCreationForm()
    return render(request, 'delegates/add_target_type.html', {'form': form})

def expire_delegate(request, delegate_id):
    delegate = get_object_or_404(Delegate, id=delegate_id)
    delegate.is_active = False
    delegate.expiry_date = datetime.now().date()
    delegate.save()
    messages.success(request, "Delegate status expired successfully.")
    return redirect('delegate_list')

def renew_delegate(request, delegate_id):
    delegate = get_object_or_404(Delegate, id=delegate_id)
    delegate.is_active = True
    delegate.assigned_date = datetime.now().date()
    delegate.expiry_date = delegate.assigned_date + timedelta(days=365)
    delegate.save()
    messages.success(request, "Delegate status renewed successfully.")
    return redirect('delegate_list')



##################################################################################
# delegates/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Term_details
from .forms import TermDetailsForm

def add_term_details(request):
    if request.method == 'POST':
        form = TermDetailsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Term details added successfully.")
            return redirect('term_details_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TermDetailsForm()
    return render(request, 'delegates/add_term_details.html', {'form': form})

def term_details_list(request):
    terms = Term_details.objects.all().order_by('-created_at')
    return render(request, 'delegates/term_details_list.html', {'terms': terms})

def edit_term_details(request, term_id):
    term = get_object_or_404(Term_details, id=term_id)
    if request.method == 'POST':
        form = TermDetailsForm(request.POST, instance=term)
        if form.is_valid():
            form.save()
            messages.success(request, "Term details updated successfully.")
            return redirect('term_details_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TermDetailsForm(instance=term)
    return render(request, 'delegates/add_term_details.html', {'form': form, 'term': term})