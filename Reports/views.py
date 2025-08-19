from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import Q
from Munomukabi.models import Member
from Munomukabi.models import Member
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.contrib.auth.models import User

from datetime import datetime
import openpyxl
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from Reports.models import UserActivity
from django.http import JsonResponse



@login_required
def customer_list(request):
    """Render the customer list page with the most recent customer"""
    latest_customer = Member.objects.order_by('-id').first()  # Get the most recent customer
    return render(request, 'member.html', {'latest_customer': latest_customer})
@login_required
def get_customer_details(request):
    """Return customer details when an account number is entered"""
    account_number = request.GET.get('account_number', None)
    if account_number:
        try:
            customer = Member.objects.get(account_number=account_number)
            data = {
                'name': Member.name,
                'account_number': Member.account_number,
                'branch': Member.branch,
                'gender': Member.gender,
               # 'age': Member.age,
                'village': Member.village,
            }
            return JsonResponse(data)
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def user_activity_report(request):
    activities = UserActivity.objects.all().order_by('-timestamp')  # Get latest actions first
    
    UserActivity.objects.create(user=request.user, action="Logged in")
    return render(request, 'reports/user_activity_report.html', {'activities': activities})
@login_required
def member(request):
    return render(request,'member.html')

@login_required
def export_members_to_excel(request):
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter members based on date range
    members = Member.objects.all()
    if start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

            if start_date_obj <= end_date_obj:
                members = members.filter(registration_date__range=[start_date, end_date])
        except ValueError:
            pass  # Ignore errors and return all members

    # Create an Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Members"

    # Write the headers
    headers = ["Name", "Account Number", "Phone", "Registration Date", "Subscription Start", "Subscription End", "Branch"]
    ws.append(headers)

    # Write member data
    for member in members:
        ws.append([
            member.name,
            member.account_number,
            member.phone,
            member.registration_date.strftime("%Y-%m-%d") if member.registration_date else "",
            member.subscription_start.strftime("%Y-%m-%d") if member.subscription_start else "",
            member.subscription_end.strftime("%Y-%m-%d") if member.subscription_end else "",
            member.branch
        ])

    # Create HTTP response with Excel file
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="members.xlsx"'
    wb.save(response)
    UserActivity.objects.create(user=request.user, action="Exported Members PDF")
    return response

@login_required
def export_members_to_pdf(request):
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter members based on date range
    members = Member.objects.all()
    if start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

            if start_date_obj <= end_date_obj:
                members = members.filter(registration_date__range=[start_date, end_date])
        except ValueError:
            pass  # Ignore errors and return all members

    # Create a PDF response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="members.pdf"'

    # Create PDF canvas
    pdf = canvas.Canvas(response, pagesize=A4)
    pdf.setTitle("Members Report")
    
    # Add Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 800, "SAO Zirobwe SACCO - Members Report")

    # Table headers
    pdf.setFont("Helvetica-Bold", 10)
    headers = ["Name", "Account Number", "Phone", "Registration Date", "Branch"]
    
    x_start = 50
    y_start = 760
    spacing = 20  # Space between rows

    for i, header in enumerate(headers):
        pdf.drawString(x_start + (i * 110), y_start, header)

    # Table content
    pdf.setFont("Helvetica", 10)
    y_position = y_start - spacing

    for member in members:
        pdf.drawString(x_start, y_position, member.name[:15])  # Name
        pdf.drawString(x_start + 110, y_position, str(member.account_number))  # Account Number
        pdf.drawString(x_start + 220, y_position, member.phone)  # Phone
        pdf.drawString(x_start + 330, y_position, member.registration_date.strftime("%Y-%m-%d"))  # Registration Date
        pdf.drawString(x_start + 440, y_position, member.branch[:10])  # Branch
        y_position -= spacing

        # Add new page if space runs out
        if y_position < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y_position = 760

    pdf.save()
    return response


# Report 1: Members in a selected date range
@login_required
def members_in_date_range(request):
    members = Member.objects.all()  # Get all members by default

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        members = members.filter(registration_date__range=[start_date, end_date])
        for member in members:
            member.update_status() 
    return render(request, 'reports/all_members.html', {'members': members})

# Report 2: Members with active subscriptions
@login_required
def active_subscriptions(request):
    today = now().date()
    members = Member.objects.filter(subscription_start__lte=today, subscription_end__gte=today)
    return render(request, "reports/active_subscriptions.html", {"members": members})

# Report 3: Members with expired subscriptions
@login_required
def expired_subscriptions(request):
    today = now().date()
    members = Member.objects.filter(subscription_end__lt=today)
    UserActivity.objects.create(user=request.user, action="Searched for Expired Subscription")
    return render(request, "reports/expired_subscriptions.html", {"members": members})

# Report 4: All members with their subscription status
@login_required
def all_members_with_subscription_status(request):
    members = Member.objects.all()
    for member in members:
     member.update_status() 

    UserActivity.objects.create(user=request.user, action="Searched for Expired Subscription")
    return render(request, "reports/all_members.html", {"members": members})



#################################################################################################################################
# your_app_name/views.py
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import UserActivity  # Adjust to your model name if different
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import datetime
@login_required
@require_GET
def search_activities(request):
    search_query = request.GET.get('search', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    page = int(request.GET.get('page', 1))

    activities = UserActivity.objects.all().order_by('-timestamp')

    if search_query:
        activities = activities.filter(
            Q(user__username__icontains=search_query) |
            Q(action__icontains=search_query)
        )
    
    if start_date:
        try:
            start_date = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            activities = activities.filter(timestamp__gte=start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            activities = activities.filter(timestamp__lte=end_date)
        except ValueError:
            pass

    paginator = Paginator(activities, 10)  # 10 items per page
    page_obj = paginator.get_page(page)

    activities_list = [
        {
            'user': {'username': activity.user.username},
            'action': activity.action,
            'timestamp': activity.timestamp.isoformat(),
            'ip_address': activity.ip_address
        }
        for activity in page_obj
    ]

    response_data = {
        'activities': activities_list,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    }

    return JsonResponse(response_data)