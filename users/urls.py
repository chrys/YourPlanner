from django.urls import path, include
from django.contrib.auth import views as auth_views 
from .views import (
    CustomLoginView,  # CHANGED: Import custom login view
    UserRegistrationView,
    SignupView,  # CHANGED: Added SignupView for landing page
    UserManagementView,
    UserProfileView,
    ChangeProfessionalView,
    CustomerTemplateListView,
    CustomerTemplateDetailView,
    CustomerProfessionalServicesView,
    DepositPaymentView,
    AgentManagementView,  # Added Agent views
    AgentCreateOrderView,
    AgentOrderDetailView,  # Removed AgentSelectCustomerView (no longer needed)
    AgentDeleteOrderView,
    WeddingTimelineDetailView,  # CHANGED: Added WeddingTimeline views
    WeddingTimelineUpdateView,
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
    
    # Agent management routes
    path('agent/dashboard/', AgentManagementView.as_view(), name='agent_management'),
    path('agent/order/create/', AgentCreateOrderView.as_view(), name='agent_create_order'),  # Removed select-customer route (no longer needed)
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
    # CHANGED: Added Wedding Timeline routes
    path('wedding-timeline/', WeddingTimelineDetailView.as_view(), name='wedding_timeline'),
    path('wedding-timeline/update/', WeddingTimelineUpdateView.as_view(), name='wedding_timeline_update'),

    # Auth views
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    
]


