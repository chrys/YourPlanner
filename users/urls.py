from django.urls import path, include
from django.contrib.auth import views as auth_views 
from .views import (
    UserRegistrationView,
    UserManagementView,
    UserProfileView,
    ChangeProfessionalView,
    CustomerTemplateListView,
    CustomerTemplateDetailView,
    CustomerProfessionalServicesView,
    DepositPaymentView,
    AgentManagementView,  # CHANGE: Added Agent views
    AgentCreateOrderView,
    AgentOrderDetailView,  # CHANGE: Removed AgentSelectCustomerView (no longer needed)
    AgentDeleteOrderView,
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
    
    # CHANGE: Agent management routes
    path('agent/dashboard/', AgentManagementView.as_view(), name='agent_management'),
    path('agent/order/create/', AgentCreateOrderView.as_view(), name='agent_create_order'),  # CHANGE: Removed select-customer route (no longer needed)
    path('agent/order/<int:order_pk>/', AgentOrderDetailView.as_view(), name='agent_order_detail'),
    path('agent/order/<int:order_pk>/delete/', AgentDeleteOrderView.as_view(), name='agent_order_delete'),
    
    # Professional customer management views
    path('customers/', CustomerManagementView.as_view(), name='customer_management'),
    path('customers/<int:customer_id>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<int:customer_id>/labels/', CustomerLabelUpdateView.as_view(), name='customer_labels'),
    path('customers/basket/<int:order_id>/', CustomerBasketView.as_view(), name='customer_basket'),
    # Customer-facing template list
    path('customer-templates/', CustomerTemplateListView.as_view(), name='customer_template_list'),
    path('customer-templates/<int:pk>/', CustomerTemplateDetailView.as_view(), name='customer_template_detail'),
    path('my-professional-services/', CustomerProfessionalServicesView.as_view(), name='customer_professional_services'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),  # CHANGE: Explicit password change URL
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),  # CHANGE: Done page after password change

    
]



