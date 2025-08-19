# your_app/context_processors.py
from .models import UserModuleAccess

def user_modules(request):
    if request.user.is_authenticated:
        # Fetch the module names the user has access to
        allowed_modules = UserModuleAccess.objects.filter(user=request.user).values_list('module__name', flat=True)
        return {'allowed_modules': allowed_modules}
    return {'allowed_modules': []}  # Return empty list if user is not authenticated