"""
main urls file for the YourPlanner project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from users.views import SignupView  # CHANGED: Import SignupView

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
    # CHANGED: Uncommented core URLs to register the 'core:home' namespace for post-signup redirect
    path('', include('core.urls', namespace='core')),
    # CHANGED: Added signup landing page route - uses SignupView to provide form context
    path('signup/', SignupView.as_view(), name='landing_signup'),
    path('api/chatbot/', include('chatbot.api_urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
