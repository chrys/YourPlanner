from django.urls import path, include
from .views import (
    UserRegistrationView,
    UserManagementView,
    UserProfileView,
    ChangeProfessionalView,
    CustomerTemplateListView,
    CustomerTemplateDetailView,
    CustomerProfessionalServicesView,
    DepositPaymentView
)
from .views_professional import (
    CustomerManagementView,
    CustomerDetailView,
    CustomerBasketView,
    CustomerLabelUpdateView
)

app_name = 'users' # Added for namespacing

urlpatterns = [
    # App-specific user views
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('management/', UserManagementView.as_view(), name='user_management'),
    path('profile/', UserProfileView.as_view(), name='profile'), # Changed path from accounts/profile/ to just profile/
    path('change-professional/', ChangeProfessionalView.as_view(), name='change_professional'),
    path('deposit-payment/', DepositPaymentView.as_view(), name='deposit_payment'),
    
    # Professional customer management views
    path('customers/', CustomerManagementView.as_view(), name='customer_management'),
    path('customers/<int:customer_id>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<int:customer_id>/labels/', CustomerLabelUpdateView.as_view(), name='customer_labels'),
    path('customers/basket/<int:order_id>/', CustomerBasketView.as_view(), name='customer_basket'),
    # Customer-facing template list
    path('customer-templates/', CustomerTemplateListView.as_view(), name='customer_template_list'),
    path('customer-templates/<int:pk>/', CustomerTemplateDetailView.as_view(), name='customer_template_detail'),
    path('my-professional-services/', CustomerProfessionalServicesView.as_view(), name='customer_professional_services'),

    
]


urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
