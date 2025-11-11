# API Contracts: VasiliasBot Chat Endpoints

**Date**: 2025-11-11 | **Feature**: Customer Chatbot MVP (VasiliasBot)

## Overview

VasiliasBot communication flows through RESTful JSON endpoints served by Django. The client (Vue.js widget) uses AJAX polling to fetch messages and submit interactions. All endpoints require authentication (signed-in Customer).

---

## Base URL

```
/api/chatbot/
```

**Authentication**: Django session-based (Cookie authentication) or Token authentication (future Phase 2).

**Content-Type**: `application/json`

**Status Codes**:
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not authorized for this customer's data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error (logged)

---

## Endpoints

### 1. Send Message

**Endpoint**: `POST /api/chatbot/messages/`

**Purpose**: Customer sends a message or bot replies with a response (internal only).

**Request Body**:

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "What's the typical duration of a wedding ceremony?"
}
```

**Fields**:
- `conversation_id` (string, UUID, optional): Existing conversation ID. If omitted, create new conversation.
- `text` (string, required, max 2000 chars): Message text.

**Response (200 OK)**:

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "sender": "bot",
  "text": "The average wedding ceremony lasts 30-45 minutes, depending on your chosen officiant and traditions.",
  "timestamp": "2025-11-11T14:30:00Z",
  "faq_matched": true,
  "feedback": null
}
```

**Fields**:
- `id` (UUID): Message ID.
- `conversation_id` (UUID): Conversation this message belongs to.
- `sender` (string): `"bot"` (response) or `"customer"` (echo of sent message).
- `text` (string): Message text.
- `timestamp` (ISO8601): Server timestamp.
- `faq_matched` (boolean): True if answer came from FAQ (vs. RAG API).
- `feedback` (object, nullable): Feedback object if customer already gave feedback.

**Behavior**:
1. Validate customer is authenticated.
2. Fetch or create Conversation.
3. Store customer Message (sender="customer").
4. Check if message text matches any FAQ (substring or fuzzy match).
5. If FAQ match: Return FAQ answer immediately (faq_matched=true).
6. Else: Call RAG API with message text; wait up to 10 seconds for response.
7. On RAG API error or timeout: Return fallback message (faq_matched=false).
8. Store bot Message (sender="bot").
9. Return bot message with 200 OK.

**Error Cases**:

- **400 Bad Request**: Empty text, invalid conversation_id.
  ```json
  {
    "error": "Text must not be empty."
  }
  ```

- **401 Unauthorized**: Not logged in.
  ```json
  {
    "error": "Authentication required."
  }
  ```

- **403 Forbidden**: Trying to send message in another customer's conversation.
  ```json
  {
    "error": "Not authorized to send messages in this conversation."
  }
  ```

---

### 2. Get Frequently Asked Questions

**Endpoint**: `GET /api/chatbot/faqs/`

**Purpose**: Fetch list of active FAQs for UI display.

**Query Parameters**:
- None

**Response (200 OK)**:

```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "question": "What's the typical duration of a wedding ceremony?",
    "answer": "The average wedding ceremony lasts 30-45 minutes, depending on your chosen officiant and traditions.",
    "order": 1
  },
  {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "question": "Can we customize the menu?",
    "answer": "Yes! We offer customizable menu options. Contact your wedding planner for details.",
    "order": 2
  }
]
```

**Fields**:
- `id` (UUID): FAQ ID.
- `question` (string): Question text.
- `answer` (string): Answer text.
- `order` (integer): Display order (ascending).

**Behavior**:
1. Query FAQ model for `is_active=true`.
2. Sort by `order` ascending.
3. Return JSON array.

**Caching**:
- Set `Cache-Control: max-age=3600` (1 hour).
- Client can cache and refetch on widget reopen.

**Error Cases**:

- **401 Unauthorized**: Not logged in.

---

### 3. Get Conversation History (Messages)

**Endpoint**: `GET /api/chatbot/conversations/<conversation_id>/messages/`

**Purpose**: Fetch all messages in a conversation (for chat history display).

**Path Parameters**:
- `conversation_id` (UUID): Conversation ID.

**Query Parameters**:
- `limit` (integer, optional, default 50, max 100): Number of messages to return.
- `offset` (integer, optional, default 0): Offset for pagination.

**Response (200 OK)**:

```json
{
  "count": 10,
  "next": "/api/chatbot/conversations/550e8400-e29b-41d4-a716-446655440000/messages/?limit=50&offset=50",
  "previous": null,
  "results": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "sender": "customer",
      "text": "What's the typical duration of a wedding ceremony?",
      "timestamp": "2025-11-11T14:25:00Z",
      "feedback": null
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "sender": "bot",
      "text": "The average wedding ceremony lasts 30-45 minutes...",
      "timestamp": "2025-11-11T14:25:05Z",
      "feedback": {
        "id": "990e8400-e29b-41d4-a716-446655440004",
        "value": "up"
      }
    }
  ]
}
```

**Fields**:
- `count` (integer): Total messages in conversation.
- `next` / `previous` (string, nullable): Pagination URLs.
- `results` (array): Message objects.
  - `id` (UUID): Message ID.
  - `sender` (string): `"customer"` or `"bot"`.
  - `text` (string): Message text.
  - `timestamp` (ISO8601): Timestamp.
  - `feedback` (object, nullable): Feedback if present.
    - `id` (UUID): Feedback ID.
    - `value` (string): `"up"` or `"down"`.

**Behavior**:
1. Validate customer is authenticated.
2. Verify customer owns the conversation.
3. Fetch messages, ordered by timestamp ascending.
4. For each message, include feedback if exists.
5. Return paginated results.

**Error Cases**:

- **401 Unauthorized**: Not logged in.
- **403 Forbidden**: Customer does not own this conversation.
- **404 Not Found**: Conversation not found.

---

### 4. Submit Feedback

**Endpoint**: `POST /api/chatbot/feedback/`

**Purpose**: Customer submits thumbs up/down feedback on a bot message. Feedback is forwarded to RAG API.

**Request Body**:

```json
{
  "message_id": "660e8400-e29b-41d4-a716-446655440002",
  "value": "up"
}
```

**Fields**:
- `message_id` (UUID, required): ID of the message being rated.
- `value` (string, required): `"up"` or `"down"`.

**Response (200 OK)**:

```json
{
  "success": true,
  "message": "Feedback submitted to RAG API"
}
```

**Fields**:
- `success` (boolean): Whether feedback was successfully forwarded to RAG API.
- `message` (string): Status message.

**Behavior**:
1. Validate customer is authenticated.
2. Fetch message; verify it's a bot message (sender="bot").
3. Extract message context (conversation_id, customer_id, message_id, text, timestamp).
4. Forward feedback to RAG API: `{ message_id, conversation_id, customer_id, value, timestamp }`.
5. Wait up to 5 seconds for RAG API response.
6. Return success or error to client (don't silently fail).

**Error Cases**:

- **400 Bad Request**: Invalid value (not "up" or "down").
  ```json
  {
    "error": "Value must be 'up' or 'down'."
  }
  ```

- **401 Unauthorized**: Not logged in.
- **404 Not Found**: Message not found.
- **502 Bad Gateway**: RAG API unreachable.
  ```json
  {
    "error": "Failed to submit feedback to RAG API. Please try again."
  }
  ```

**Note**: Feedback is NOT stored in YourPlanner database (MVP scope). RAG API is responsible for logging, analysis, and KPI tracking.

---

### 5. Get Chat Configuration

**Endpoint**: `GET /api/chatbot/config/`

**Purpose**: Fetch client-side configuration (polling interval, fallback message).

**Query Parameters**:
- None

**Response (200 OK)**:

```json
{
  "polling_interval_ms": 2500,
  "fallback_message": "I'm sorry, I'm not sure how to help with that. Would you like to rephrase? If not, you can always send an email to your wedding planner."
}
```

**Fields**:
- `polling_interval_ms` (integer): AJAX polling interval in milliseconds.
- `fallback_message` (string): Message shown when bot cannot answer.

**Behavior**:
1. Load ChatConfig singleton.
2. Return public fields only (never expose RAG API key or URL).

**Caching**:
- Set `Cache-Control: max-age=3600` (1 hour).
- Client can cache and refetch on widget init.

---

### 6. Get Active Conversations (for session restore)

**Endpoint**: `GET /api/chatbot/conversations/`

**Purpose**: Fetch customer's active (or recent) conversations (for widget state restoration on page load).

**Query Parameters**:
- `status` (string, optional, default "active"): Filter by status (`"active"` or `"closed"`).
- `limit` (integer, optional, default 10): Number of conversations to return.

**Response (200 OK)**:

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "active",
    "started_at": "2025-11-11T14:00:00Z",
    "ended_at": null,
    "message_count": 5
  }
]
```

**Fields**:
- `id` (UUID): Conversation ID.
- `status` (string): `"active"` or `"closed"`.
- `started_at` (ISO8601): Start timestamp.
- `ended_at` (ISO8601, nullable): End timestamp.
- `message_count` (integer): Number of messages.

**Behavior**:
1. Validate customer is authenticated.
2. Fetch conversations for authenticated customer, filtered by status.
3. Return most recent first (order by `-started_at`).
4. Limit to N conversations.

**Error Cases**:

- **401 Unauthorized**: Not logged in.

---

## Client-Side Usage (Vue.js Widget)

### Widget Initialization

```javascript
// On page load or widget first open:
async function initializeWidget() {
  // 1. Restore config
  const config = await fetch('/api/chatbot/config/').then(r => r.json());
  this.pollingInterval = config.polling_interval_ms;
  this.fallbackMessage = config.fallback_message;
  
  // 2. Restore active conversations
  const conversations = await fetch('/api/chatbot/conversations/?status=active')
    .then(r => r.json());
  if (conversations.length > 0) {
    this.currentConversation = conversations[0]; // Resume last active
    await this.loadMessages();
  }
  
  // 3. Load FAQs
  const faqs = await fetch('/api/chatbot/faqs/').then(r => r.json());
  this.faqs = faqs;
  
  // 4. Start polling (if conversation active)
  if (this.currentConversation) {
    this.startPolling();
  }
}
```

### Sending a Message

```javascript
async function sendMessage(text) {
  const payload = {
    conversation_id: this.currentConversation?.id || null,
    text
  };
  
  const response = await fetch('/api/chatbot/messages/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }).then(r => r.json());
  
  // Store bot response locally
  this.messages.push(response);
  this.currentConversation = response.conversation_id;
  
  // Trigger feedback template
  this.showFeedbackFor = response.id;
}
```

### Polling for New Messages

```javascript
async function pollNewMessages() {
  const response = await fetch(
    `/api/chatbot/conversations/${this.currentConversation.id}/messages/?limit=50`
  ).then(r => r.json());
  
  // Merge with local cache
  this.messages = response.results;
}

// Start polling every N milliseconds
function startPolling() {
  this.pollInterval = setInterval(() => {
    this.pollNewMessages();
  }, this.pollingInterval);
}

function stopPolling() {
  clearInterval(this.pollInterval);
}
```

---

## Error Handling

All endpoints follow this error response format:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

**Common error codes**:
- `VALIDATION_ERROR`: Input validation failed.
- `NOT_AUTHENTICATED`: User not logged in.
- `NOT_AUTHORIZED`: User not authorized for this resource.
- `NOT_FOUND`: Resource not found.
- `INTERNAL_ERROR`: Server error.

---

## Performance Targets

- **Send Message**: <300ms p95 (FAQ match) or <600ms p95 (RAG API call).
- **Get Messages**: <200ms p95 (DB query + serialization).
- **Get FAQs**: <100ms p95 (cached or simple query).
- **Get Config**: <50ms p95 (singleton, no DB).

---

## Security Considerations

1. **Authentication**: All endpoints except health checks require Django session or token.
2. **Authorization**: Customers can only access their own conversations, messages, and feedback.
3. **Rate Limiting** (Phase 2): Prevent spam (e.g., 10 messages/minute per customer).
4. **Input Validation**: Sanitize message text; prevent XSS.
5. **API Key Handling**: RAG API key never exposed to client.
6. **CORS**: Allow requests from same origin (Django template) only.

---

## OpenAPI Schema (Partial)

See `api.openapi.json` for full OpenAPI 3.0 specification. Example:

```yaml
openapi: 3.0.0
info:
  title: VasiliasBot Chat API
  version: 1.0.0
  description: Customer chatbot API for YourPlanner

paths:
  /api/chatbot/messages/:
    post:
      summary: Send a message
      operationId: sendMessage
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                conversation_id:
                  type: string
                  format: uuid
                text:
                  type: string
              required:
                - text
      responses:
        '200':
          description: Message sent and bot replied
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Message'
        '400':
          description: Validation error
```

---

## Testing

### Unit Test Example (DRF)

```python
# tests/test_views.py
from rest_framework.test import APITestCase
from users.models import Customer
from chatbot.models import Conversation, Message, FAQ

class MessageSendTestCase(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create_user(
            email='test@example.com',
            password='password'
        )
        self.client.force_authenticate(user=self.customer)
    
    def test_send_message_creates_conversation(self):
        response = self.client.post('/api/chatbot/messages/', {
            'text': 'Hello bot!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['conversation_id'])
        self.assertEqual(Conversation.objects.count(), 1)
    
    def test_send_message_matches_faq(self):
        FAQ.objects.create(
            question="What's the duration?",
            answer="30-45 minutes.",
            is_active=True
        )
        response = self.client.post('/api/chatbot/messages/', {
            'text': "What's the duration?"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['faq_matched'])
```

---

## Summary

The VasiliasBot API is straightforward, RESTful, and designed for client-side polling. Key endpoints:
1. **POST /messages/** — Send/receive messages
2. **GET /faqs/** — Fetch FAQ list
3. **GET /conversations/<id>/messages/** — Fetch history
4. **POST /feedback/** — Submit rating
5. **GET /config/** — Fetch client config
6. **GET /conversations/** — Restore session

All endpoints authenticated, JSON-based, and documented for client integration.

---

<!-- Changes: Phase 1 API contracts defined; full endpoint specifications, request/response formats, error handling, and usage examples documented. -->
