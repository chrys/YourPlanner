from django.urls import path
from .views import select_items, basket

urlpatterns = [
    path('select-items/', select_items, name='select-items'),
    path('basket/', basket, name='basket'),
]