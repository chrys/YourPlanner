from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    path('', views.TemplateListView.as_view(), name='template-list'),
    path('create/', views.TemplateCreateView.as_view(), name='template-create'),
    path('<int:pk>/', views.TemplateDetailView.as_view(), name='template-detail'),
    path('<int:pk>/update/', views.TemplateUpdateView.as_view(), name='template-update'),
    path('<int:pk>/delete/', views.TemplateDeleteView.as_view(), name='template-delete'),
    # CHANGED: Added packages view URL
    path('packages/', views.PackagesView.as_view(), name='packages'),
    # CHANGED: Added URL for adding package to order
    path('packages/add-to-order/', views.AddPackageToOrderView.as_view(), name='add_package_to_order'),
]
