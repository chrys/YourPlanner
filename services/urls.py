from django.urls import path
from .views import professional_account, service_items, edit_item

urlpatterns = [
    path('professional-account/', professional_account, name='professional-account'),
    path('service/<int:service_id>/items/', service_items, name='service-items'),
    path('item/<int:item_id>/edit/', edit_item, name='edit-item'),

]