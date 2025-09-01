from django.urls import path
from .views import (
    users_list, manage_user_modules, update_user_modules,
    user_login, user_logout, two_factorauth, verify_2fa, home, resend_otp,
    manage_group_permissions, group_list, setting, two_factor_setup,
    create_user, edit_user, toggle_user_status, delete_user,
    reset_password_set,  # Added missing import
    reset_password_verify,  # Added missing import
    forgot_password  # Added missing import
)
from django.urls import path

urlpatterns = [
    path("", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("2fa/setup/", two_factorauth, name="two_factor_auth"),
    path("2fa/verify/", verify_2fa, name="verify_2fa"),
    path('dashboard',home, name='dashboard'),
    path('2fa/resend/', resend_otp, name='resend_otp'),
    path('setting/', setting, name='setting'),
    path("2fa/onboard/", two_factor_setup, name="two_factor_setup"),
    path('groups/', group_list, name='group_list'),
    path('groups/<int:group_id>/permissions/', manage_group_permissions, name='manage_group_permissions'),


    path('users_list/', users_list, name='user_list'),
    path('users/<int:user_id>/modules/', manage_user_modules, name='manage_user_modules'),
    path('users/<int:user_id>/modules/update/', update_user_modules, name='update_user_modules'),
    #path("user/", user_list, name="user_list"),
    path("create/user", create_user, name="create_user"),
    path("<int:user_id>/edit/", edit_user, name="edit_user"),
    path("<int:user_id>/toggle/", toggle_user_status, name="toggle_user_status"),
    path("<int:user_id>/delete/", delete_user, name="delete_user"),
    #path("users/<int:user_id>/toggle-block/", views.toggle_user_block, name="toggle_user_block"),
    # Removed duplicate entries using 'views.' which is not defined
    path("forgot-password/", forgot_password, name="forgot_password"),
    path("reset-password/verify/", reset_password_verify, name="reset_password_verify"),
    path("reset-password/set/", reset_password_set, name="reset_password_set"),
    
]
