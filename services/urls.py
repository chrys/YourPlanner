from django.urls import path
from .views import professional_account, service_items, edit_item, delete_service, delete_item

urlpatterns = [
    path('professional-account/', professional_account, name='professional-account'),
    path('service/<int:service_id>/items/', service_items, name='service-items'),
    path('item/<int:item_id>/edit/', edit_item, name='edit-item'),
    path('service/<int:service_id>/delete/', delete_service, name='delete-service'),
    path('item/<int:item_id>/delete/', delete_item, name='delete-item'),
]
