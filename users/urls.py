from django.urls import path
from .views import user_list, manage_user_modules, update_user_modules
from django.urls import path

from .views import user_login, user_logout, two_factorauth, verify_2fa,home,resend_otp,manage_group_permissions, group_list,setting,two_factor_setup

urlpatterns = [
    path("", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("2fa/setup/", two_factorauth, name="two_factor_auth"),
    path("2fa/verify/", verify_2fa, name="verify_2fa"),
    path('dashboard',home, name='dashboard'),
    path('2fa/resend/', resend_otp, name='resend_otp'),
    path('setting/', setting, name='setting'),
    path("2fa/onboard/", two_factor_setup, name="two_factor_setup"),

    path('users/', user_list, name='user_list'),
    path('users/<int:user_id>/modules/', manage_user_modules, name='manage_user_modules'),
    path('users/<int:user_id>/modules/update/', update_user_modules, name='update_user_modules'),
    path('groups/', group_list, name='group_list'),
    path('manage-permissions/<int:group_id>/', manage_group_permissions, name='manage_group_permissions'),
    
]
