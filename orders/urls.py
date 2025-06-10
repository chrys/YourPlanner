from django.urls import path
from .views import (
    OrderCreateView, OrderListView, OrderDetailView, OrderStatusUpdateView, OrderCancelView,
    OrderItemCreateView, OrderItemUpdateView, OrderItemDeleteView,
    SelectItemsView, BasketView, AgentOrdersApiView, AgentDeleteOrderApiView
)

app_name = 'orders'

urlpatterns = [
    # Order URLs
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('', OrderListView.as_view(), name='order_list'), # List can be at the app root
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/update-status/', OrderStatusUpdateView.as_view(), name='order_status_update'),
    path('<int:pk>/cancel/', OrderCancelView.as_view(), name='order_cancel'),

    # OrderItem URLs (actions on a specific order)
    # 'order_pk' is used in the URL to identify the parent order for item operations
    path('<int:order_pk>/item/add/', OrderItemCreateView.as_view(), name='orderitem_create'),
    # 'item_pk' identifies the specific OrderItem to update or delete
    path('<int:order_pk>/item/<int:item_pk>/update/', OrderItemUpdateView.as_view(), name='orderitem_update'),
    path('<int:order_pk>/item/<int:item_pk>/delete/', OrderItemDeleteView.as_view(), name='orderitem_delete'),

    # Other Order related URLs
    path('<int:order_pk>/select-items/', SelectItemsView.as_view(), name='select_items'),
    path('basket/', BasketView.as_view(), name='basket'),

    # API URLs
    path('api/agent/orders/', AgentOrdersApiView.as_view(), name='agent_orders_api'),
    path('api/agent/order/<int:order_id>/delete/', AgentDeleteOrderApiView.as_view(), name='agent_delete_order_api'),
]