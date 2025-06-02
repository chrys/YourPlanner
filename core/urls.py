from django.urls import path
from .views import home_view
from orders.views import SelectItemsView, BasketView

app_name = 'core'  # Define the namespace

urlpatterns = [
    path('', home_view, name='home'),
]
