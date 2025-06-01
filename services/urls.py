from django.urls import path
from .views import (
    ServiceCreateView, ServiceListView, ServiceDetailView, ServiceUpdateView, ServiceDeleteView,
    ItemCreateView, ItemListView, ItemDetailView, ItemUpdateView, ItemDeleteView, # ItemListView might be optional if only shown in service_detail
    PriceCreateView, PriceListView, PriceDetailView, PriceUpdateView, PriceDeleteView, # PriceListView might be optional
)

app_name = 'services'

urlpatterns = [
    # Service URLs
    path('services/', ServiceListView.as_view(), name='service_list'), # Was professional-account
    path('service/create/', ServiceCreateView.as_view(), name='service_create'),
    path('service/<int:pk>/', ServiceDetailView.as_view(), name='service_detail'),
    path('service/<int:pk>/update/', ServiceUpdateView.as_view(), name='service_update'),
    path('service/<int:pk>/delete/', ServiceDeleteView.as_view(), name='service_delete'),

    # Item URLs (nested under services)
    # service_pk is used by the UserOwnsParentServiceMixin to fetch the parent service
    path('service/<int:service_pk>/item/create/', ItemCreateView.as_view(), name='item_create'),
    # Optional: Standalone Item List View (if not just part of service_detail)
    path('service/<int:service_pk>/items/', ItemListView.as_view(), name='item_list'),
    path('service/<int:service_pk>/item/<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('service/<int:service_pk>/item/<int:pk>/update/', ItemUpdateView.as_view(), name='item_update'),
    path('service/<int:service_pk>/item/<int:pk>/delete/', ItemDeleteView.as_view(), name='item_delete'),

    # Price URLs (nested under items)
    # service_pk and item_pk are used by UserOwnsGrandparentServiceViaItemMixin
    path('service/<int:service_pk>/item/<int:item_pk>/price/create/', PriceCreateView.as_view(), name='price_create'),
    # Optional: Standalone Price List View (if not just part of item_detail)
    path('service/<int:service_pk>/item/<int:item_pk>/prices/', PriceListView.as_view(), name='price_list'),
    path('service/<int:service_pk>/item/<int:item_pk>/price/<int:pk>/', PriceDetailView.as_view(), name='price_detail'),
    path('service/<int:service_pk>/item/<int:item_pk>/price/<int:pk>/update/', PriceUpdateView.as_view(), name='price_update'),
    path('service/<int:service_pk>/item/<int:item_pk>/price/<int:pk>/delete/', PriceDeleteView.as_view(), name='price_delete'),
]
