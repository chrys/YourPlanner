from django.urls import path
from . import views

app_name = 'configuration'

urlpatterns = [
    path('', views.ConfigurationDashboardView.as_view(), name='dashboard'),
    path('labels/', views.ConfigurationLabelListView.as_view(), name='label_list'),
    path('labels/<str:category>/', views.ConfigurationLabelListView.as_view(), name='label_list_by_category'),
    path('labels/create/', views.ConfigurationLabelCreateView.as_view(), name='label_create'),
    path('labels/create/<str:category>/', views.ConfigurationLabelCreateView.as_view(), name='label_create_for_category'),
    path('labels/<int:pk>/update/', views.ConfigurationLabelUpdateView.as_view(), name='label_update'),
    path('labels/<int:pk>/delete/', views.ConfigurationLabelDeleteView.as_view(), name='label_delete'),
]

