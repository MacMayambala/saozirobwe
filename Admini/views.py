from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from Reports.models import UserActivity 
from users.models import TwoFactorAuth

from functools import wraps

from django.contrib import messages
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect

def superuser_or_redirect(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "You do not have permission to access this page.")
            # Redirect to previous page if available, else fallback
            return redirect(request.META.get('HTTP_REFERER', 'staff_management:staff_dashboard'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view



def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name='Admin').exists():
                return redirect('dashboard')
            elif user.groups.filter(name='Teller').exists():
                return redirect('dashboard')
            elif user.groups.filter(name='Officer').exists():
                return redirect('dashboard')
            else:
                return redirect('dashboard')  # Default redirect if no role is assigned
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    UserActivity.objects.create(user=request.user, action="Logged Out")
    return redirect('login')

@login_required
def home(request):
    return render(request,"shared.html")


def dashboard(request):
    user_2fa = TwoFactorAuth.objects.filter(user=request.user).first()
    
    # Redirect to 2FA verification if not verified
    if not request.session.get("verified", False):
        return redirect("setup_2fa")  # Ensure 'verify_2fa' is the correct URL name

    return render(request, "dashboard.html")  # Your dashboard template

@login_required
def reports(request):
    return render(request, 'reports.html')

# @login_required
# def settings(request):
#     return render(request, 'settings.html')

@login_required
def home(request):
    return render(request, 'dashboard.html')  # Redirect home to dashboard

from django.contrib.auth import logout
from django.shortcuts import redirect
@login_required
def custom_logout(request):
    logout(request)
    response = redirect('/')  # Redirect to login page
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


from django.shortcuts import render

@login_required
def custom_404_view(request, exception):
    return render(request, "404.html", status=404)


#####################################################################################################################
# your_app_name/views.py
import logging
import json
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render

logger = logging.getLogger(__name__)

@require_GET
def audit_trails(request):
    search_query = request.GET.get('search', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    page = int(request.GET.get('page', 1))

    logs = LogEntry.objects.select_related('user', 'content_type').all().order_by('-action_time')
    logger.info(f"Total logs: {logs.count()}")

    if search_query:
        logs = logs.filter(
            Q(user__username__icontains=search_query) |
            Q(object_repr__icontains=search_query) |
            Q(change_message__icontains=search_query)
        )
        logger.info(f"After search filter ('{search_query}'): {logs.count()}")

    if start_date:
        try:
            start_date = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            logs = logs.filter(action_time__gte=start_date)
            logger.info(f"After start_date filter ({start_date}): {logs.count()}")
        except ValueError:
            logger.error(f"Invalid start_date: {start_date}")

    if end_date:
        try:
            end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            logs = logs.filter(action_time__lte=end_date)
            logger.info(f"After end_date filter ({end_date}): {logs.count()}")
        except ValueError:
            logger.error(f"Invalid end_date: {end_date}")

    paginator = Paginator(logs, 5)  # 2 items per page for testing
    page_obj = paginator.get_page(page)
    logger.info(f"Page {page}: {page_obj.object_list.count()} items")

    action_map = {
        ADDITION: 'added',
        CHANGE: 'changed',
        DELETION: 'deleted',
    }

    def format_change_message(log):
        action_verb = action_map.get(log.action_flag, 'performed')
        if log.action_flag == ADDITION:
            return f"{log.user.username} {action_verb} {log.object_repr} at {log.action_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        elif log.action_flag == DELETION:
            return f"{log.user.username} {action_verb} {log.object_repr} at {log.action_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        else:  # CHANGE
            try:
                changes = json.loads(log.change_message)
                if not changes or not isinstance(changes, list):
                    return f"{log.user.username} {action_verb} {log.object_repr} (no details) at {log.action_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
                fields_changed = []
                for change in changes:
                    if 'changed' in change and 'fields' in change['changed']:
                        fields_changed.extend(change['changed']['fields'])
                if fields_changed:
                    fields_str = ', '.join(fields_changed)
                    return f"{log.user.username} {action_verb} {fields_str} for {log.object_repr} at {log.action_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
                return f"{log.user.username} {action_verb} {log.object_repr} (no fields specified) at {log.action_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
            except json.JSONDecodeError:
                return f"{log.user.username} {action_verb} {log.object_repr} (invalid change data) at {log.action_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logs_list = [
            {
                'user': {'username': log.user.username},
                'action': log.get_action_flag_display(),
                'object_repr': log.object_repr,
                'change_message': format_change_message(log),
                'timestamp': log.action_time.isoformat(),
                'content_type': str(log.content_type) if log.content_type else 'Unknown',
            }
            for log in page_obj
        ]

        response_data = {
            'activities': logs_list,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        }

        return JsonResponse(response_data)
    else:
        activities = [
            {
                'user': {'username': log.user.username},
                'action': log.get_action_flag_display(),
                'object_repr': log.object_repr,
                'change_message': format_change_message(log),
                'timestamp': log.action_time.isoformat(),
                'content_type': str(log.content_type) if log.content_type else 'Unknown',
            }
            for log in page_obj
        ]

        context = {
            'activities': activities,
            'page_obj': page_obj,
        }
        return render(request, 'audits.html', context)
########################################################################################################################################
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.core.management import call_command, CommandError
from django.conf import settings
from django.http import HttpResponseForbidden
import logging

logger = logging.getLogger(__name__)

def superuser_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Permission denied.")
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    wrapper.__doc__ = view_func.__doc__
    return wrapper

@login_required
@superuser_required
def cron_management(request):
    """Manage and run cron jobs for leave reminders and membership expiry notifications."""
    cron_jobs = [
        {
            'name': 'Leave Reminder',
            'command': 'staff_management.management.commands.leave_reminder.Command',
            'id': 'leave_reminder',
            'schedule': '0 8 * * *',
            'time': '08:00',
        },
        {
            'name': 'Membership Expiry Notification',
            'command': 'Munomukabi.management.commands.expiry_notification.Command',
            'id': 'membership_expiry',
            'schedule': '0 9 * * *',
            'time': '09:00',
        },
    ]

    if request.method == "POST":
        action = request.POST.get("action")
        job_id = request.POST.get("job_id")
        password = request.POST.get("password")

        # Verify password
        if not password:
            messages.error(request, "Password is required to perform this action.")
            return redirect("cron_management")

        auth_user = authenticate(username=request.user.username, password=password)
        if not auth_user:
            messages.error(request, "Incorrect password.")
            return redirect("cron_management")

        # Run job immediately
        if action == "run":
            try:
                if job_id == "leave_reminder":
                    call_command("leave_reminder")
                    messages.success(request, "Leave reminder job executed successfully.")
                elif job_id == "membership_expiry":
                    call_command("expiry_notification")
                    messages.success(request, "Membership expiry job executed successfully.")
                else:
                    messages.error(request, "Invalid job ID.")
            except CommandError as e:
                logger.error(f"Failed to run command {job_id}: {str(e)}")
                messages.error(request, f"Failed to run job: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error running command {job_id}: {str(e)}")
                messages.error(request, f"Unexpected error: {str(e)}")

        # Update schedule
        elif action == "update":
            hour = request.POST.get("hour")
            minute = request.POST.get("minute")
            frequency = request.POST.get("frequency", "daily")  # new field: daily, weekly, monthly

            if not _is_valid_time(hour, minute):
                messages.error(request, "Invalid time selected.")
                return redirect("cron_management")

            # Construct cron expression
            if frequency == "daily":
                schedule = f"{minute} {hour} * * *"
            elif frequency == "weekly":
                # Default to Monday (1)
                schedule = f"{minute} {hour} * * 1"
            elif frequency == "monthly":
                # Default to 1st of month
                schedule = f"{minute} {hour} 1 * *"
            else:
                messages.error(request, "Invalid frequency.")
                return redirect("cron_management")

            # Update settings.CRONTAB dynamically
            try:
                from django_crontab.crontab import Crontab
                crontab = Crontab()
                crontab.load()  # load current crontab from settings

                # Remove existing job safely
                crontab.jobs = [job for job in crontab.jobs if job.name != job_id]

                # Add updated job
                job_command = next((j['command'] for j in cron_jobs if j['id'] == job_id), None)
                if job_command:
                    crontab.add_job(job_id, schedule, job_command)
                    crontab.write()
                    messages.success(request, f"Schedule for {job_id} updated to {hour}:{minute} ({frequency}).")
                else:
                    messages.error(request, "Job command not found.")

            except Exception as e:
                logger.error(f"Failed to update schedule for {job_id}: {str(e)}")
                messages.error(request, f"Failed to update schedule: {str(e)}")

        return redirect("cron_management")

    return render(request, "admin/cron_management.html", {"cron_jobs": cron_jobs})


def _is_valid_time(hour, minute):
    try:
        hour = int(hour)
        minute = int(minute)
        return 0 <= hour <= 23 and 0 <= minute <= 59
    except (ValueError, TypeError):
        return False
