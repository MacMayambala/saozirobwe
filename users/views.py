from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Module, UserModuleAccess
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserSession

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import CustomUser
from .models import UserSession  # assuming you have this model


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


MAX_FAILED_ATTEMPTS = 3

def user_login(request):
    """Handles user login and locks account after 3 failed attempts until superuser reactivates."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(username=username)
            custom_user = user_obj.customuser
        except (User.DoesNotExist, CustomUser.DoesNotExist):
            user_obj = None
            custom_user = None

        if user_obj and not user_obj.is_active:
            messages.error(request, "Your account is inactive. Please contact a Admin to reactivate.")
            return render(request, "login/auth/login.html")

        user = authenticate(request, username=username, password=password)

        if user:
            # Reset failed attempts after successful login
            if custom_user:
                custom_user.failed_login_attempts = 0
                custom_user.save()

            login(request, user)

            # Single-device login enforcement
            session_key = request.session.session_key
            UserSession.objects.filter(user=user).delete()
            UserSession.objects.create(user=user, session_key=session_key)

            request.session["2fa_verified"] = False
            return redirect("two_factor_auth")

        else:
            # Invalid login
            messages.error(request, "Invalid username or password.")

            # Increment failed login attempts
            if custom_user:
                custom_user.failed_login_attempts += 1
                if custom_user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                    user_obj.is_active = False  # deactivate account
                    user_obj.save()
                    messages.error(request, "Your account has been deactivated due to too many failed login attempts. Contact a Admin.")
                custom_user.save()

    return render(request, "login/auth/login.html")



from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserSession

@login_required
def user_logout(request):
    """Handles user logout and cleans up the active session."""
    # Delete the UserSession entry on logout
    UserSession.objects.filter(user=request.user).delete()

    # Log the user out
    logout(request)
    messages.success(request, "You have signed out 🙂")
    return redirect('login')  # Redirect to login page after logout


from django.contrib.auth.views import LogoutView
from .models import UserSession

class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        # Delete the UserSession entry on logout
        if request.user.is_authenticated:
            UserSession.objects.filter(user=request.user).delete()
        return super().dispatch(request, *args, **kwargs)
    



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.timezone import now
from datetime import timedelta
import random
import pyotp
import qrcode
import io
import base64

from .models import TwoFactorAuth

import random
import io
import base64
import pyotp
import qrcode
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages
from .models import TwoFactorAuth



# views.py
import random, io, base64, pyotp, qrcode
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import TwoFactorAuth  # Replace with your actual model
import random
import io
import base64
import pyotp
import qrcode
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from base64 import b32decode
from .models import TwoFactorAuth
import random
import io
import base64
import pyotp
import qrcode
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from base64 import b32decode
from .models import TwoFactorAuth

@login_required
@require_http_methods(["GET", "POST"])
def two_factorauth(request):
    user_2fa, _ = TwoFactorAuth.objects.get_or_create(user=request.user)

    if request.method == "POST":
        method = request.POST.get("method")
        if method not in ["email", "google_auth"]:
            messages.error(request, "Invalid 2FA method selected.")
            return render(request, "login/2fa/setup.html")

        if method == "google_auth":
            if user_2fa.mfa_enabled and user_2fa.auth_method == "google_auth" and user_2fa.secret_key:
                try:
                    b32decode(user_2fa.secret_key, casefold=False)
                    request.session["2fa_method"] = "google_auth"
                    return redirect("verify_2fa")
                except Exception:
                    user_2fa.mfa_enabled = False
                    user_2fa.secret_key = None
                    user_2fa.auth_method = None
                    user_2fa.save()
                    request.session["2fa_verified"] = False
            else:
                messages.error(request, "Google Authenticator not set up. Please onboard in Profile > 2FA Setup or use Email OTP.")
                return render(request, "login/2fa/setup.html")

        user_2fa.auth_method = method
        user_2fa.save()
        request.session["2fa_method"] = method

        if method == "email":
            otp_code = f"{random.randint(100000, 999999)}"
            user_2fa.email_otp = otp_code
            user_2fa.otp_created_at = now()
            user_2fa.save()

            email_content = render_to_string("email/otp_email_template.html", {
                "user_name": request.user.username,
                "otp": otp_code
            })
            email = EmailMultiAlternatives(
                subject="Verification Code",
                body="",
                from_email="Sao Zirobwe Sacco <noreply@saozirobwe.co.ug>",
                to=[request.user.email],
            )
            email.attach_alternative(email_content, "text/html")
            try:
                email.send()
                messages.success(request, "A verification code has been sent to your email.")
            except Exception as e:
                messages.error(request, "Failed to send email. Please try again.")
                print(f"Email sending error: {e}")
            return redirect("verify_2fa")

    return render(request, "login/2fa/setup.html")

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from datetime import timedelta
import pyotp
from base64 import b32decode
from .models import TwoFactorAuth

@login_required
@require_http_methods(["GET", "POST"])
def verify_2fa(request):
    try:
        user_2fa = TwoFactorAuth.objects.get(user=request.user)
    except TwoFactorAuth.DoesNotExist:
        messages.error(request, "2FA setup incomplete. Please try again.")
        return redirect("two_factor_auth")

    if request.method == "POST":
        input_code = request.POST.get("code")
        method = request.session.get("2fa_method")

        if not input_code or not method:
            messages.error(request, "Missing verification code or method.")
            return render(request, "login/2fa/verify.html", {"method": method})

        if method == "google_auth":
            if not user_2fa.secret_key:
                messages.error(request, "Google Authenticator setup incomplete.")
                return redirect("two_factor_auth")

            try:
                b32decode(user_2fa.secret_key, casefold=False)
            except Exception:
                messages.error(request, "Invalid 2FA secret key. Resetting 2FA.")
                user_2fa.secret_key = None
                user_2fa.mfa_enabled = False
                user_2fa.auth_method = None
                user_2fa.save()
                return redirect("two_factor_auth")

            if not input_code.isdigit() or len(input_code) != 6:
                messages.error(request, "Invalid code format. Please enter a 6-digit number.")
                return render(request, "login/2fa/verify.html", {"method": method})

            totp = pyotp.TOTP(user_2fa.secret_key)
            if totp.verify(input_code, valid_window=1):
                user_2fa.mfa_enabled = True
                user_2fa.auth_method = "google_auth"
                user_2fa.save()
                request.session["2fa_verified"] = True
                messages.success(request, "Login successful!")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid Google Authenticator code.")

        elif method == "email":
            if not user_2fa.email_otp or not user_2fa.otp_created_at:
                messages.error(request, "Email OTP not generated. Please try again.")
                return redirect("two_factor_auth")

            if (
                user_2fa.email_otp == input_code and
                now() - user_2fa.otp_created_at < timedelta(minutes=10)
            ):
                user_2fa.mfa_enabled = True
                user_2fa.auth_method = "email"
                user_2fa.save()
                request.session["2fa_verified"] = True
                messages.success(request, "2FA verification successful!")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid or expired email OTP.")

        else:
            messages.error(request, "Invalid 2FA method.")

    return render(request, "login/2fa/verify.html", {"method": request.session.get("2fa_method")})



from django.contrib import messages
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
import random


from django.contrib import messages
from django.shortcuts import redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
import random
from django.contrib.auth.decorators import login_required

@login_required
def resend_otp(request):
    user = request.user

    # Generate new OTP
    new_otp = random.randint(100000, 999999)

    # Store OTP in session
    request.session["otp"] = str(new_otp)  # Store as string to avoid serialization issues
    request.session.modified = True  # Ensure session updates

    # Check user's preferred OTP method
    try:
        preferred_method = getattr(user.profile, "otp_method", "email")  # Default to email
    except AttributeError:
        preferred_method = "email"  # Fallback if profile doesn't exist
        messages.warning(request, "OTP method not set, defaulting to email.")

    if preferred_method == "email":
        try:
            email_content = render_to_string("email/otp_email_template.html", {
                "user_name": user.username,
                "otp": new_otp
            })

            email = EmailMultiAlternatives(
                subject="Verification Code",
                body="Your OTP code is: {}".format(new_otp),  # Plain text fallback
                from_email="noreply@saozirobwe.co.ug",
                to=[user.email],
            )
            email.attach_alternative(email_content, "text/html")
            email.send()

            messages.success(request, "A new OTP has been sent to your email.")
        except Exception as e:
            messages.error(request, f"Failed to send OTP: {str(e)}")
    elif preferred_method == "authenticator":
        messages.error(request, "Use Google Authenticator to generate the OTP.")
    else:
        messages.error(request, "Unsupported OTP method. Contact support.")

    return redirect(reverse("verify_2fa"))




@login_required
def home(request):
    return render(request, 'dashboard.html') 

#######################################################################################################################

# views.py
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.http import HttpResponseRedirect

# Check if the user is a superuser
def superuser_required(user):
    return user.is_superuser

# Custom decorator to redirect non-superusers to the previous page with a message
def superuser_or_redirect(view_func):
    def wrapper(request, *args, **kwargs):
        if not superuser_required(request.user):
            messages.error(request, "You do not have permission to access this page. ")
            referer = request.META.get('HTTP_REFERER', 'dashboard')
            return HttpResponseRedirect(referer)
        return view_func(request, *args, **kwargs)
    return wrapper

# View to list all groups
@superuser_or_redirect
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'group_list.html', {'groups': groups})

# View to manage permissions for a group
@superuser_or_redirect
def manage_group_permissions(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    # Get all available permissions
    permissions = Permission.objects.all()
    # Get the permissions currently assigned to the group
    group_permissions = group.permissions.all().values_list('id', flat=True)

    if request.method == 'POST':
        # Get the selected permissions from the form
        selected_permissions = request.POST.getlist('permissions')
        # Clear existing permissions
        group.permissions.clear()
        # Add selected permissions
        for perm_id in selected_permissions:
            permission = Permission.objects.get(id=perm_id)
            group.permissions.add(permission)
        messages.success(request, f"Permissions for group '{group.name}' updated successfully!")
        return redirect('group_list')

    return render(request, 'manage_group_permissions.html', {
        'group': group,
        'permissions': permissions,
        'group_permissions': group_permissions
    })

# Existing views (user_list, manage_user_modules, update_user_modules) remain unchanged
@superuser_or_redirect
def user_list(request):
    users = User.objects.all()
    user_data = []
    for user in users:
        group = user.groups.first()
        role = group.name if group else "Not Assigned"
        user_data.append({
            'user': user,
            'role': role
        })
    return render(request, 'user_list.html', {'user_data': user_data})

@superuser_or_redirect
def manage_user_modules(request, user_id):
    user = get_object_or_404(User, id=user_id)
    modules = Module.objects.all()
    user_modules = UserModuleAccess.objects.filter(user=user).values_list('module__id', flat=True)
    return render(request, 'manage_user_modules.html', {
        'user': user,
        'modules': modules,
        'user_modules': user_modules
    })

@superuser_or_redirect
def update_user_modules(request, user_id):
    user = get_object_or_404(User, id=user_id)
    selected_modules = request.POST.getlist('modules')
    UserModuleAccess.objects.filter(user=user).delete()
    for module_id in selected_modules:
        module = Module.objects.get(id=module_id)
        UserModuleAccess.objects.create(user=user, module=module)
        messages.success(request, f"User {user.username} updated successfully!")
    return redirect('user_list')

@superuser_or_redirect
def setting(request):

    return render(request, 'all_settings.html')

################################################################
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import pyotp
import qrcode
import io
import base64
from base64 import b32decode
from .models import TwoFactorAuth

@login_required
@require_http_methods(["GET", "POST"])
def two_factor_setup(request):
    user_2fa, _ = TwoFactorAuth.objects.get_or_create(user=request.user)

    if user_2fa.mfa_enabled and user_2fa.auth_method == "google_auth" and user_2fa.secret_key:
        try:
            b32decode(user_2fa.secret_key, casefold=False)
            messages.info(request, "Google Authenticator is already set up.")
            return render(request, "users/2fa/setup_google.html", {"is_setup": True})
        except Exception:
            user_2fa.mfa_enabled = False
            user_2fa.secret_key = None
            user_2fa.auth_method = None
            user_2fa.save()

    if request.method == "POST":
        input_code = request.POST.get("code")
        if not input_code or not input_code.isdigit() or len(input_code) != 6:
            messages.error(request, "Invalid code format. Please enter a 6-digit number.")
            return redirect("two_factor_setup")

        if user_2fa.secret_key:
            try:
                b32decode(user_2fa.secret_key, casefold=False)
                totp = pyotp.TOTP(user_2fa.secret_key)
                if totp.verify(input_code, valid_window=1):
                    user_2fa.mfa_enabled = True
                    user_2fa.auth_method = "google_auth"
                    user_2fa.save()
                    messages.success(request, "Google Authenticator setup successful! Please log in again to continue.")
                    logout(request)  # Log the user out
                    return redirect("login")
                else:
                    messages.error(request, "Invalid Google Authenticator code.")
            except Exception:
                user_2fa.secret_key = None
                user_2fa.save()
                messages.error(request, "Invalid 2FA secret key. Please try again.")
        else:
            messages.error(request, "Setup incomplete. Please scan the QR code again.")
        return redirect("two_factor_setup")

    # Generate new secret key and QR code
    user_2fa.secret_key = pyotp.random_base32()
    try:
        b32decode(user_2fa.secret_key, casefold=False)
        user_2fa.save()
    except Exception:
        messages.error(request, "Failed to generate valid 2FA key. Please try again.")
        print(f"Key generation error: Invalid base32 key generated")
        return redirect("two_factor_setup")

    otp_uri = pyotp.TOTP(user_2fa.secret_key).provisioning_uri(
        name=request.user.email or f"user{request.user.id}@example.com",
        issuer_name="SAO Zirobwe SACCO"
    )
    print("Generated OTP URI:", otp_uri)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=6,
    )
    qr.add_data(otp_uri)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    qr_image.save(buffer, format="PNG")
    buffer.seek(0)
    qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")
    qr_code_data_uri = f"data:image/png;base64,{qr_code}"

    return render(request, "login/2fa/setup_google.html", {
        "qrcode": qr_code_data_uri,
        "secret_key": user_2fa.secret_key,
        "is_setup": False
    })
# users/views.py
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from users.forms import CustomUserCreationForm, CustomUserEditForm
from users.models import CustomUser

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from users.forms import CustomUserCreationForm
from users.models import CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from .models import CustomUser

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from .models import CustomUser

@login_required
@superuser_or_redirect
def create_user(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Only admins can create users.")
        return redirect("user_list")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save user with password
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()  # Save user first

            # Let form handle branch, groups, and modules
            form.save(commit=True)  # Calls CustomUserCreationForm.save()

            # Set password_expired
            custom_user, created = CustomUser.objects.get_or_create(user=user)
            custom_user.password_expired = True  # Force password change
            custom_user.save()

            messages.success(request, f"User {user.username} created successfully! Password will expire on first login.")
            return redirect("user_list")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()

    return render(request, "users/create_user.html", {"form": form})


   
@login_required
@superuser_or_redirect 
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Only admins can edit users.")
        return redirect("user_list")
    
    if request.method == "POST":
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            # Update group assignments
            groups = form.cleaned_data['groups']
            user.groups.set(groups)
            messages.success(request, "User updated successfully!")
            return redirect("user_list")
    else:
        form = CustomUserEditForm(instance=user)
    
    return render(request, "users/edit_user.html", {"form": form, "user": user})

@login_required
@superuser_or_redirect 
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Permission denied.")
        return redirect("user_list")

    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User {user.username} has been {status}.")
    return redirect("user_list")

@login_required
@superuser_or_redirect 
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Permission denied.")
        return redirect("user_list")

    if request.method == "POST":
        user.delete()
        messages.success(request, f"User {user.username} has been deleted.")
        return redirect("user_list")

    return render(request, "users/confirm_delete.html", {"user": user})
################################################################################################################
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now, timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from .forms import PasswordResetRequestForm, SetNewPasswordForm
import random

# Temporary OTP storage (can be saved in DB or session)
from django.contrib.sessions.backends.db import SessionStore

# =========================
# FORGOT PASSWORD VIEW
# =========================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.timezone import now
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import timedelta
import random

from .forms import PasswordResetRequestForm, SetNewPasswordForm
from .models import PasswordHistory


# =========================
# FORGOT PASSWORD
# =========================
def forgot_password(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
                
                # Generate OTP
                otp_code = f"{random.randint(100000, 999999)}"
                request.session["password_reset_otp"] = otp_code
                request.session["password_reset_user"] = user.id
                request.session["otp_created_at"] = now().isoformat()

                # Send OTP email
                email_content = render_to_string("email/otp_email_template.html", {
                    "user_name": user.username,
                    "otp": otp_code
                })
                email_message = EmailMultiAlternatives(
                    subject="Password Reset OTP",
                    body="",
                    from_email="Sao Zirobwe Sacco <noreply@saozirobwe.co.ug>",
                    to=[user.email]
                )
                email_message.attach_alternative(email_content, "text/html")
                email_message.send()

                messages.success(request, "A password reset OTP has been sent to your email.")
                return redirect("reset_password_verify")
            except User.DoesNotExist:
                messages.error(request, "No user found with this email.")
    else:
        form = PasswordResetRequestForm()
    return render(request, "users/forgot_password.html", {"form": form})


# =========================
# VERIFY OTP BEFORE RESET
# =========================
def reset_password_verify(request):
    if request.method == "POST":
        otp_input = request.POST.get("otp")
        otp_saved = request.session.get("password_reset_otp")
        otp_time = request.session.get("otp_created_at")
        user_id = request.session.get("password_reset_user")

        if not otp_saved or not otp_time or not user_id:
            messages.error(request, "OTP session expired. Please try again.")
            return redirect("forgot_password")

        from django.utils.dateparse import parse_datetime
        try:
            otp_created = parse_datetime(otp_time)
        except:
            otp_created = now() - timedelta(minutes=11)

        if now() - otp_created > timedelta(minutes=10):
            messages.error(request, "OTP expired. Please request a new one.")
            return redirect("forgot_password")

        if otp_input == otp_saved:
            messages.success(request, "OTP verified. You can now reset your password.")
            return redirect("reset_password_set")
        else:
            messages.error(request, "Invalid OTP. Try again.")

    return render(request, "users/reset_password_verify.html")


# =========================
# SET NEW PASSWORD VIEW WITH PASSWORD REUSE CHECK
# =========================
def reset_password_set(request):
    user_id = request.session.get("password_reset_user")
    if not user_id:
        messages.error(request, "Session expired. Please request password reset again.")
        return redirect("forgot_password")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = SetNewPasswordForm(user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get("new_password1")

            # Check password reuse
            previous_passwords = PasswordHistory.objects.filter(user=user)
            for old in previous_passwords:
                if user.check_password(new_password):
                    form.add_error("new_password1", "You cannot reuse a previous password.")
                    return render(request, "users/reset_password_set.html", {"form": form})

            # Save new password
            form.save()

            # Add to password history
            PasswordHistory.objects.create(user=user, password=user.password)

            # Optional: keep only last 5 passwords
            history = PasswordHistory.objects.filter(user=user).order_by('-created_at')
            if history.count() > 5:
                for old_pw in history[5:]:
                    old_pw.delete()

            # Clear session
            request.session.pop("password_reset_otp", None)
            request.session.pop("password_reset_user", None)
            request.session.pop("otp_created_at", None)

            messages.success(request, "Password reset successful! You can now log in.")
            return redirect("login")
    else:
        form = SetNewPasswordForm(user)

    return render(request, "users/reset_password_set.html", {"form": form})


from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.models import User
from .forms import CustomSetPasswordForm  # <-- Add this import
from django.utils import timezone

def users_list(request):
    users = User.objects.all().select_related('customuser__branch')
    # add branch_name attribute to each user
    for u in users:
        u.branch_name = getattr(u.customuser.branch, "name", "N/A") if hasattr(u, "customuser") else "N/A"
    return render(request, 'users/user_list.html', {'users': users})

@login_required
def force_password_change(request):
    if request.method == "POST":
        form = CustomSetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Update expiration flags
            custom_user = request.user.customuser
            custom_user.password_expired = False
            custom_user.last_password_change = timezone.now()  # 👈 mark new date
            custom_user.save()

            # Save password in history
            PasswordHistory.objects.create(user=request.user, password=request.user.password)

            messages.success(request, "Password updated successfully! Please continue.")
            return redirect("two_factor_auth")
    else:
        form = CustomSetPasswordForm(user=request.user)

    return render(request, "users/force_password_change.html", {"form": form})
