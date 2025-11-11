# Quickstart: VasiliasBot MVP Development

**Date**: 2025-11-11 | **Feature**: Customer Chatbot MVP (VasiliasBot)

## Overview

This quickstart guide walks through the end-to-end implementation of VasiliasBot (Customer Chatbot MVP) for the YourPlanner Django project. Follow these steps in order to build, test, and integrate the chatbot.

---

## Prerequisites

- Django 5.1.12, Python 3.13.9
- SQLite3 (dev) or PostgreSQL (prod)
- Vue.js 3
- Django REST Framework (DRF)
- Playwright (for UI testing)
- Virtual environment active: `source venv/bin/activate`

---

## Phase 1: Django App Setup

### Step 1.1: Create the `chatbot` App

```bash
cd /Users/chrys/Projects/YourPlanner
python manage.py startapp chatbot
```

**Expected output**:
```
YourPlanner/chatbot/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
├── models.py
├── tests.py
├── views.py
```

### Step 1.2: Add App to INSTALLED_APPS

**File**: `YourPlanner/settings.py`

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'rest_framework',
    'chatbot',  # Add this
]
```

### Step 1.3: Configure DRF Settings

**File**: `YourPlanner/settings.py` (add if not present)

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

---

## Phase 2: Data Model Implementation

### Step 2.1: Define Models

**File**: `chatbot/models.py`

```python
import uuid
from django.db import models
from django.contrib.auth import get_user_model

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
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion."""
        pass
    
    @classmethod
    def load(cls):
        """Get or create singleton."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return "Chat Configuration (Singleton)"
```

### Step 2.2: Create Migrations

```bash
python manage.py makemigrations chatbot
python manage.py migrate chatbot
```

### Step 2.3: Create Data Migration for ChatConfig

```bash
python manage.py makemigrations chatbot --empty --name load_initial_config
```

**File**: `chatbot/migrations/0002_load_initial_config.py`

```python
from django.db import migrations

def load_config(apps, schema_editor):
    ChatConfig = apps.get_model('chatbot', 'ChatConfig')
    ChatConfig.objects.get_or_create(pk=1)

class Migration(migrations.Migration):
    dependencies = [
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_config),
    ]
```

```bash
python manage.py migrate chatbot
```

---

## Phase 3: API Views & Serializers

### Step 3.1: Create Serializers

**File**: `chatbot/serializers.py`

```python
from rest_framework import serializers
from .models import Conversation, Message, FAQ

class ConversationSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'status', 'started_at', 'ended_at', 'message_count']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class MessageSerializer(serializers.ModelSerializer):
    faq_matched = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'text', 'timestamp', 'faq_matched']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'order']


class ChatConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatConfig
        fields = ['polling_interval_ms', 'fallback_message']
```

### Step 3.2: Create Views

**File**: `chatbot/views.py`

```python
import requests
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from .models import Conversation, Message, FAQ, ChatConfig
from .serializers import (
    ConversationSerializer, MessageSerializer,
    FAQSerializer, ChatConfigSerializer
)


@api_view(['GET'])
def faq_list_view(request):
    """Fetch active FAQs."""
    faqs = FAQ.objects.filter(is_active=True).order_by('order')
    serializer = FAQSerializer(faqs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def chat_config_view(request):
    """Fetch client configuration."""
    config = ChatConfig.load()
    serializer = ChatConfigSerializer(config)
    return Response(serializer.data)


@api_view(['GET'])
def conversation_list_view(request):
    """Fetch customer's conversations."""
    status_filter = request.query_params.get('status', 'active')
    limit = int(request.query_params.get('limit', 10))
    
    conversations = Conversation.objects.filter(
        customer=request.user,
        status=status_filter
    ).order_by('-started_at')[:limit]
    
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data)


@api_view(['POST', 'GET'])
def message_view(request):
    """Send message or fetch message history."""
    if request.method == 'POST':
        conversation_id = request.data.get('conversation_id')
        text = request.data.get('text', '').strip()
        
        if not text:
            return Response(
                {'error': 'Text must not be empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create conversation
        if conversation_id:
            conversation = get_object_or_404(
                Conversation,
                id=conversation_id,
                customer=request.user
            )
        else:
            conversation = Conversation.objects.create(customer=request.user)
        
        # Store customer message
        customer_message = Message.objects.create(
            conversation=conversation,
            customer=request.user,
            text=text,
            sender='customer'
        )
        
        # Check FAQ match (simple substring match for MVP)
        faq_match = FAQ.objects.filter(
            is_active=True,
            question__icontains=text
        ).first()
        
        bot_text = faq_match.answer if faq_match else ChatConfig.load().fallback_message
        
        # If no FAQ match, call RAG API (Phase 1 MVP: skip for now)
        if not faq_match:
            # TODO: Integrate RAG API in Phase 1.5
            pass
        
        # Store bot message
        bot_message = Message.objects.create(
            conversation=conversation,
            customer=request.user,
            text=bot_text,
            sender='bot'
        )
        
        # Annotate faq_matched for response
        bot_message.faq_matched = bool(faq_match)
        
        serializer = MessageSerializer(bot_message)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def conversation_messages_view(request, conversation_id):
    """Fetch messages in a conversation."""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        customer=request.user
    )
    
    limit = int(request.query_params.get('limit', 50))
    offset = int(request.query_params.get('offset', 0))
    
    messages = conversation.messages.all()[offset:offset+limit]
    
    serializer = MessageSerializer(messages, many=True)
    return Response({
        'count': conversation.messages.count(),
        'results': serializer.data
    })


@api_view(['POST'])
def feedback_view(request):
    """Submit feedback on a message. Forward to RAG API."""
    message_id = request.data.get('message_id')
    value = request.data.get('value')
    
    if value not in ['up', 'down']:
        return Response(
            {'error': "Value must be 'up' or 'down'."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    message = get_object_or_404(
        Message,
        id=message_id,
        conversation__customer=request.user
    )
    
    # Prepare feedback payload for RAG API
    config = ChatConfig.load()
    feedback_payload = {
        'message_id': str(message.id),
        'conversation_id': str(message.conversation.id),
        'customer_id': str(request.user.id),
        'value': value,
        'timestamp': message.timestamp.isoformat()
    }
    
    try:
        # Forward to RAG API
        rag_response = requests.post(
            f"{config.rag_api_url}/feedback",
            json=feedback_payload,
            headers={'Authorization': f'Bearer {config.rag_api_key}'},
            timeout=config.rag_api_timeout_seconds
        )
        
        if rag_response.status_code >= 200 and rag_response.status_code < 300:
            return Response({'success': True, 'message': 'Feedback submitted to RAG API'})
        else:
            return Response(
                {'error': 'Failed to submit feedback to RAG API'},
                status=status.HTTP_502_BAD_GATEWAY
            )
    except requests.RequestException as e:
        return Response(
            {'error': f'RAG API error: {str(e)}'},
            status=status.HTTP_502_BAD_GATEWAY
        )
```

### Step 3.3: Create API URLs

**File**: `chatbot/api_urls.py`

```python
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
```

### Step 3.4: Include API URLs in Main Project

**File**: `YourPlanner/urls.py`

```python
from django.urls import path, include

urlpatterns = [
    # ... existing patterns ...
    path('api/chatbot/', include('chatbot.api_urls')),
]
```

---

## Phase 4: Django Admin Setup

### Step 4.1: Register Models in Admin

**File**: `chatbot/admin.py`

```python
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
```

---

## Phase 5: Vue.js Widget Integration

### Step 5.1: Create Vue.js Component

**File**: `core/static/core/js/VasiliasBot.vue`

```vue
<template>
  <div class="vasbot-container">
    <!-- Widget Icon (Closed) -->
    <button
      v-if="!isOpen"
      class="vasbot-icon"
      @click="toggleWidget"
      aria-label="Open chat"
    >
      💬
    </button>

    <!-- Chat Window (Open) -->
    <div v-if="isOpen" class="vasbot-window">
      <div class="vasbot-header">
        <h3>VasiliasBot</h3>
        <button @click="toggleWidget" aria-label="Close chat">✕</button>
      </div>

      <!-- Messages -->
      <div class="vasbot-messages">
        <div
          v-for="message in messages"
          :key="message.id"
          :class="['vasbot-message', `vasbot-${message.sender}`]"
        >
          <p>{{ message.text }}</p>
          
          <!-- Feedback (bot messages only) -->
          <div v-if="message.sender === 'bot'" class="vasbot-feedback">
            <button
              @click="submitFeedback(message.id, 'up')"
              :class="{ active: message.feedback?.value === 'up' }"
            >
              👍
            </button>
            <button
              @click="submitFeedback(message.id, 'down')"
              :class="{ active: message.feedback?.value === 'down' }"
            >
              👎
            </button>
          </div>
        </div>

        <!-- Typing Indicator -->
        <div v-if="isLoading" class="vasbot-typing">
          <span>•</span><span>•</span><span>•</span>
        </div>
      </div>

      <!-- FAQ List (if no conversation yet) -->
      <div v-if="messages.length === 0" class="vasbot-faqs">
        <p>Popular questions:</p>
        <button
          v-for="faq in faqs"
          :key="faq.id"
          @click="sendMessage(faq.question)"
          class="vasbot-faq-btn"
        >
          {{ faq.question }}
        </button>
      </div>

      <!-- Input -->
      <div class="vasbot-input">
        <input
          v-model="inputText"
          @keyup.enter="sendMessage(inputText)"
          placeholder="Ask me anything..."
          :disabled="isLoading"
        />
        <button @click="sendMessage(inputText)" :disabled="!inputText || isLoading">
          Send
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const isOpen = ref(false);
const isLoading = ref(false);
const inputText = ref('');
const messages = ref([]);
const faqs = ref([]);
const currentConversationId = ref(null);
const pollingInterval = ref(2500);
let pollTimer = null;

const apiBaseUrl = '/api/chatbot';

// Toggle widget
function toggleWidget() {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    initializeWidget();
  } else {
    stopPolling();
  }
}

// Initialize widget on open
async function initializeWidget() {
  try {
    // Fetch config
    const configRes = await fetch(`${apiBaseUrl}/config/`);
    const config = await configRes.json();
    pollingInterval.value = config.polling_interval_ms;

    // Fetch active conversations
    const convsRes = await fetch(`${apiBaseUrl}/conversations/?status=active&limit=1`);
    const conversations = await convsRes.json();
    
    if (conversations.length > 0) {
      currentConversationId.value = conversations[0].id;
      await loadMessages();
      startPolling();
    }

    // Fetch FAQs
    const faqsRes = await fetch(`${apiBaseUrl}/faqs/`);
    faqs.value = await faqsRes.json();
  } catch (error) {
    console.error('Failed to initialize widget:', error);
  }
}

// Load messages for current conversation
async function loadMessages() {
  if (!currentConversationId.value) return;

  try {
    const res = await fetch(
      `${apiBaseUrl}/conversations/${currentConversationId.value}/messages/?limit=50`
    );
    const data = await res.json();
    messages.value = data.results;
  } catch (error) {
    console.error('Failed to load messages:', error);
  }
}

// Send message
async function sendMessage(text) {
  if (!text.trim()) return;

  inputText.value = '';
  isLoading.value = true;

  try {
    const res = await fetch(`${apiBaseUrl}/messages/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conversation_id: currentConversationId.value || null,
        text: text.trim()
      })
    });

    const botMessage = await res.json();
    
    // Add user message
    messages.value.push({
      id: `local-${Date.now()}`,
      sender: 'customer',
      text: text,
      timestamp: new Date().toISOString(),
      feedback: null
    });

    // Add bot message
    messages.value.push(botMessage);
    currentConversationId.value = botMessage.conversation_id;

    // Scroll to bottom
    setTimeout(() => {
      const messagesEl = document.querySelector('.vasbot-messages');
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }, 100);

  } catch (error) {
    console.error('Failed to send message:', error);
  } finally {
    isLoading.value = false;
  }
}

// Submit feedback
async function submitFeedback(messageId, value) {
  try {
    const res = await fetch(`${apiBaseUrl}/feedback/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message_id: messageId, value })
    });

    const feedback = await res.json();
    
    // Update message feedback
    const message = messages.value.find(m => m.id === messageId);
    if (message) {
      message.feedback = feedback;
    }
  } catch (error) {
    console.error('Failed to submit feedback:', error);
  }
}

// Polling
function startPolling() {
  pollTimer = setInterval(loadMessages, pollingInterval.value);
}

function stopPolling() {
  if (pollTimer) clearInterval(pollTimer);
}

onUnmounted(() => {
  stopPolling();
});
</script>

<style scoped>
.vasbot-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  z-index: 9999;
}

.vasbot-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.2s;
}

.vasbot-icon:hover {
  transform: scale(1.1);
}

.vasbot-window {
  width: 350px;
  height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 5px 40px rgba(0, 0, 0, 0.16);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.vasbot-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.vasbot-header h3 {
  margin: 0;
  font-size: 18px;
}

.vasbot-header button {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
}

.vasbot-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.vasbot-message {
  display: flex;
  flex-direction: column;
  max-width: 80%;
}

.vasbot-customer {
  align-self: flex-end;
}

.vasbot-customer p {
  background: #667eea;
  color: white;
  border-radius: 12px 12px 0 12px;
  padding: 10px 12px;
  margin: 0;
}

.vasbot-bot p {
  background: #f0f0f0;
  color: #333;
  border-radius: 12px 12px 12px 0;
  padding: 10px 12px;
  margin: 0;
}

.vasbot-feedback {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.vasbot-feedback button {
  background: #f0f0f0;
  border: 1px solid #ddd;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.vasbot-feedback button.active {
  background: #667eea;
  color: white;
}

.vasbot-typing {
  display: flex;
  gap: 4px;
  color: #999;
  font-size: 18px;
  margin-top: 8px;
}

.vasbot-typing span {
  animation: bounce 1.4s infinite;
}

.vasbot-typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.vasbot-typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 80%, 100% { opacity: 0.3; }
  40% { opacity: 1; }
}

.vasbot-faqs {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.vasbot-faqs p {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #999;
}

.vasbot-faq-btn {
  background: #f0f0f0;
  border: 1px solid #ddd;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  font-size: 13px;
  transition: background 0.2s;
}

.vasbot-faq-btn:hover {
  background: #e0e0e0;
}

.vasbot-input {
  padding: 12px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 8px;
}

.vasbot-input input {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 13px;
}

.vasbot-input button {
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 13px;
}

.vasbot-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
```

### Step 5.2: Include Widget in Base Template

**File**: `core/templates/core/base.html` (add before closing `</body>`)

```html
<!-- VasiliasBot Chatbot Widget -->
<div id="vasbot-app"></div>

<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
<script>
  // Import and mount VasiliasBot component (simplified inline for quickstart)
  const { createApp } = Vue;
  
  // Load component (in production, use bundled Vue components)
  // For now, include inline Vue SFC or load from separate file
  // See Phase 5.1 VasiliasBot.vue file above
</script>
```

---

## Phase 6: Testing

### Step 6.1: Unit Tests

**File**: `chatbot/tests/test_models.py`

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from chatbot.models import Conversation, Message, FAQ, Feedback

User = get_user_model()

class ConversationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='pass')
    
    def test_create_conversation(self):
        conv = Conversation.objects.create(customer=self.user)
        self.assertEqual(conv.status, 'active')
        self.assertIsNotNone(conv.id)


class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='pass')
        self.conv = Conversation.objects.create(customer=self.user)
    
    def test_create_message(self):
        msg = Message.objects.create(
            conversation=self.conv,
            customer=self.user,
            text='Hello',
            sender='customer'
        )
        self.assertEqual(msg.text, 'Hello')
        self.assertEqual(msg.sender, 'customer')
```

### Step 6.2: API Tests

**File**: `chatbot/tests/test_views.py`

```python
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from chatbot.models import Conversation, Message, FAQ

User = get_user_model()

class ChatbotAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='pass')
        self.client.force_authenticate(user=self.user)
        
        self.faq = FAQ.objects.create(
            question="What's the duration?",
            answer="30-45 minutes.",
            is_active=True
        )
    
    def test_send_message(self):
        response = self.client.post('/api/chatbot/messages/', {
            'text': 'What\'s the duration?'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['faq_matched'])
    
    def test_get_faqs(self):
        response = self.client.get('/api/chatbot/faqs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
```

### Step 6.3: Run Tests

```bash
python manage.py test chatbot
```

---

## Summary

You've now implemented the VasiliasBot MVP with:

1. ✅ Django models (Conversation, Message, Feedback, FAQ, ChatConfig)
2. ✅ REST API endpoints (send message, get FAQs, get history, submit feedback)
3. ✅ Django admin interface
4. ✅ Vue.js widget for customer UI
5. ✅ AJAX polling for real-time chat
6. ✅ Basic tests

**Next steps** (Phase 2):
- Integrate RAG API in Django view (replace TODO in message_view)
- Add advanced UI features (file upload, rich text)
- Implement WebSocket support (Django Channels)
- Add admin analytics dashboard

---

<!-- Changes: Quickstart guide for VasiliasBot MVP implementation, covering Django setup, models, API, admin, Vue.js widget, and tests. -->
