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
from .views_agent import (
    AgentCreateOrderView,
    AgentSelectServicesView,
    AgentFinalizeOrderView,
    AgentEditOrderView
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

    # Agent views
    path('agent/create-order/', AgentCreateOrderView.as_view(), name='agent_create_order'),
    path('agent/select-services/', AgentSelectServicesView.as_view(), name='agent_select_services'),
    path('agent/finalize-order/', AgentFinalizeOrderView.as_view(), name='agent_finalize_order'),
    path('agent/edit-order/<int:pk>/', AgentEditOrderView.as_view(), name='agent_edit_order'),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
