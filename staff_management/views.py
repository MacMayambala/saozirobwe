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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def test_view(request):
    """A simple test view to verify routing is working"""
    return HttpResponse("<h1>Test View is Working!</h1><p>If you can see this, your URL routing is functioning.</p>")




#################################################################
# staff_management/views.py
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Staff
@login_required
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

            # Update target
            target.period = period
            target.goal_value = goal_value
            target.start_date = start_date
            target.end_date = end_date

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
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import datetime
import logging
import requests
from .models import Staff, Leave

# Configure logging
logger = logging.getLogger(__name__)

# === SMS Function ===
def send_sms_speedamobile(phone_number, message_text):
    """
    Send an SMS using the SpeedaMobile API.
    
    Args:
        phone_number (str): Recipient's phone number.
        message_text (str): Message content (max 160 characters).
    
    Returns:
        dict: API response.
    """
    url = "http://apidocs.speedamobile.com/api/SendSMS"
    payload = {
        "api_id": "API67606975827",  # Replace with environment variable in production
        "api_password": "Admin@sao256",  # Replace with environment variable in production
        "sms_type": "P",
        "encoding": "T",
        "sender_id": "BULKSMS",
        "phonenumber": phone_number,
        "textmessage": message_text[:160],
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"SMS API error for {phone_number}: {str(e)}")
        return {"status": "F", "remarks": str(e)}

@login_required
def leave_management(request, staff_id):
    """
    Handle leave management for a specific staff member, including requesting, reviewing,
    approving, or rejecting leaves. Sends notifications for actions and enforces business rules.
    
    Args:
        request: HTTP request object.
        staff_id: ID of the staff member.
    
    Returns:
        Rendered template for GET requests or redirects/JSON responses for POST requests.
    """
    # Fetch staff and related data
    staff = get_object_or_404(Staff, id=staff_id)
    leaves = staff.leaves.all().order_by('-created_at')
    user = request.user

    # Check for approved leaves
    has_approved_leave = staff.leaves.filter(status='Approved').exists()
    latest_approved_leave = staff.leaves.filter(status='Approved').order_by('-created_at').first() if has_approved_leave else None

    # Group-based permissions
    authorized_groups = ['Manager', 'HR Manager', 'General Manager']
    can_reject_statuses = ['Pending', 'Reviewed', 'HR_Reviewed']
    is_authorized = user.groups.filter(name__in=authorized_groups).exists()
    is_manager = user.groups.filter(name='Manager').exists()
    is_hr_manager = user.groups.filter(name='HR Manager').exists()
    is_general_manager = user.groups.filter(name='General Manager').exists()
    reviewing_staff = Staff.objects.filter(user=user).first()

    if request.method == 'POST':
        action = request.POST.get('action')
        input_password = request.POST.get('password', '')

        # Password verification for sensitive actions
        if action in ['review', 'hr_review', 'approve', 'reject'] and not user.check_password(input_password):
            logger.warning(f"Invalid password attempt by user {user.username} for action {action}")
            messages.error(request, "Incorrect password.")
            return JsonResponse({'success': False, 'error': 'Incorrect password'}, status=401)

        leave_id = request.POST.get('leave_id')
        leave = get_object_or_404(Leave, id=leave_id) if leave_id else None
        comment = request.POST.get('comment', '').strip()[:500]  # Limit comment length

        # === Request New Leave ===
        if action == 'request' and not leave_id:
            try:
                leave_type = request.POST.get('leave_type')
                start_date_str = request.POST.get('start_date')
                end_date_str = request.POST.get('end_date')
                reason = request.POST.get('reason', '').strip()[:500]

                # Input validation
                if not all([leave_type, start_date_str, end_date_str]):
                    raise ValueError("Leave type, start date, and end date are required.")

                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError("Invalid date format. Use YYYY-MM-DD.")

                if end_date < start_date:
                    raise ValueError("End date must be after start date.")
                if start_date < timezone.now().date():
                    raise ValueError("Start date cannot be in the past.")

                # Business rules
                ongoing_same_leave = staff.leaves.filter(
                    leave_type=leave_type,
                    status='Approved',
                    end_date__gte=timezone.now().date()
                ).exists()
                past_two_leaves = staff.leaves.filter(
                    leave_type=leave_type,
                    start_date__year=timezone.now().year
                ).count()

                if ongoing_same_leave:
                    raise ValueError(f"You are already on {leave_type} leave.")
                if past_two_leaves >= 2:
                    raise ValueError(f"You cannot request {leave_type} leave more than twice this year.")

                # Create leave request
                leave = Leave.objects.create(
                    staff=staff,
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date,
                    reason=reason or None,
                    created_at=timezone.now()
                )
                logger.info(f"Leave request created for {staff.full_name}: {leave_type} from {start_date} to {end_date}")

                # Send confirmation notification
                subject = "Leave Request Submitted"
                message_text = f"Dear {staff.full_name},\n\nYour {leave_type} leave request from {start_date} to {end_date} has been submitted and is pending review."
                contact_info = f"Contact: {staff.phone}"
                if staff.next_of_kin_phone:
                    contact_info += f" | Emergency: {staff.next_of_kin_phone}"
                message_text += f"\n{contact_info}\nSAO ZIROBWE SACCO"

                # Email notification
                if staff.email:
                    try:
                        context = {
                            "first_name": staff.first_name,
                            "last_name": staff.last_name,
                            "leave_type": leave_type,
                            "start_date": start_date,
                            "end_date": end_date,
                            "status": "Pending",
                        }
                        html_content = render_to_string("email/leave_notification.html", context)
                        text_content = strip_tags(html_content)
                        email = EmailMultiAlternatives(
                            subject=subject,
                            body=text_content,
                            from_email="Sao Zirobwe Sacco <noreply@saozirobwe.co.ug>",
                            to=[staff.email],
                            headers={'Reply-To': 'info@saozirobwe.co.ug'}
                        )
                        email.attach_alternative(html_content, "text/html")
                        email.send(fail_silently=False)
                        logger.info(f"Confirmation email sent to {staff.email}")
                    except Exception as e:
                        logger.error(f"Failed to send confirmation email to {staff.email}: {str(e)}")

                # SMS notification
                if staff.phone:
                    sms_result = send_sms_speedamobile(staff.phone, message_text)
                    if sms_result.get("status") != "S":
                        logger.error(f"Failed to send SMS to {staff.phone}: {sms_result.get('remarks')}")

                messages.success(request, "Leave request submitted successfully.")
                return redirect('staff_management:leave_management', staff_id=staff.id)

            except ValueError as e:
                logger.error(f"Leave request error for {staff.full_name}: {str(e)}")
                messages.error(request, str(e))
                return redirect('staff_management:leave_management', staff_id=staff.id)
            except Exception as e:
                logger.error(f"Unexpected error in leave request for {staff.full_name}: {str(e)}")
                messages.error(request, "An unexpected error occurred.")
                return redirect('staff_management:leave_management', staff_id=staff.id)

        # === Review / Approve / Reject Leave ===
        elif action in ['review', 'hr_review', 'approve', 'reject'] and leave:
            try:
                action_success = False
                subject = None
                message_text = None

                if action == 'review' and is_manager and leave.status == 'Pending':
                    leave.status = 'Reviewed'
                    leave.manager_reviewed_by = reviewing_staff.user if reviewing_staff else None
                    leave.comment = comment or None
                    subject = "Leave Reviewed by Manager"
                    message_text = f"Dear {staff.full_name},\n\nYour {leave.leave_type} leave has been reviewed by a manager."
                    action_success = True

                elif action == 'hr_review' and is_hr_manager and leave.status == 'Reviewed':
                    leave.status = 'HR_Reviewed'
                    leave.hr_reviewed_by = reviewing_staff.user if reviewing_staff else None
                    leave.comment = comment or None
                    subject = "Leave Reviewed by HR"
                    message_text = f"Dear {staff.full_name},\n\nYour {leave.leave_type} leave has been reviewed by HR."
                    action_success = True

                elif action == 'approve' and is_general_manager and leave.status == 'HR_Reviewed':
                    leave.status = 'Approved'
                    leave.gm_approved_by = reviewing_staff.user if reviewing_staff else None
                    leave.comment = comment or None
                    subject = "Leave Approved"
                    message_text = f"Dear {staff.full_name},\n\nYour {leave.leave_type} leave from {leave.start_date} to {leave.end_date} has been approved."
                    action_success = True

                elif action == 'reject' and is_authorized and leave.status in can_reject_statuses:
                    leave.status = 'Rejected'
                    leave.comment = comment or None
                    subject = "Leave Rejected"
                    message_text = f"Dear {staff.full_name},\n\nYour {leave.leave_type} leave from {leave.start_date} to {leave.end_date} has been rejected. Comment: {comment or 'None'}"
                    action_success = True

                if action_success:
                    leave.updated_at = timezone.now()
                    leave.save()
                    logger.info(f"Leave {action} successful for {staff.full_name}: {leave.leave_type} (ID: {leave.id})")

                    # Add contact info to message
                    contact_info = f"Contact: {staff.phone}"
                    if staff.next_of_kin_phone:
                        contact_info += f" | Emergency: {staff.next_of_kin_phone}"
                    message_text += f"\n{contact_info}\nSAO ZIROBWE SACCO"

                    # Email notification
                    if staff.email:
                        try:
                            context = {
                                "first_name": staff.first_name,
                                "last_name": staff.last_name,
                                "leave_type": leave.leave_type,
                                "start_date": leave.start_date,
                                "end_date": leave.end_date,
                                "status": leave.status,
                                "comment": leave.comment,
                            }
                            html_content = render_to_string("email/leave_notification.html", context)
                            text_content = strip_tags(html_content)
                            email = EmailMultiAlternatives(
                                subject=subject,
                                body=text_content,
                                from_email="Sao Zirobwe Sacco <noreply@saozirobwe.co.ug>",
                                to=[staff.email],
                                headers={'Reply-To': 'info@saozirobwe.co.ug'}
                            )
                            email.attach_alternative(html_content, "text/html")
                            email.send(fail_silently=False)
                            logger.info(f"{action.capitalize()} email sent to {staff.email}")
                        except Exception as e:
                            logger.error(f"Failed to send {action} email to {staff.email}: {str(e)}")

                    # SMS notification
                    if staff.phone:
                        sms_result = send_sms_speedamobile(staff.phone, message_text)
                        if sms_result.get("status") != "S":
                            logger.error(f"Failed to send {action} SMS to {staff.phone}: {sms_result.get('remarks')}")

                    messages.success(request, f"Leave {action} successful.")
                    return JsonResponse({'success': True, 'message': f"Leave {action} successful."})

                else:
                    logger.warning(f"Invalid action or permissions for user {user.username}: {action} on leave {leave.id}")
                    messages.error(request, "Invalid action or insufficient permissions.")
                    return JsonResponse({'success': False, 'error': 'Invalid action or insufficient permissions.'}, status=403)

            except Exception as e:
                logger.error(f"Error processing {action} for leave {leave.id}: {str(e)}")
                messages.error(request, "An unexpected error occurred.")
                return JsonResponse({'success': False, 'error': 'An unexpected error occurred.'}, status=500)

        else:
            logger.warning(f"Invalid POST request by {user.username}: action={action}, leave_id={leave_id}")
            messages.error(request, "Invalid request.")
            return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

    # GET request - render page
    context = {
        'staff': staff,
        'leaves': leaves,
        'has_approved_leave': has_approved_leave,
        'latest_approved_leave': latest_approved_leave,
        'is_authorized': is_authorized,
        'is_manager': is_manager,
        'is_hr_manager': is_hr_manager,
        'is_general_manager': is_general_manager,
    }
    return render(request, 'staff_management/leave_management.html', context)