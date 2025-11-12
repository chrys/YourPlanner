from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

# CHANGED: Added InvoiceView for displaying invoicing and payments
class InvoiceView(TemplateView):
    """
    View to display invoicing and payments.
    """
    template_name = 'payments/invoice.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Invoicing & Payments"
        return context
