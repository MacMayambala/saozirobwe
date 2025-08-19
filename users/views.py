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

def user_login(request):
    """Handles user login, enforces single-device login, and redirects to 2FA setup if successful."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            # Log the user in
            login(request, user)

            # Get the current session key
            session_key = request.session.session_key

            # Invalidate any existing session for this user
            UserSession.objects.filter(user=user).delete()

            # Store the new session key
            UserSession.objects.create(user=user, session_key=session_key)

            # Ensure 2FA is required
            request.session["2fa_verified"] = False
            return redirect("two_factor_auth")  # Redirect to 2FA setup
        else:
            messages.error(request, "Invalid username or password.")

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

@login_required
def resend_otp(request):
    user = request.user

    # Generate new OTP
    new_otp = random.randint(100000, 999999)

    # Store OTP in session
    request.session["otp"] = new_otp
    request.session.modified = True  # Ensure session updates

    # Check user's preferred OTP method
    preferred_method = getattr(user.profile, "otp_method", "email")  # Default to email

    if preferred_method == "email":
        try:
            email_content = render_to_string("email/otp_email_template.html", {
                "user_name": user.username,
                "otp": new_otp
            })

            email = EmailMultiAlternatives(
                subject="Verification Code",
                body="",
                from_email="noreply@saozirobwe.co.ug",
                to=[user.email],
            )
            email.attach_alternative(email_content, "text/html")
            email.send()

            messages.success(request, "A new OTP has been sent to your email.")
        except Exception as e:
            messages.error(request, f"Failed to send OTP: {e}")
    
    else:
        messages.error(request, "Use Google Authenticator to generate the OTP.")

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
            messages.error(request, "You do not have permission to access this page. Only superusers are allowed.")
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