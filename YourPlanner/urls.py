"""
main urls file for the YourPlanner project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('services/', include('services.urls')),
    path('orders/', include('orders.urls')),
    path('templates/', include('templates.urls', namespace='templates')), 
    path('config/', include('configuration.urls', namespace='configuration')),
    #path('accounts/', include('django.contrib.auth.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('', include('core.urls', namespace='core')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
