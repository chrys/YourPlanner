from django.urls import path
from .views import home_view
from orders.views import SelectItemsView, BasketView

urlpatterns = [
    path('', home_view, name='home'),
]