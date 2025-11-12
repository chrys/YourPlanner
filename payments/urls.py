from django.urls import path
from .views import InvoiceView

app_name = 'payments'

urlpatterns = [
    # CHANGED: Added invoice/payments route
    path('invoice/', InvoiceView.as_view(), name='invoice'),
]
