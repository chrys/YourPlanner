from django.urls import path
from .views import home_view
from orders.views import select_items, basket

urlpatterns = [
    path('', home_view, name='home'),
]