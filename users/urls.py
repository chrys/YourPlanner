from django.urls import path
from .views import register, user_management_view
from django.urls import include

urlpatterns = [
    path('register/', register, name='register'),
    path('management/', user_management_view, name='user_management'),
    path('accounts/', include('django.contrib.auth.urls')),
]