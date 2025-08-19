from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Staff, StaffTargetType, Target, Department, Position, TargetTransaction
from django.contrib import messages


# staff_management/views.py
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Staff
@login_required
def staff_dashboard(request):
    # Get search query and page number from GET parameters
    query = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    items_per_page = 5  # Matches template's itemsPerPage

    # Filter staff based on search query
    staff_list = Staff.objects.all()
    if query:
        staff_list = staff_list.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    # Paginate results
    paginator = Paginator(staff_list, items_per_page)
    page_obj = paginator.get_page(page)

    context = {
        'staff_list': page_obj,  # Pass paginated staff list
        'page_obj': page_obj,    # For pagination in template
        'query': query           # Preserve search query in template
    }
    return render(request, 'staff_management/staff_dashboard.html', context)

# staff_management/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Branch, Department, Position, Staff
from .forms import StaffForm
import logging

logger = logging.getLogger(__name__)

# staff_management/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Staff, Branch, Position, Department
from .forms import StaffForm

def staff_dashboard(request):
    query = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    items_per_page = 5

    staff_list = Staff.objects.all()
    if query:
        staff_list = staff_list.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query)
        )

    paginator = Paginator(staff_list, items_per_page)
    page_obj = paginator.get_page(page)

    context = {
        'staff_list': page_obj,
        'page_obj': page_obj,
        'query': query
    }
    return render(request, 'staff_management/staff_dashboard.html', context)

def search_staff(request):
    query = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    items_per_page = 5

    staff_list = Staff.objects.all()
    if query:
        staff_list = staff_list.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query)
        )

    paginator = Paginator(staff_list, items_per_page)
    page_obj = paginator.get_page(page)

    staff_data = []
    for staff in page_obj:
        staff_data.append({
            'id': staff.id,
            'first_name': staff.first_name,
            'last_name': staff.last_name,
            'email': staff.email,
            'phone_number': staff.phone_number,
            'position': staff.position.name if staff.position else None,
            'department': staff.department.name if staff.department else None,
            'photo': staff.photo.url if staff.photo else None
        })

    data = {
        'staff': staff_data,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'total_items': paginator.count
    }

    return JsonResponse(data)
# staff_management/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Staff
from .forms import StaffForm

def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save()  # employee_id generated in save()
            messages.success(request, f"Staff {staff.full_name} created successfully with Employee ID {staff.employee_id}!")
            return redirect('staff_management:staff_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StaffForm()
    return render(request, 'staff_management/add_staff.html', {'form': form})

def update_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            staff = form.save()  # employee_id unchanged
            messages.success(request, f"Staff {staff.full_name} updated successfully!")
            return redirect('staff_management:staff_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StaffForm(instance=staff)
    return render(request, 'staff_management/add_staff.html', {'form': form, 'staff': staff})


# staff_management/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from .models import Staff, Target, TargetTransaction, StaffTargetType

# staff_management/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from .models import Staff, Target, TargetTransaction, StaffTargetType

def add_target(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    target_types = StaffTargetType.objects.all()
    period_choices = Target.PERIOD_CHOICES  # Get period choices for template

    if request.method == 'POST':
        try:
            target_type_id = request.POST['target_type']
            goal_value = Decimal(request.POST['goal_value'])
            current_value = Decimal(request.POST.get('current_value', '0.00'))
            start_date = request.POST['start_date']
            end_date = request.POST['end_date']
            period = request.POST['period']  # New period field

            # Validate inputs
            if goal_value <= 0:
                messages.error(request, "Goal value must be greater than 0.")
                return redirect('staff_management:view_performance', staff_id=staff.id)
            if current_value < 0:
                messages.error(request, "Current value cannot be negative.")
                return redirect('staff_management:view_performance', staff_id=staff.id)
            if start_date > end_date:
                messages.error(request, "Start date must be before end date.")
                return redirect('staff_management:view_performance', staff_id=staff.id)
            if period not in [choice[0] for choice in Target.PERIOD_CHOICES]:
                messages.error(request, "Invalid period selected.")
                return redirect('staff_management:view_performance', staff_id=staff.id)

            # Get the selected target type
            target_type = get_object_or_404(StaffTargetType, id=target_type_id)

            # Check for active targets with the same StaffTargetType
            today = timezone.now().date()
            existing_target = Target.objects.filter(
                staff=staff,
                target_type=target_type,
                end_date__gte=today
            ).first()
            if existing_target:
                messages.error(
                    request,
                    f"An active target of type '{target_type.stname}' already exists for {staff.full_name} "
                    f"until {existing_target.end_date}. Wait until the end date is reached to assign this type again."
                )
                return redirect('staff_management:view_performance', staff_id=staff.id)

            # Create the Target instance
            target = Target(
                staff=staff,
                target_type=target_type,
                goal_value=goal_value,
                current_value=current_value,
                start_date=start_date,
                end_date=end_date,
                period=period  # Save period
            )
            target.save()

            # Create transaction if current_value > 0
            if current_value > 0:
                TargetTransaction.objects.create(
                    target=target,
                    shares_added=current_value
                )

            messages.success(request, f"Target '{target_type.stname}' added successfully for {staff.full_name}!")
            return redirect('staff_management:view_performance', staff_id=staff.id)

        except ValueError:
            messages.error(request, "Invalid input values. Please enter valid numbers for goal and current values.")
        except Exception as e:
            messages.error(request, f"Error adding target: {str(e)}")

    return render(request, 'staff_management/add_target.html', {
        'staff': staff,
        'target_types': target_types,
        'period_choices': period_choices  # Pass period choices to template
    })





from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import logging
from datetime import datetime
import pytz
from .models import Target, TargetTransaction

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def update_target(request, target_id):
    target = get_object_or_404(Target, id=target_id)
    # Debug: Log target attributes
    logger.debug(f"Target object: {target.__dict__}")
    
    if request.method == 'POST':
        try:
            actual_value = float(request.POST.get('actual_value'))
            transaction_type = request.POST.get('transaction_type')
            transaction_date = request.POST.get('transaction_date')
            transdescription = request.POST.get('transdescription')

            # Validate inputs
            if transaction_type not in ['Deposit', 'Withdrawal']:
                messages.error(request, "Invalid transaction type.")
                return redirect('staff_management:view_performance', staff_id=target.staff.id)
            if actual_value < 0:
                messages.error(request, "Transaction value cannot be negative.")
                return redirect('staff_management:view_performance', staff_id=target.staff.id)
            if not transaction_date:
                messages.error(request, "Transaction date is required.")
                return redirect('staff_management:view_performance', staff_id=target.staff.id)
            try:
                naive_date = datetime.strptime(transaction_date, '%Y-%m-%d %H:%M')
                parsed_date = timezone.make_aware(naive_date, timezone.get_default_timezone())
                if parsed_date > timezone.now():
                    messages.error(request, "Transaction date cannot be in the future.")
                    return redirect('staff_management:view_performance', staff_id=target.staff.id)
            except ValueError:
                messages.error(request, "Invalid transaction date format. Use YYYY-MM-DD HH:MM.")
                return redirect('staff_management:view_performance', staff_id=target.staff.id)
            if not transdescription or len(transdescription) > 25:
                messages.error(request, "Trans description is required and must be 25 characters or less.")
                return redirect('staff_management:view_performance', staff_id=target.staff.id)

            # Calculate new current_value
            new_current_value = float(target.current_value)
            if transaction_type == 'Deposit':
                new_current_value += actual_value
            elif transaction_type == 'Withdrawal':
                new_current_value -= actual_value
            
            if new_current_value < 0:
                messages.error(request, "Withdrawal would result in a negative current value.")
                return redirect('staff_management:view_performance', staff_id=target.staff.id)
            if new_current_value > target.goal_value:
                messages.error(request, f"Transaction would exceed the goal value of {target.goal_value}.")
                return redirect('staff_management:view_performance', staff_id=target.staff.id)
            
            # Create a transaction
            TargetTransaction.objects.create(
                target=target,
                transaction_type=transaction_type,
                actual_value=actual_value,
                transaction_date=parsed_date,
                transdescription=transdescription
            )
            
            # Update target's current_value
            target.current_value = new_current_value
            target.save()
            
            # Use target_type.stname for success message
            messages.success(request, f"{transaction_type} of {actual_value} for '{target.target_type.stname}' recorded successfully!")
        except ValueError:
            messages.error(request, "Invalid transaction value. Please enter a valid number.")
            logger.error(f"ValueError recording transaction for target {target_id} for staff {target.staff.id}: Invalid input")
        except Exception as e:
            messages.error(request, f"Error recording transaction: {str(e)}")
            logger.error(f"Unexpected error recording transaction for target {target_id} for staff {target.staff.id}: {str(e)}")
        return redirect('staff_management:view_performance', staff_id=target.staff.id)
    return redirect('staff_management:view_performance', staff_id=target.staff.id)


#########################BranchView4
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms
from .models import Branch

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['code', 'name', 'description', 'location']
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'e.g., BR001'}),
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Main Branch'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter branch description (optional)'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., Kampala, Uganda (optional)'}),
        }

    def clean_code(self):
        code = self.cleaned_data['code'].strip()
        if not code:
            raise forms.ValidationError("Branch code cannot be empty.")
        return code

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if not name:
            raise forms.ValidationError("Branch name cannot be empty.")
        return name

@login_required
def add_branch(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Branch '{form.cleaned_data['name']}' added successfully!")
            return redirect('staff_management:staff_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BranchForm()
    return render(request, 'staff_management/add_branch.html', {'form': form})


@login_required
def delete_target(request, target_id):
    target = get_object_or_404(Target, id=target_id)
    staff_id = target.staff.id
    if request.method == 'POST':
        target.delete()
        messages.success(request, f"Target {target.target_type} deleted successfully!")
        return redirect('staff_management:view_performance', staff_id=staff_id)
    messages.error(request, "Invalid request method.")
    return redirect('staff_management:view_performance', staff_id=staff_id)


# staff_management/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Staff, Target, StaffTargetType
from .forms import TargetForm


from django.contrib.auth.decorators import login_required
from .models import Staff, Target, StaffTargetType
from .forms import TargetForm

@login_required
def view_performance(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    # Order targets by end_date (ascending)
    targets = Target.objects.filter(staff=staff).order_by('-end_date')
    target_types = StaffTargetType.objects.all()
    form = TargetForm(initial={'staff': staff})
    
    # Check for approved leaves
    has_approved_leave = staff.leaves.filter(status='Approved').exists()
    latest_approved_leave = staff.leaves.filter(status='Approved').order_by('-created_at').first() if has_approved_leave else None

    return render(request, 'staff_management/view_performance.html', {
        'staff': staff,
        'targets': targets,
        'target_types': target_types,
        'form': form,
        'has_approved_leave': has_approved_leave,
        'latest_approved_leave': latest_approved_leave,
    })

@login_required
def add_position(request):
    if request.method == 'POST':
        try:
            name = request.POST['name']
            
            position = Position(name=name)
            position.save()
            messages.success(request, f"Position '{name}' added successfully!")
            return redirect('staff_management:staff_dashboard')
        except Exception as e:
            messages.error(request, f"Error adding position: {str(e)}")
    return render(request, 'staff_management/add_position.html')

@login_required
def add_department(request):
    if request.method == 'POST':
        try:
            name = request.POST['name']
            description = request.POST.get('description', '')
            department = Department(name=name, description=description)
            department.save()
            messages.success(request, f"Department '{name}' added successfully!")
            return redirect('staff_management:staff_dashboard')
        except Exception as e:
            messages.error(request, f"Error adding department: {str(e)}")
    return render(request, 'staff_management/add_department.html')

#########New Staff Target###################################################################################
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import StaffTargetType
from .forms import StaffTargetTypeForm

@login_required
def staff_target_type_list(request):
    """View to list all staff target types"""
    target_types = StaffTargetType.objects.all().order_by('stname')
    context = {
        'target_types': target_types,
        'title': 'Target Types'
    }
    return render(request, 'staff_management/staff_target_type_list.html', context)

@login_required
def staff_target_type_create(request):
    """View to create a new staff target type"""
    if request.method == 'POST':
        form = StaffTargetTypeForm(request.POST)
        if form.is_valid():
            target_type = form.save()
            messages.success(request, f'Target Type "{target_type.stname}" has been created successfully')
            return redirect('staff_management:staff_target_type_list')
    else:
        form = StaffTargetTypeForm()
    
    context = {
        'form': form,
        'title': 'Create Target Type',
        'is_create': True
    }
    return render(request, 'staff_management/staff_target_type_form.html', context)

@login_required
def staff_target_type_update(request, pk):
    """View to update an existing staff target type"""
    target_type = get_object_or_404(StaffTargetType, pk=pk)
    
    if request.method == 'POST':
        form = StaffTargetTypeForm(request.POST, instance=target_type)
        if form.is_valid():
            updated_target_type = form.save()
            messages.success(request, f'Target Type "{updated_target_type.stname}" has been updated successfully')
            return redirect('staff_target_type_list')
    else:
        form = StaffTargetTypeForm(instance=target_type)
    
    context = {
        'form': form,
        'target_type': target_type,
        'title': 'Update Target Type',
        'is_update': True
    }
    return render(request, 'staff_management/staff_target_type_form.html', context)

@login_required
def staff_target_type_detail(request, pk):
    """View to display details of a staff target type"""
    target_type = get_object_or_404(StaffTargetType, pk=pk)
    
    context = {
        'target_type': target_type,
        'title': f'Target Type: {target_type.stname}',
    }
    return render(request, 'staff_management/staff_target_type_detail.html', context)

@login_required
def staff_target_type_delete(request, pk):
    """View to delete a staff target type"""
    target_type = get_object_or_404(StaffTargetType, pk=pk)
    
    if request.method == 'POST':
        target_name = target_type.stname
        target_type.delete()
        messages.success(request, f'Target Type "{target_name}" has been deleted successfully')
        return redirect('staff_target_type_list')
    
    context = {
        'target_type': target_type,
        'title': 'Delete Target Type',
        'is_delete': True
    }
    return render(request, 'staff_management/staff_target_type_confirm_delete.html', context)

def test_view(request):
    """A simple test view to verify routing is working"""
    return HttpResponse("<h1>Test View is Working!</h1><p>If you can see this, your URL routing is functioning.</p>")




#################################################################
# staff_management/views.py
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Staff

def search_staff(request):
    query = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    items_per_page = 5

    # Filter staff based on search query
    staff_list = Staff.objects.all()
    if query:
        staff_list = staff_list.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    # Paginate results
    paginator = Paginator(staff_list, items_per_page)
    page_obj = paginator.get_page(page)

    # Prepare data for JSON response
    staff_data = []
    for staff in page_obj:
        staff_data.append({
            'id': staff.id,
            'first_name': staff.first_name,
            'last_name': staff.last_name,
            'email': staff.email,
            'phone': staff.phone,
            'position': staff.position.name if staff.position else None,
            'department': staff.department.name if staff.department else None,
            'profile_photo': staff.profile_photo.url if staff.profile_photo else None
        })

    data = {
        'staff': staff_data,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'total_items': paginator.count
    }

    return JsonResponse(data)



from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Target
from django.core.exceptions import ValidationError
from datetime import datetime

@login_required
def edit_target_goal(request, target_id):
    target = get_object_or_404(Target, id=target_id)
    
    if request.method == 'POST':
        try:
            # Retrieve form data
            period = request.POST.get('period')
            goal_value = request.POST.get('goal_value')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # Validate period
            if period not in dict(Target.PERIOD_CHOICES).keys():
                messages.error(request, "Invalid period selected.")
                return redirect('staff_management:view_performance', staff_id=target.staff.id)

            # Validate goal value
            try:
                goal_value = float(goal_value)
                if goal_value <= 0:
                    messages.error(request, "Goal value must be positive.")
                    return redirect('staff_management:view_performance', staff_id=target.staff.id)
                if goal_value < float(target.current_value):
                    messages.error(request, "Goal value cannot be less than current value.")
                    return redirect('staff_management:view_performance', staff_id=target.staff.id)
            except (ValueError, TypeError):
                messages.error(request, "Invalid goal value. Please enter a valid number.")
                return redirect('staff_management:view_performance', staff_id=target.staff.id)

            # Validate dates
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                if end_date <= start_date:
                    messages.error(request, "End date must be after start date.")
                    return redirect('staff_management:view_performance', staff_id=target.staff.id)
            except (ValueError, TypeError):
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect('staff_management:view_performance', staff_id=target.staff.id)

            # Update target (target_type remains unchanged)
            target.period = period
            target.goal_value = goal_value
            target.start_date = start_date
            target.end_date = end_date

            # Save with validation
            target.full_clean()  # Run model validation
            target.save()
            messages.success(request, f"Target '{target.target_type.stname}' updated successfully.")
        except ValidationError as e:
            messages.error(request, f"Validation error: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error updating target: {str(e)}")
        return redirect('staff_management:view_performance', staff_id=target.staff.id)
    
    return redirect('staff_management:view_performance', staff_id=target.staff.id)


################################################################################################

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User, Group
from .models import Staff, Leave
from datetime import datetime

@login_required
def leave_management(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    leaves = staff.leaves.all().order_by('-created_at')
    user = request.user

    # Check for approved leaves
    has_approved_leave = staff.leaves.filter(status='Approved').exists()
    latest_approved_leave = staff.leaves.filter(status='Approved').order_by('-created_at').first() if has_approved_leave else None

    # Define authorized groups and statuses
    authorized_groups = ['Manager', 'HR Manager', 'General Manager']
    can_reject_statuses = ['Pending', 'Reviewed', 'HR_Reviewed']

    # Check if the user is in an authorized group
    is_authorized = user.groups.filter(name__in=authorized_groups).exists()
    is_manager = user.groups.filter(name='Manager').exists()
    is_hr_manager = user.groups.filter(name='HR Manager').exists()
    is_general_manager = user.groups.filter(name='General Manager').exists()

    # Get the Staff record for the logged-in user
    reviewing_staff = Staff.objects.filter(user=user).first()

    print(f"User: {user.username}, Groups: {[g.name for g in user.groups.all()]}, Is Authorized: {is_authorized}")
    for leave in leaves:
        print(f"Leave ID: {leave.id}, Status: {leave.status}")

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')
        leave = get_object_or_404(Leave, id=leave_id) if leave_id else None

        if action == 'request' and not leave_id:
            leave_type = request.POST.get('leave_type')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            reason = request.POST.get('reason')

            try:
                if not start_date or not end_date:
                    raise ValueError("Start date and end date are required.")
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                if end_date < start_date:
                    raise ValueError("End date must be after start date.")

                Leave.objects.create(
                    staff=staff,
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date,
                    reason=reason
                )
                messages.success(request, f"Leave request for {staff.full_name} submitted successfully.")
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Error submitting leave request: {str(e)}")
            return redirect('staff_management:leave_management', staff_id=staff_id)

        elif action in ['review', 'hr_review', 'approve', 'reject'] and leave:
            if action == 'review' and is_manager and leave.status == 'Pending':
                leave.status = 'Reviewed'
                leave.manager_reviewed_by = reviewing_staff
                leave.save()
                messages.success(request, f"Leave request for {staff.full_name} reviewed by manager.")
            elif action == 'hr_review' and is_hr_manager and leave.status == 'Reviewed':
                leave.status = 'HR_Reviewed'
                leave.hr_reviewed_by = reviewing_staff
                leave.save()
                messages.success(request, f"Leave request for {staff.full_name} reviewed by HR manager.")
            elif action == 'approve' and is_general_manager and leave.status == 'HR_Reviewed':
                leave.status = 'Approved'
                leave.gm_approved_by = reviewing_staff
                leave.save()
                messages.success(request, f"Leave request for {staff.full_name} approved.")
            elif action == 'reject' and is_authorized and leave.status in can_reject_statuses:
                leave.status = 'Rejected'
                leave.save()
                messages.success(request, f"Leave request for {staff.full_name} rejected.")
            else:
                messages.error(request, "Invalid action or insufficient permissions.")
            return redirect('staff_management:leave_management', staff_id=staff_id)

    context = {
        'staff': staff,
        'leaves': leaves,
        'has_approved_leave': has_approved_leave,
        'latest_approved_leave': latest_approved_leave,
        'can_reject_statuses': can_reject_statuses,
        'is_authorized': is_authorized,
        'is_manager': is_manager,
        'is_hr_manager': is_hr_manager,
        'is_general_manager': is_general_manager,
    }
    return render(request, 'staff_management/leave_management.html', context)
