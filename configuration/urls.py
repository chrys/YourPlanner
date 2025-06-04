from django.urls import path
from . import views

app_name = 'configuration'

urlpatterns = [
    path('', views.configuration_index, name='index'),
    path('labels/<str:label_type>/', views.manage_labels, name='manage_labels'),
    path('labels/edit/<int:label_id>/', views.edit_label, name='edit_label'),
    path('labels/delete/<int:label_id>/', views.delete_label, name='delete_label'),
]
