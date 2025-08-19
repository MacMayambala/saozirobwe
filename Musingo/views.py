import logging
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.auth.models import User
from .models import DocumentCustody, Customer, DocumentActionLog
from .forms import DocumentCustodyForm, ReleaseDocumentForm

logger = logging.getLogger(__name__)

@login_required
def document_list(request):
    query = request.GET.get("q", "")
    documents = DocumentCustody.objects.select_related("customer").all()
    if query:
        documents = documents.filter(customer__member_number__icontains=query)
    documents = documents.order_by("-date_received")
    paginator = Paginator(documents, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    users = User.objects.filter(is_active=True).order_by("username") if request.user.is_staff or request.user.is_superuser else None
    return render(request, "document_list.html", {"page_obj": page_obj, "query": query, "users": users})

@login_required
def admin_document_list(request):
    """Displays all documents for admins (staff) and superusers"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only admins can access this page.")
        return redirect("document_list")

    query = request.GET.get('q', '')
    documents = DocumentCustody.objects.all()
    if query:
        # Filter by customer member_number or other relevant field instead of account_number
        documents = documents.filter(customer__member_number__icontains=query)
    
    # Order by most recent date_received (descending order)
    documents = documents.order_by('-date_received')
    
    paginator = Paginator(documents, 10)  # 10 documents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'document_list.html', {
        'page_obj': page_obj,
        'query': query,
    })

@login_required
def document_list(request):
    query = request.GET.get("q", "")
    documents = DocumentCustody.objects.select_related("customer").filter(requested_by=request.user)
    if query:
        documents = documents.filter(customer__member_number__icontains=query)
    documents = documents.order_by("-date_received")
    paginator = Paginator(documents, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "document_list.html", {"page_obj": page_obj, "query": query})

@login_required
def active_list(request):
    query = request.GET.get("q", "")
    documents = DocumentCustody.objects.select_related("customer").exclude(status="returned")
    if query:
        documents = documents.filter(customer__member_number__icontains=query)
    documents = documents.order_by("-date_received")
    paginator = Paginator(documents, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "active_musingo.html", {"page_obj": page_obj, "query": query})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.http import HttpResponseBadRequest
from django.db import transaction
from django.utils import timezone
from .models import DocumentCustody, DocumentActionLog
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

@login_required
def document_detail(request, pk):
    """Display document details with action logs and users for select fields"""
    document = get_object_or_404(DocumentCustody, pk=pk)
    action_logs = document.action_logs.all().order_by('-performed_at')
    users = User.objects.filter(is_active=True).order_by('username')
    logger.debug(f"Rendering document detail for pk={pk}, user={request.user.username}")
    context = {
        'document': document,
        'action_logs': action_logs,
        'users': users,
    }
    return render(request, 'document_details.html', context)

@login_required
def request_document(request, pk):
    """Handle document request by regular users"""
    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, "Only regular users can request documents.")
        logger.warning(f"Unauthorized request attempt for document {pk} by {request.user.username}")
        return redirect("admin_document_list" if request.user.is_staff else "document_list")

    if request.method != "POST":
        logger.warning(f"Invalid request method for request_document by {request.user.username}")
        return HttpResponseBadRequest("Invalid request method.")

    document = get_object_or_404(DocumentCustody, pk=pk)
    password = request.POST.get("password")
    comment = request.POST.get("comment")
    logger.debug(f"Processing request for document {pk} by {request.user.username}")

    user = authenticate(username=request.user.username, password=password)
    if not user:
        messages.error(request, "Invalid password. Request failed.")
        logger.warning(f"Invalid password for request_document {pk} by {request.user.username}")
        return redirect("admin_document_list" if request.user.is_staff else "document_list")

    try:
        with transaction.atomic():
            if document.status != "available":
                messages.error(request, "This document cannot be requested because it is not available.")
                logger.warning(f"Document {pk} not available for request by {request.user.username}")
                return redirect("admin_document_list" if request.user.is_staff else "document_list")
            document.status = "requested"
            document.requested_by = user
            document.date_requested = timezone.now()
            document.save()

            DocumentActionLog.objects.create(
                document=document,
                action_type="REQUEST",
                comment=comment,
                performed_by=user
            )

            messages.success(request, "Document request sent successfully.")
            logger.info(f"Document {pk} requested by {request.user.username}")
    except Exception as e:
        messages.error(request, f"Error requesting document: {str(e)}")
        logger.error(f"Error requesting document {pk}: {str(e)}", exc_info=True)

    return redirect("admin_document_list" if request.user.is_staff else "document_list")

@login_required
def acknowledge_document(request, pk):
    """Handle document acknowledgment by staff"""
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to acknowledge documents.")
        logger.warning(f"Unauthorized acknowledge attempt for document {pk} by {request.user.username}")
        return redirect("admin_document_list")

    if request.method != "POST":
        logger.warning(f"Invalid request method for acknowledge_document by {request.user.username}")
        return HttpResponseBadRequest("Invalid request method.")

    document = get_object_or_404(DocumentCustody, pk=pk)
    password = request.POST.get("password")
    comment = request.POST.get("comment")

    user = authenticate(username=request.user.username, password=password)
    if not user:
        messages.error(request, "Invalid password. Acknowledgement failed.")
        logger.warning(f"Invalid password for acknowledge_document {pk} by {request.user.username}")
        return redirect("admin_document_list")

    try:
        with transaction.atomic():
            if document.status != "Pending":
                messages.error(request, "Only pending documents can be acknowledged.")
                logger.warning(f"Document {pk} not in Pending status for acknowledge by {request.user.username}")
                return redirect("admin_document_list")
            document.status = "branch"
            document.acknowledged_by = user
            document.date_acknowledged = timezone.now()
            document.save()

            DocumentActionLog.objects.create(
                document=document,
                action_type="ACKNOWLEDGE",
                comment=comment,
                performed_by=user
            )

            messages.success(request, f"Document '{document.get_document_type_display()}' acknowledged successfully.")
            logger.info(f"Document {pk} acknowledged by {request.user.username}")
    except Exception as e:
        messages.error(request, f"Error acknowledging document: {str(e)}")
        logger.error(f"Error acknowledging document {pk}: {str(e)}", exc_info=True)

    return redirect("admin_document_list")

@login_required
def approve_document(request, pk):
    """Handle document approval by staff or superuser"""
    if request.method != "POST":
        logger.warning(f"Invalid request method for approve_document by {request.user.username}")
        return HttpResponseBadRequest("Invalid request method.")
    
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "You do not have permission to approve documents.")
        logger.warning(f"Unauthorized approve attempt for document {pk} by {request.user.username}")
        return redirect("admin_document_list" if request.user.is_staff else "document_list")
    
    document = get_object_or_404(DocumentCustody, pk=pk)
    password = request.POST.get("password")
    comment = request.POST.get("comment")
    
    user = authenticate(username=request.user.username, password=password)
    if not user:
        messages.error(request, "Invalid password. Approval failed.")
        logger.warning(f"Invalid password for approve_document {pk} by {request.user.username}")
        return redirect("admin_document_list")
    
    try:
        with transaction.atomic():
            if document.status != "branch":
                messages.error(request, "Only documents at Branch can be approved.")
                logger.warning(f"Document {pk} not in branch status for approve by {request.user.username}")
                return redirect("admin_document_list")
            document.status = "available"
            document.approved_by = user
            document.date_approved = timezone.now()
            document.save()
            
            DocumentActionLog.objects.create(
                document=document,
                action_type="APPROVE",
                comment=comment,
                performed_by=user
            )
            
            messages.success(request, "Document approved successfully and set to Available.")
            logger.info(f"Document {pk} approved by {request.user.username}")
    except Exception as e:
        messages.error(request, f"Error approving document: {str(e)}")
        logger.error(f"Error approving document {pk}: {str(e)}", exc_info=True)
    
    return redirect("admin_document_list")

@login_required
def authorise_document(request, pk):
    """Handle document authorization by staff or superuser"""
    if request.method != "POST":
        logger.warning(f"Invalid request method for authorise_document by {request.user.username}")
        return HttpResponseBadRequest("Invalid request method.")
    
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "You do not have permission to authorise documents.")
        logger.warning(f"Unauthorized authorise attempt for document {pk} by {request.user.username}")
        return redirect("admin_document_list" if request.user.is_staff else "document_list")
    
    document = get_object_or_404(DocumentCustody, pk=pk)
    password = request.POST.get("password")
    comment = request.POST.get("comment")
    
    user = authenticate(username=request.user.username, password=password)
    if not user:
        messages.error(request, "Invalid password. Authorisation failed.")
        logger.warning(f"Invalid password for authorise_document {pk} by {request.user.username}")
        return redirect("admin_document_list")
    
    try:
        with transaction.atomic():
            if document.status != "requested":
                messages.error(request, "Only requested documents can be authorised.")
                logger.warning(f"Document {pk} not in requested status for authorise by {request.user.username}")
                return redirect("admin_document_list")
            document.status = "authorised"
            document.authorised_by = user
            document.date_authorised = timezone.now()
            document.save()
            
            DocumentActionLog.objects.create(
                document=document,
                action_type="AUTHORISE",
                comment=comment,
                performed_by=user
            )
            
            messages.success(request, "Document authorised successfully.")
            logger.info(f"Document {pk} authorised by {request.user.username}")
    except Exception as e:
        messages.error(request, f"Error authorising document: {str(e)}")
        logger.error(f"Error authorising document {pk}: {str(e)}", exc_info=True)
    
    return redirect("admin_document_list")

@login_required
def release_document(request, pk):
    """Handle document release by staff or superuser"""
    if request.method != "POST":
        logger.warning(f"Invalid request method for release_document by {request.user.username}")
        return HttpResponseBadRequest("Invalid request method.")
    
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "You do not have permission to release documents.")
        logger.warning(f"Unauthorized release attempt for document {pk} by {request.user.username}")
        return redirect("admin_document_list" if request.user.is_staff else "document_list")
    
    document = get_object_or_404(DocumentCustody, pk=pk)
    password = request.POST.get("password")
    comment = request.POST.get("comment")
    collected_by_id = request.POST.get("collected_by")
    
    if not collected_by_id:
        messages.error(request, "Collected by is required for releasing the document.")
        logger.warning(f"Missing collected_by for release_document {pk} by {request.user.username}")
        return redirect("admin_document_list")
    
    user = authenticate(username=request.user.username, password=password)
    if not user:
        messages.error(request, "Invalid password. Release failed.")
        logger.warning(f"Invalid password for release_document {pk} by {request.user.username}")
        return redirect("admin_document_list")
    
    try:
        with transaction.atomic():
            if document.status != "authorised":
                messages.error(request, "Only authorised documents can be released.")
                logger.warning(f"Document {pk} not in authorised status for release by {request.user.username}")
                return redirect("admin_document_list")
            
            collected_by = User.objects.get(id=collected_by_id)
            document.status = "released"
            document.released_by = user
            document.date_released = timezone.now()
            document.collected_by = collected_by
            document.save()
            
            DocumentActionLog.objects.create(
                document=document,
                action_type="RELEASE",
                comment=comment,
                performed_by=user
            )
            
            messages.success(request, f"Document released successfully to {collected_by.get_full_name() or collected_by.username}.")
            logger.info(f"Document {pk} released to {collected_by.username} by {request.user.username}")
    except Exception as e:
        messages.error(request, f"Error releasing document: {str(e)}")
        logger.error(f"Error releasing document {pk}: {str(e)}", exc_info=True)
    
    return redirect("admin_document_list")

@login_required
def deliver_document(request, pk):
    """Handle document delivery by authorized user"""
    document = get_object_or_404(DocumentCustody, pk=pk)
    
    if document.status != "released" or not document.collected_by or document.collected_by != request.user:
        messages.error(request, "Not authorized to deliver this document.")
        logger.warning(f"Unauthorized delivery attempt for document {pk} by {request.user.username}")
        return redirect("admin_document_list")
    
    if request.method != "POST":
        logger.warning(f"Invalid request method for deliver_document by {request.user.username}")
        return HttpResponseBadRequest("Invalid request method.")
    
    password = request.POST.get("password")
    comment = request.POST.get("comment")
    user_select_id = request.POST.get("user_select")
    
    if not user_select_id:
        messages.error(request, "Please select a user.")
        logger.warning(f"No user selected for document {pk} delivery by {request.user.username}")
        return redirect("admin_document_list")
    
    user = authenticate(username=request.user.username, password=password)
    if not user:
        messages.error(request, "Invalid password. Delivery failed.")
        logger.warning(f"Invalid password for deliver_document {pk} by {request.user.username}")
        return redirect("admin_document_list")
    
    try:
        with transaction.atomic():
            selected_user = User.objects.get(id=user_select_id)
            document.delivered_by = selected_user
            document.status = "delivered"
            document.date_delivered = timezone.now()
            document.save()
            
            DocumentActionLog.objects.create(
                document=document,
                action_type="DELIVER",
                comment=comment,
                performed_by=user
            )
            
            messages.success(request, f"Document delivered successfully to {selected_user.get_full_name() or selected_user.username}.")
            logger.info(f"Document {pk} delivered to {selected_user.username} by {request.user.username}")
    except User.DoesNotExist:
        messages.error(request, "Invalid user selected.")
        logger.error(f"Invalid user ID {user_select_id} for document {pk} delivery")
    except Exception as e:
        messages.error(request, f"Error delivering document: {str(e)}")
        logger.error(f"Error delivering document {pk}: {str(e)}", exc_info=True)
    
    return redirect("admin_document_list")

@login_required
def return_document(request, pk):
    """Handle document return by authorized user"""
    document = get_object_or_404(DocumentCustody, pk=pk)
    
    if document.status != "delivered" or not document.delivered_by or document.delivered_by != request.user:
        messages.error(request, "Not authorized to return this document.")
        logger.warning(f"Unauthorized return attempt for document {pk} by {request.user.username}")
        return redirect("admin_document_list")
    
    if request.method != "POST":
        logger.warning(f"Invalid request method for return_document by {request.user.username}")
        return HttpResponseBadRequest("Invalid request method.")
    
    password = request.POST.get("password")
    comment = request.POST.get("comment")
    recipient = request.POST.get("recipient")
    
    if not recipient:
        messages.error(request, "Recipient is required for returning the document.")
        logger.warning(f"Missing recipient for return_document {pk} by {request.user.username}")
        return redirect("admin_document_list")
    
    user = authenticate(username=request.user.username, password=password)
    if not user:
        messages.error(request, "Invalid password. Return failed.")
        logger.warning(f"Invalid password for return_document {pk} by {request.user.username}")
        return redirect("admin_document_list")
    
    try:
        with transaction.atomic():
            if recipient == "customer":
                document.returned_to_name = f"{document.customer.first_name} {document.customer.surname}"
                document.returned_to_phone = document.customer.phone
            elif recipient == "next_of_kin" and document.next_of_kin_name:
                document.returned_to_name = document.next_of_kin_name
                document.returned_to_phone = document.next_of_kin_phone
            else:
                messages.error(request, "Invalid recipient selected.")
                logger.warning(f"Invalid recipient for return_document {pk} by {request.user.username}")
                return redirect("admin_document_list")
            document.status = "returned"
            document.save()
            
            DocumentActionLog.objects.create(
                document=document,
                action_type="RETURN",
                comment=comment,
                performed_by=user
            )
            
            messages.success(request, "Document returned successfully.")
            logger.info(f"Document {pk} returned by {request.user.username}")
    except Exception as e:
        messages.error(request, f"Error returning document: {str(e)}")
        logger.error(f"Error returning document {pk}: {str(e)}", exc_info=True)
    
    return redirect("admin_document_list")

@login_required
def reverse_action(request, pk):
    """Handle action reversal by superuser"""
    if request.method != "POST":
        logger.warning(f"Invalid request method for reverse_action by {request.user.username}")
        return HttpResponseBadRequest("Invalid request method.")
    
    if not request.user.is_superuser:
        messages.error(request, "Only superusers can reverse actions.")
        logger.warning(f"Unauthorized reverse attempt for document {pk} by {request.user.username}")
        return redirect("admin_document_list" if request.user.is_staff else "document_list")
    
    document = get_object_or_404(DocumentCustody, pk=pk)
    password = request.POST.get("password")
    comment = request.POST.get("comment")
    
    user = authenticate(username=request.user.username, password=password)
    if not user:
        messages.error(request, "Invalid password. Reverse failed.")
        logger.warning(f"Invalid password for reverse_action {pk} by {request.user.username}")
        return redirect("admin_document_list")
    
    try:
        with transaction.atomic():
            transitions = {
                "branch": ("Pending", {"acknowledged_by": None, "date_acknowledged": None}),
                "available": ("branch", {"approved_by": None, "date_approved": None}),
                "requested": ("available", {"requested_by": None, "date_requested": None}),
                "authorised": ("requested", {"authorised_by": None, "date_authorised": None}),
                "released": ("authorised", {"released_by": None, "date_released": None, "collected_by": None}),
                "delivered": ("released", {"delivered_by": None, "date_delivered": None}),
                "returned": ("delivered", {"returned_to_name": None, "returned_to_phone": None}),
            }
            logger.info(f"Current document {pk} status: {document.status}")
            
            if document.status == "Pending":
                messages.error(request, "No previous state to revert to from Pending.")
                logger.warning(f"Cannot reverse document {pk} from Pending by {request.user.username}")
                return redirect("admin_document_list")
            
            transition = transitions.get(document.status)
            if not transition:
                logger.error(f"Invalid status {document.status} for document {pk}")
                messages.error(request, f"Cannot reverse document with status '{document.get_status_display()}'.")
                return redirect("admin_document_list")
            
            new_status, fields = transition
            logger.info(f"Reverting document {pk} from {document.status} to {new_status} with fields {fields}")
            document.status = new_status
            for field, value in fields.items():
                setattr(document, field, value)
            document.save()
            
            DocumentActionLog.objects.create(
                document=document,
                action_type="REVERSE",
                comment=comment,
                performed_by=user
            )
            
            logger.info(f"Document {pk} saved with status: {document.status}")
            messages.success(request, f"Document reverted to {document.get_status_display()}.")
            logger.info(f"Document {pk} reversed to {document.status} by {request.user.username}")
    except Exception as e:
        logger.error(f"Error reversing document {pk}: {str(e)}", exc_info=True)
        messages.error(request, f"Error reversing action: {str(e)}")
    
    return redirect("admin_document_list")


@login_required
def register_document(request, cus_id):
    customer = get_object_or_404(Customer, cus_id=cus_id)
    if request.method == "POST":
        form = DocumentCustodyForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    document = form.save(commit=False)
                    document.customer = customer
                    document.received_by = request.user
                    document.date_received = timezone.now()
                    document.status = "Pending"
                    document.save()
                    messages.success(
                        request,
                        f"Document '{document.get_document_type_display()}' registered successfully for {customer.first_name} {customer.surname}.",
                    )
                    logger.info(f"Document registered for customer {cus_id} by {request.user.username}")
                    return redirect("admin_document_list")
            except Exception as e:
                messages.error(request, f"Error registering document: {str(e)}")
                logger.error(f"Error registering document for customer {cus_id}: {str(e)}", exc_info=True)
        else:
            messages.error(request, "Please correct the errors below.")
            logger.warning(f"Invalid form data for registering document by {request.user.username}")
    else:
        form = DocumentCustodyForm()
    return render(request, "register_document.html", {"customer": customer, "form": form})

@login_required
def dashboard(request):
    total_documents = DocumentCustody.objects.count()
    active_documents = DocumentCustody.objects.filter(status="available").count()
    requested_documents = DocumentCustody.objects.filter(status="requested").count()
    recent_documents = DocumentCustody.objects.select_related("customer").order_by("-date_received")[:5]
    context = {
        "total_documents": total_documents,
        "active_documents": active_documents,
        "requested_documents": requested_documents,
        "recent_documents": recent_documents,
    }
    return render(request, "dashboard.html", context)

@login_required
def muno(request):
    return render(request, "register_Musingo.html")