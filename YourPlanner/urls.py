"""
main urls file for the YourPlanner project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from users.views import SignupView  # CHANGED: Import SignupView
from wagtail.admin import urls as wagtailadmin_urls  
from wagtail.documents import urls as wagtaildocs_urls 
from wagtail import urls as wagtail_urls  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('services/', include('services.urls')),
    path('orders/', include('orders.urls')),
    path('packages/', include('packages.urls', namespace='packages')),
    path('config/', include('configuration.urls', namespace='configuration')),
    # CHANGED: Added payments app URLs
    path('payments/', include('payments.urls', namespace='payments')),
    #path('accounts/', include('django.contrib.auth.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('signup/', SignupView.as_view(), name='landing_signup'),
    path('api/chatbot/', include('chatbot.api_urls')),
    path('cms/', include(wagtailadmin_urls)),  # Wagtail admin
    path('documents/', include(wagtaildocs_urls)),  # Wagtail documents
    path('pages/', include(wagtail_urls)),
    path('', include('core.urls', namespace='core')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
