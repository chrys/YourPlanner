# Data Model: VasiliasBot Chat System

**Date**: 2025-11-11 | **Feature**: Customer Chatbot MVP (VasiliasBot)

## Overview

The VasiliasBot data model consists of four Django models organized into the `chatbot` app:
- **Conversation**: Chat session for a customer
- **Message**: Individual message in a conversation
- **FAQ**: Frequently asked questions managed in Admin
- **ChatConfig**: Singleton configuration (RAG API endpoint, fallback message, polling interval)

Feedback is sent directly to the RAG API and not stored locally (MVP scope).

All models use UUID primary keys and timestamp tracking for auditability.

---

## Entity Definitions

### Conversation

Represents a chat session for a customer. Groups related messages into a single conversation.

```python
class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        'users.Customer',
        on_delete=models.CASCADE,
        related_name='chatbot_conversations'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('closed', 'Closed'),
        ],
        default='active'
    )
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['customer', '-started_at']),
        ]
    
    def __str__(self):
        return f"Conversation {self.id[:8]} - {self.customer} ({self.status})"
```

**Constraints:**
- `customer` is required (only authenticated customers).
- `started_at` is immutable (set on creation).
- `status` is one of: `active`, `closed`.
- `metadata` allows storing extra context (e.g., session tags, analytics data).

**Relationships:**
- One-to-many: A Conversation has many Messages.
- Foreign key: Links to `users.Customer` model.

**Lifecycle:**
- Created when customer opens chat for the first time.
- Status changes to `closed` when customer explicitly closes chat or session ends.
- Query index on `(customer, -started_at)` for efficient history retrieval.

---

### Message

Represents a single message in a conversation (customer or bot).

```python
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
        'users.Customer',
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
```

**Constraints:**
- `conversation`, `customer`, and `text` are required.
- `timestamp` is immutable (set on creation).
- `sender` is one of: `customer`, `bot`.
- `text` is immutable after creation (audit trail).

**Relationships:**
- Foreign key: Belongs to one Conversation and one Customer.

**Lifecycle:**
- Created on send (customer or bot).
- Immutable after creation (no edits).
- Deleted only if Conversation is deleted (cascade).

**Validation:**
- `text` must be non-empty.
- `sender` must be one of defined choices.

---

### FAQ

Frequently asked questions and answers, managed by admins. Serves as fallback knowledge base.

```python
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
```

**Constraints:**
- `question` and `answer` are required.
- `question` is unique (no duplicate FAQs).
- `order` determines display order in UI (default 0; sort ascending).
- `is_active` controls visibility (soft delete; admins disable instead of delete).

**Lifecycle:**
- Created/updated in Django Admin.
- Admins can activate/deactivate without deleting.
- `created_at` and `updated_at` track audit history.

**Use Cases:**
- CLI endpoint: `/api/chatbot/faqs/` returns list of active FAQs (sorted by order).
- Matching: Simple substring match on customer message; return FAQ if matched (before calling RAG API).

---

### ChatConfig

Singleton configuration model storing runtime settings (RAG API endpoint, fallback message, polling interval).

```python
class ChatConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rag_api_url = models.CharField(
        max_length=500,
        help_text="FastAPI endpoint for RAG application (e.g., https://rag.example.com/query)"
    )
    rag_api_key = models.CharField(
        max_length=255,
        help_text="API key for RAG application (encrypted in database)"
    )
    fallback_message = models.TextField(
        default="I'm sorry, I'm not sure how to help with that. Would you like to rephrase? If not, you can always send an email to your wedding planner."
    )
    polling_interval_ms = models.IntegerField(
        default=2500,
        help_text="AJAX polling interval in milliseconds (default 2500ms = 2.5 seconds)"
    )
    rag_api_timeout_seconds = models.IntegerField(
        default=10,
        help_text="Timeout for RAG API calls in seconds"
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Chat Configuration"
    
    def save(self, *args, **kwargs):
        """Enforce singleton pattern."""
        self.pk = 1  # Only one record allowed
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion."""
        pass
    
    @classmethod
    def load(cls):
        """Get or create the singleton configuration."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return "Chat Configuration (Singleton)"
```

**Constraints:**
- Singleton pattern: Only one record exists (pk=1).
- `rag_api_url` and `rag_api_key` are required.
- `rag_api_key` should be encrypted in database (use `django-environ` or similar).
- `polling_interval_ms` must be positive integer.
- `rag_api_timeout_seconds` must be positive integer.

**Use Cases:**
- Django view: Load via `ChatConfig.load()` to get current settings.
- Admin: Update RAG API endpoint or fallback message without code change.
- Client (Vue.js): Fetch polling interval from `/api/chatbot/config/` on widget init.

---

## Relationships & Constraints

### Entity Relationship Diagram (Conceptual)

```
Customer (users.Customer)
    |
    +--- Conversation (1:N)
            |
            +--- Message (1:N)
                    |
                    +--- Feedback (1:N, max 1 per customer)
    |
    +--- Message (1:N, denormalized for efficiency)
    |
    +--- Feedback (1:N, denormalized for efficiency)

FAQ (independent, referenced by business logic, not foreign keys)

ChatConfig (singleton, global settings)
```

### Unique Constraints

- **FAQ**: `question` — no duplicate questions.
- **ChatConfig**: `pk=1` — singleton enforced in model logic.

### Foreign Key Constraints

- **Conversation.customer** → `users.Customer` (CASCADE delete)
- **Message.conversation** → `Conversation` (CASCADE delete)
- **Message.customer** → `users.Customer` (CASCADE delete)

**Cascade implications:**
- Deleting a Customer deletes all their conversations and messages.
- Deleting a Conversation deletes all its messages.

### Indexes

To support efficient queries:

- **Conversation**: Index on `(customer, -started_at)` — retrieve customer's conversation history.
- **Message**: Index on `(conversation, timestamp)` and `(customer, timestamp)` — retrieve conversation messages; retrieve customer's messages.
- **FAQ**: Index on `(is_active, order)` — retrieve active FAQs in order.

---

## State Transitions

### Conversation States

```
[created] ---> active ---> closed
  |
  +-------> (deleted if cascade from customer)
```

- **active**: Conversation is ongoing; messages can be added.
- **closed**: Conversation ended; no new messages (enforced in view logic).
- Transition: Admin or automated task can close old conversations (>7 days inactive, Phase 2).

### Message Lifecycle

```
[created] ---> (immutable) ---> (deleted only if conversation deleted)
```

- Messages are immutable after creation (audit trail).
- Deletion happens only via cascade (conversation delete).

### Feedback Lifecycle

```
[created] ---> (optional: updated) ---> (deleted if message deleted)
```

- Created on customer action (thumbs up/down).
- Can be updated (customer changes mind, Phase 2).
- Deletion happens only via cascade (message delete).

### FAQ Lifecycle

```
[created] ---> active ---> (deactivated via is_active=False, or deleted)
```

- Admins create FAQs in Django Admin.
- Soft delete: Set `is_active=False` instead of deleting (preserves history).
- Hard delete allowed for cleanup (no cascade issues).

---

## Data Volume & Scale Assumptions (MVP)

| Entity | Estimated Volume | Growth | Notes |
|--------|------------------|--------|-------|
| Conversation | 100-500 / day | Linear | 1 conversation per customer per day (avg) |
| Message | 500-2500 / day | Linear | 5-10 messages per conversation |
| FAQ | 10-50 | Slow | 10-15 curated FAQs; grows gradually |
| ChatConfig | 1 | Static | Singleton; never grows |

**Storage estimates (MVP, 1 month):**
- Conversation: ~15KB each → ~150MB
- Message: ~200 bytes average → ~150MB
- FAQ: ~1KB average → ~50KB
- **Total: ~300MB** (well below SQLite/PostgreSQL limits)

**Query patterns (MVP):**
- Frequent: Fetch conversation history (index on `conversation, timestamp`)
- Frequent: Fetch active FAQs (index on `is_active, order`)

**No optimization needed for MVP**; Phase 2 can add caching (Redis) if needed.

---

## Migration Path

**Initial migration (`0001_initial.py`)** creates all models:
1. `Conversation`
2. `Message`
3. `FAQ`
4. `ChatConfig`

**Data migration (`0002_load_initial_config.py`)** creates the singleton `ChatConfig` record.

**Testing migration**: Ensure migrations work on both SQLite (dev) and PostgreSQL (prod).

---

## Admin Interface

### Conversation Admin

- List view: customer, status, started_at, message count (readonly count aggregate)
- Filter: by customer, status, started_at (date range)
- Search: customer email/name
- Readonly: id, started_at, created_at
- Editable: status, ended_at

### Message Admin

- List view: conversation, sender, text[:50], timestamp
- Filter: by sender, timestamp, conversation
- Search: text (full-text search, future Phase 2)
- Readonly: id, timestamp
- Editable: none (messages are immutable)

### FAQ Admin

- List view: question[:50], is_active, order
- Filter: by is_active
- Search: question, answer
- Editable: question, answer, order, is_active
- Actions: Bulk activate/deactivate

### ChatConfig Admin

- Singleton view (only one record).
- Editable: rag_api_url, rag_api_key, fallback_message, polling_interval_ms, rag_api_timeout_seconds.
- Help text: Guidance on each field (e.g., "Polling interval in milliseconds").
- Read-only: updated_at.

---

## Summary

The VasiliasBot data model is straightforward and scalable for MVP:
- **Four models**: Clear separation of concerns (conversations, messages, FAQs, config).
- **UUID primary keys**: Future-proof for distributed systems (Phase 2+).
- **Immutable messages**: Audit trail; prevents accidental edits.
- **Feedback to RAG API**: Direct forwarding; no local storage in MVP.
- **Singleton config**: Runtime tuning without code changes.
- **Indexes**: Optimized for key queries (conversation history, FAQ list).
- **Cascade deletes**: Automatic cleanup when customers deleted.
- **Admin interface**: Non-developer control of FAQs and settings.

Ready for implementation → Django models, serializers, views.

---

<!-- Changes: Phase 1 data model definition complete; all entities, relationships, and constraints documented. -->
