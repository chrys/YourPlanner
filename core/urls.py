from django.urls import path
from .views import home_view
from orders.views import select_items, basket

app_name = 'core'  # Define the namespace

urlpatterns = [
    path('', home_view, name='home'),
]
