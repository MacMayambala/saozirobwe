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

@login_required
def settings(request):
    return render(request, 'settings.html')

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
