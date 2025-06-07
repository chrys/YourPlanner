from django.urls import path
from . import views

app_name = 'template_app'

urlpatterns = [
    path('', views.template_list, name='template_list'),
    path('create/', views.template_create, name='template_create'),
    path('<slug:slug>/', views.template_detail, name='template_detail'),
    path('<slug:slug>/update/', views.template_update, name='template_update'),
    path('<slug:slug>/delete/', views.template_delete, name='template_delete'),
]

