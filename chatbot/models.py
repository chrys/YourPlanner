import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class Conversation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chatbot_conversations'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['customer', '-started_at']),
        ]

    def __str__(self):
        return f"Conversation {self.id.hex[:8]} - {self.customer}"


class Message(models.Model):
    SENDER_CHOICES = [
        ('customer', 'Customer'),
        ('bot', 'Bot'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chatbot_messages'
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['customer', 'timestamp']),
        ]

    def __str__(self):
        return f"[{self.sender.upper()}] {self.text[:50]}... ({self.timestamp})"


class FAQ(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField(unique=True)
    answer = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self):
        return f"{self.question[:50]}..."


class ChatConfig(models.Model):
    """Singleton configuration for chatbot."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rag_api_url = models.CharField(
        max_length=500,
        help_text="FastAPI endpoint for RAG (e.g., https://rag.example.com/query)"
    )
    rag_api_key = models.CharField(
        max_length=255,
        help_text="API key for RAG (encrypted in database)"
    )
    fallback_message = models.TextField(
        default="I'm sorry, I'm not sure how to help with that. Would you like to rephrase? If not, you can always send an email to your wedding planner."
    )
    polling_interval_ms = models.IntegerField(
        default=2500,
        help_text="AJAX polling interval in milliseconds"
    )
    rag_api_timeout_seconds = models.IntegerField(
        default=10,
        help_text="Timeout for RAG API calls in seconds"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Chat Configuration"

    def save(self, *args, **kwargs):
        """Enforce singleton."""
        if not self.pk and ChatConfig.objects.exists():
            # if you'll not check for self.pk
            # then error will also raised in update of exists model
            raise ValidationError('There is can be only one DropboxSettings instance')
        super(ChatConfig, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion."""
        pass

    @classmethod
    def load(cls):
        """Get or create singleton."""
        obj, created = cls.objects.get_or_create()
        return obj

    def __str__(self):
        return "Chat Configuration (Singleton)"
