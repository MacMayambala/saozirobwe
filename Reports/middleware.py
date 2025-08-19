from django.utils.timezone import now
from Reports.models import UserActivity
from django.contrib.auth.models import AnonymousUser

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Ignore requests for static files, media, and admin panel
        ignored_paths = ["/assets/", "/static/", "/media/", "/admin/"]
        if any(path in request.path for path in ignored_paths):
            return response

        if request.user.is_authenticated:
            UserActivity.objects.create(
                user=request.user,
                action=f"Visited {request.path}",
                url=request.path,
                method=request.method,
                ip_address=request.META.get("REMOTE_ADDR"),
                timestamp=now(),
            )
        return response
