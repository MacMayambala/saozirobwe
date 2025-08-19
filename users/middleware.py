from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from .models import TwoFactorAuth
from base64 import b32decode

class TwoFactorMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        allowed_paths = ["/2fa/setup/", "/2fa/verify/", "/2fa/onboard/", "/logout/", "/login/"]
        if request.path in allowed_paths:
            return None

        try:
            user_2fa = TwoFactorAuth.objects.get(user=request.user)
        except TwoFactorAuth.DoesNotExist:
            return redirect("two_factor_auth")

        if user_2fa.secret_key:
            try:
                b32decode(user_2fa.secret_key, casefold=False)
            except Exception:
                user_2fa.mfa_enabled = False
                user_2fa.secret_key = None
                user_2fa.auth_method = None
                user_2fa.save()
                request.session["2fa_verified"] = False
                return redirect("two_factor_auth")

        verified = request.session.get("2fa_verified", False)

        if user_2fa.auth_method and not verified:
            request.session["2fa_method"] = user_2fa.auth_method
            return redirect("verify_2fa")
        elif not user_2fa.auth_method:
            return redirect("two_factor_auth")

        return None
###########################################################################################################################################
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from .models import UserSession

class SingleDeviceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip middleware for unauthenticated users or specific paths (e.g., login, logout)
        if not request.user.is_authenticated or request.path in [reverse('login'), reverse('logout')]:
            return self.get_response(request)

        # Get the current session key
        current_session_key = request.session.session_key

        try:
            # Check if the user has an active session
            user_session = UserSession.objects.get(user=request.user)

            # If the current session key doesn't match the stored session key, log the user out
            if user_session.session_key != current_session_key:
                logout(request)
                return redirect('login')  # Redirect to login page
        except UserSession.DoesNotExist:
            # If no UserSession exists, this might be the first login; we'll handle it in the login view
            pass

        return self.get_response(request)