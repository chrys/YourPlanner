from django.urls import path
from .views import register, user_management_view, change_professional
from django.urls import include

from .views import profile_view

urlpatterns = [
    path('register/', register, name='register'),
    path('management/', user_management_view, name='user_management'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', profile_view, name='profile'),
    path('change-professional/', change_professional, name='change_professional'),

]