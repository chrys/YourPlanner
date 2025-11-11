from django.contrib import admin
from .models import Conversation, Message, FAQ, ChatConfig

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'started_at']
    list_filter = ['status', 'started_at']
    search_fields = ['customer__email', 'customer__first_name']
    readonly_fields = ['id', 'started_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'text', 'timestamp']
    list_filter = ['sender', 'timestamp']
    search_fields = ['text', 'customer__email']
    readonly_fields = ['id', 'timestamp']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['question', 'answer']
    list_editable = ['is_active', 'order']
    ordering = ['order']


@admin.register(ChatConfig)
class ChatConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ('RAG API Configuration', {
            'fields': ('rag_api_url', 'rag_api_key', 'rag_api_timeout_seconds')
        }),
        ('Fallback & Polling', {
            'fields': ('fallback_message', 'polling_interval_ms')
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['updated_at']

    def has_add_permission(self, request):
        """Prevent adding more than one instance."""
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion."""
        return False
