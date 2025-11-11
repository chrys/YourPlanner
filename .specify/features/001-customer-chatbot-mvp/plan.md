# Implementation Plan: Customer Chatbot MVP (VasiliasBot)

**Branch**: `001-customer-chatbot-mvp` | **Date**: 2025-11-11 | **Spec**: [customer-chatbot-mvp.md](./customer-chatbot-mvp.md)

## Summary

Build a customer-facing chatbot (VasiliasBot) as a Vue.js widget integrated with Django backend via AJAX polling. The MVP provides rule-based FAQ answers to signed-in Customers with thumbs up/down feedback. Django acts as middleware, forwarding messages to an external RAG API (FastAPI, out of scope). The chatbot persists conversations across page navigation, displays a typing indicator, and provides graceful fallback messages for unanswerable questions.

## Technical Context

**Language/Version**: Python 3.13.9 (Django 5.1.12)  
**Primary Dependencies**: Django 5.1.12, Vue.js 3, Bootstrap 5, DRF (Django REST Framework)  
**Frontend Framework**: Vue.js 3 (single-file components with TypeScript, AJAX polling)  
**Storage**: SQLite3 (dev), PostgreSQL (prod) — existing databases  
**Testing**: pytest (backend), Playwright (frontend/UI smoke tests)  
**Target Platform**: Web (responsive, browser-based)  
**Project Type**: Web application (monolithic Django + frontend Vue.js widget)  
**Performance Goals**: AJAX poll responses <300ms p95; chat widget init <500ms  
**Constraints**: Non-intrusive widget in bottom-right corner; <100KB gzipped JS+CSS; offline graceful degradation  
**Scale/Scope**: Single feature affecting authenticated Customers; MVP: 10-15 FAQs, <1K conversations/day in dev

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| Code Quality and Consistency | Black, ruff, isort, mypy MUST pass; no secrets in VCS | ✅ CLEAR (no blocking issues for MVP) |
| Test Discipline and Coverage | Unit tests for logic; integration tests for chat flow; ≥85% coverage | ✅ CLEAR (new code will be tested) |
| UX Consistency and Accessibility | WCAG 2.1 AA; shared components; keyboard navigation; clear states | ⚠️ PARTIAL (MVP scope: basic keyboard support, no advanced a11y until Phase 2) |
| Performance and Efficiency | p95 <300ms for GETs; select_related/prefetch; lazy-load; <200KB gzipped CSS+JS | ✅ CLEAR (AJAX polling, minimal JS footprint) |
| Security and Observability | DEBUG=False; CSRF enabled; secure cookies; structured logging; request IDs | ✅ CLEAR (Django security defaults; logging needed in Phase 1) |

**Justification**: MVP trades advanced a11y (Phase 2 enhancement) for faster time-to-market. Core UX (keyboard close, tab order) will be included.

## Project Structure

### Documentation (this feature)

```
.specify/features/001-customer-chatbot-mvp/
├── customer-chatbot-mvp.md    # Feature spec
├── plan.md                     # This file
├── research.md                 # Phase 0 output (TBD)
├── data-model.md               # Phase 1 output (TBD)
├── quickstart.md               # Phase 1 output (TBD)
├── contracts/                  # Phase 1 output (TBD)
│   ├── api.openapi.json       # REST API schema
│   └── vue-component.schema.json # Vue component interface
└── tasks.md                    # Phase 2 output (via /speckit.tasks)
```

### Source Code (Django repository root)

```
YourPlanner/
├── core/                       # Existing Django app
│   ├── static/core/
│   │   ├── css/vassbot.css    # Widget styling
│   │   └── js/vassbot.js      # Vue.js component initialization
│   ├── templates/core/
│   │   └── _vassbot_widget.html # Widget HTML template
│   └── views.py               # (update: add chat endpoints)
├── chatbot/                    # NEW Django app for chatbot
│   ├── __init__.py
│   ├── admin.py               # FAQ, Conversation, Message, Feedback models
│   ├── apps.py
│   ├── models.py              # Conversation, Message, Feedback, FAQ, ChatConfig
│   ├── views.py               # Chat endpoints (send message, get FAQs, get history)
│   ├── api_urls.py            # DRF routes for chat
│   ├── urls.py
│   ├── serializers.py         # MessageSerializer, FeedbackSerializer, FAQSerializer
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py     # Unit tests for models
│   │   ├── test_views.py      # Integration tests for chat flow
│   │   └── test_feedback.py   # Feedback logic
│   ├── migrations/
│   │   └── 0001_initial.py    # Initial schema (Conversation, Message, Feedback, FAQ, ChatConfig)
│   └── templatetags/
│       └── chatbot_tags.py    # Optional template helpers
├── YourPlanner/
│   ├── settings.py            # (update: add chatbot app, INSTALLED_APPS; logging config)
│   ├── urls.py                # (update: include chatbot.urls)
│   └── wsgi.py
└── tests-UI/
    ├── chatbot-mvp.spec.ts    # Playwright test: open widget, send message, verify feedback
```

**Structure Decision**: Monolithic Django + embedded Vue.js widget. New `chatbot` app isolates chat logic; `core` app hosts widget UI. This avoids unnecessary complexity (e.g., separate FastAPI server for MVP) while keeping concerns separated.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None identified | N/A | N/A |

---

## Phase 0: Outline & Research

### Research Tasks

1. **AJAX polling best practices for Django**
   - Decision: Use jQuery/vanilla JS with `setInterval` or Fetch API for polling; store poll interval in ChatConfig model (configurable in Admin). Consider exponential backoff on error.
   - Rationale: Simpler than WebSockets for MVP; allows rate limiting and graceful degradation.
   - Alternatives: WebSockets (deferred to Phase 2), Server-Sent Events (overkill).

2. **Vue.js 3 single-file components + Django integration**
   - Decision: Use Vue 3 with vite/webpack (or plain <script setup>). Load Vue widget via Django template script tag; initialize with customer ID and conversation ID.
   - Rationale: Vue 3 is modern and integrates well with Django templates; no build step required if using CDN.
   - Alternatives: React (already Vue in project stack), Alpine.js (too minimal for complex chat UI).

3. **localStorage vs session-based persistence**
   - Decision: Use localStorage for client-side history cache; Django session for server-side state. On page reload, fetch from server to ensure consistency.
   - Rationale: Balances UX (instant history) with data integrity.
   - Alternatives: SessionStorage (lost on browser close), IndexedDB (overkill).

4. **RAG API integration pattern (FastAPI)**
   - Decision: Define ChatConfig model with RAG API URL and API key (editable in Admin). Django endpoint forwards message as JSON to RAG API, receives response, stores in DB.
   - Rationale: Decouples chatbot from RAG implementation; allows swapping RAG provider.
   - Alternatives: Direct client-side call (breaks CORS, leaks API key), WebSocket relay (MVP too complex).

5. **Feedback logging architecture**
   - Decision: Store Feedback records in DB. Admin can view/export. Optional: Send feedback to RAG API via separate async task (Celery job, deferred to Phase 2).
   - Rationale: MVP logs locally for visibility; Phase 2 integrates with RAG for training.
   - Alternatives: Direct RAG API call (adds latency to user action), file-based logging (unscalable).

### Output

**research.md** will consolidate these decisions with implementation notes.

---

## Phase 1: Design & Contracts

### Data Model (data-model.md)

Extract from spec; refine with Django field types:

- **Conversation**: `id (UUIDField)`, `customer (ForeignKey → User)`, `started_at (DateTimeField)`, `ended_at (DateTimeField, null)`, `status (CharField, choices: active/closed)`, `metadata (JSONField, default {})`
- **Message**: `id (UUIDField)`, `conversation (FK)`, `customer (FK → User)`, `text (TextField)`, `timestamp (DateTimeField)`, `sender (CharField, choices: customer/bot)`
- **Feedback**: `id (UUIDField)`, `message (FK)`, `customer (FK → User)`, `value (CharField, choices: up/down)`, `timestamp (DateTimeField)`, unique constraint `(message, customer)` (one feedback per user per message)
- **FAQ**: `id (UUIDField)`, `question (TextField)`, `answer (TextField)`, `order (IntegerField)`, `is_active (BooleanField)`
- **ChatConfig**: `id (UUIDField)`, `rag_api_url (CharField, max_length=500)`, `rag_api_key (CharField, encrypted)`, `fallback_message (TextField)`, `polling_interval_ms (IntegerField)`, `updated_at (DateTimeField)`

### API Contracts (contracts/)

**REST Endpoints** (OpenAPI schema):

1. `POST /api/chatbot/messages/` — Send customer message
   - Input: `{ conversation_id?, message_text }`
   - Output: `{ message_id, conversation_id, sender: "bot", text, timestamp }`
   - Behavior: Store message, call RAG API, return bot response, store feedback template

2. `GET /api/chatbot/faqs/` — Fetch active FAQs
   - Output: `[ { id, question, answer, order } ]`
   - Caching: Etag or max-age 1 hour

3. `GET /api/chatbot/conversations/<id>/messages/` — Fetch conversation history
   - Output: `[ { id, sender, text, timestamp, feedback? } ]`
   - Auth: Customer can only fetch own conversations

4. `POST /api/chatbot/feedback/` — Submit feedback on message
   - Input: `{ message_id, value: up|down }`
   - Output: `{ success, feedback_id }`

5. `GET /api/chatbot/config/` — Get client config (poll interval, fallback message)
   - Output: `{ polling_interval_ms, fallback_message }`

### Vue.js Component Interface (contracts/vue-component.schema.json)

```json
{
  "component": "VasiliasBot",
  "props": {
    "apiBaseUrl": "string",
    "customerId": "string",
    "conversationId": "string | null"
  },
  "events": {
    "message-sent": "{ messageId, text }",
    "feedback-submitted": "{ messageId, value }"
  },
  "internal-state": {
    "isOpen": "boolean",
    "isLoading": "boolean",
    "messages": "Message[]",
    "faqs": "FAQ[]"
  }
}
```

### Quickstart (quickstart.md)

- Set up `chatbot` Django app
- Create models and migrations
- Write serializers and API views
- Create Vue.js component (`VasiliasBot.vue`)
- Integrate widget into base template
- Write unit and integration tests
- Test end-to-end chat flow

### Agent Context Update

Run `.specify/scripts/bash/update-agent-context.sh copilot` to register new technologies:
- Django REST Framework (DRF) patterns
- Vue.js 3 single-file components
- AJAX polling pattern
- UUID fields and Django UUIDs

---

## Gate Validation (Post-Phase 1)

*Re-evaluate Constitution Check after design:*

| Principle | Status |
|-----------|--------|
| Code Quality | ✅ CLEAR (Django linting, type hints planned; VCS security rules apply) |
| Test Discipline | ✅ CLEAR (unit + integration tests for models, views, Vue component) |
| UX Consistency | ✅ CLEAR (Bootstrap styling, shared form components, keyboard support in widget) |
| Performance | ✅ CLEAR (AJAX polling, lazy-load FAQs, <100KB JS footprint target) |
| Security | ✅ CLEAR (CSRF protection, authenticated endpoints, API key in ChatConfig encrypted) |

All gates pass. Proceed to Phase 2.

---

## Next Steps

1. Complete Phase 0: Research → **research.md**
2. Complete Phase 1 Design → **data-model.md**, **contracts/**, **quickstart.md**
3. Invoke `/speckit.tasks` to generate detailed task breakdown (**tasks.md**)
4. Begin development (see tasks.md for step-by-step tasks)

---

<!-- Changes: Initial implementation plan for VasiliasBot MVP, Phase 0-1 design. -->
