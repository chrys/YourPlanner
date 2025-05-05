# Defines the URL pattern for the homepage 

from django.urls import path
from .views import home_view

urlpatterns = [
    path('', home_view, name='home'),
]