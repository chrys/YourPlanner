from django.urls import path
from . import views

app_name = 'templates'

urlpatterns = [
    path('', views.TemplateListView.as_view(), name='template-list'),
    path('create/', views.TemplateCreateView.as_view(), name='template-create'),
    path('<int:pk>/', views.TemplateDetailView.as_view(), name='template-detail'),
    path('<int:pk>/update/', views.TemplateUpdateView.as_view(), name='template-update'),
    # Add other paths like delete if needed later
]
