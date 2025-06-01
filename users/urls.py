from django.urls import path, include
from .views import (
    UserRegistrationView,
    UserManagementView,
    UserProfileView,
    ChangeProfessionalView
)

app_name = 'users' # Added for namespacing

urlpatterns = [
    # App-specific user views
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('management/', UserManagementView.as_view(), name='user_management'),
    path('profile/', UserProfileView.as_view(), name='profile'), # Changed path from accounts/profile/ to just profile/
    path('change-professional/', ChangeProfessionalView.as_view(), name='change_professional'),

    # Django's built-in auth URLs (login, logout, password management)
    # These are typically not namespaced under 'users', so they are kept separate.
    # If you want them under /users/accounts/, you would adjust the path here,
    # but standard practice is often to have them at a higher level like /accounts/.
    # For this refactor, I'll keep them included as they were but outside the app_name's direct influence for now.
    # However, to make `users:profile` work if `django.contrib.auth.urls` defines its own `profile`,
    # it's better to have our app's profile URL distinct or ensure it's resolved first.
    # The path 'profile/' is now distinct from 'accounts/profile/'.

    # path('accounts/', include('django.contrib.auth.urls')), # Original line
    # To avoid potential conflicts and keep auth URLs grouped if desired:
    # path('auth/', include('django.contrib.auth.urls')), # Option 1: Prefix Django auth
]

# It's common to include Django's auth URLs at the project level urls.py.
# If they are intended to be part of the 'users' app namespace like '/users/accounts/',
# the include should be: path('accounts/', include('django.contrib.auth.urls'))
# For now, assuming the original structure where `django.contrib.auth.urls` are separate.
# The `profile` URL is now directly under the app, `users:profile`.
# If login redirects to `accounts/profile/` by default, Django's default will be used unless overridden.
# For this task, I will keep the include as it was, but it's a point of attention for project structure.
# The prompt implies refactoring *users* app views, so django.contrib.auth.urls are secondary.

# Re-adding django.contrib.auth.urls as they provide login, logout etc.
# The profile view is now `users:profile`. Default login redirect might need
# settings.LOGIN_REDIRECT_URL = reverse_lazy('users:profile') or 'users:user_management'
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]