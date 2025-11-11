from django.urls import path
from . import views

urlpatterns = [
    path('messages/', views.message_view, name='message-send-or-list'),
    path('conversations/', views.conversation_list_view, name='conversation-list'),
    path('conversations/<uuid:conversation_id>/messages/', views.conversation_messages_view, name='conversation-messages'),
    path('faqs/', views.faq_list_view, name='faq-list'),
    path('feedback/', views.feedback_view, name='feedback-submit'),
    path('config/', views.chat_config_view, name='chat-config'),
]
