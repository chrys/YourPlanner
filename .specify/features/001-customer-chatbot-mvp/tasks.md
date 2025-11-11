# Implementation Tasks: VasiliasBot Customer Chatbot MVP

**Feature**: Customer Chatbot MVP (VasiliasBot) | **Branch**: `001-customer-chatbot-mvp` | **Date**: 2025-11-11

**Reference Documents**: [customer-chatbot-mvp.md](./customer-chatbot-mvp.md) | [plan.md](./plan.md) | [data-model.md](./data-model.md) | [contracts.md](./contracts.md) | [research.md](./research.md) | [quickstart.md](./quickstart.md)

---

## Task Execution Strategy

**MVP Scope**: Complete Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (US1: Core Chatbot). This delivers the minimum viable product: customers can open the chatbot, ask questions, and receive FAQ-based answers with feedback.

**Suggested Execution Order**:
1. **Phase 1** (Setup): Days 1-2 (project initialization, dependencies)
2. **Phase 2** (Foundational): Days 3-5 (Django models, migrations, admin interface, API contracts)
3. **Phase 3** (US1): Days 6-10 (chat widget, message endpoints, FAQ integration)
4. **Phase 4** (US2): Days 11-13 (fallback handling, graceful errors) — *Optional: defer to Phase 2 if time permits*
5. **Phase 5** (US3): Days 14-16 (persistence, typing indicator, close/transcript) — *Optional: defer to Phase 3*
6. **Phase 6** (Polish): Days 17-20 (testing, linting, documentation)

**Parallel Opportunities**:
- T016 (Message serializer) and T018 (FAQ serializer) can run in parallel (different files, no dependencies).
- T020 (Message view) and T023 (Config view) can run in parallel within Phase 2.
- T024-T026 (Vue component, styling, API integration) can run in parallel within Phase 3.

**Testing Strategy**: Minimal for MVP (smoke tests + integration tests for happy path). Unit tests added incrementally during Phase 6.

---

## Phase 1: Project Setup & Initialization

**Goal**: Initialize the Django chatbot app, install dependencies, configure settings, and create initial project structure.

**Acceptance Criteria**:
- ✅ `chatbot` Django app created and registered in `INSTALLED_APPS`
- ✅ Dependencies installed (Django REST Framework, requests)
- ✅ Django settings updated (chatbot app, logging configuration, API base URL)
- ✅ No errors on `python manage.py migrate` or `python manage.py check`

**Test Criteria**:
```bash
python manage.py check
python manage.py migrate
pytest --collect-only chatbot/tests/  # Verify test discovery
```

---

### Phase 1 Tasks

- [ ] T001 Create Django chatbot app with `python manage.py startapp chatbot` in repo root

- [ ] T002 Register `chatbot` app in `YourPlanner/settings.py` under `INSTALLED_APPS` and add logging configuration for chatbot module

- [ ] T003 Install dependencies: `pip install djangorestframework requests pytest pytest-django` and update `requirements.txt`

- [ ] T004 Create initial directory structure:
  - `chatbot/templates/chatbot/` (Vue widget HTML template)
  - `chatbot/static/chatbot/` (JS, CSS for widget)
  - `chatbot/tests/` (test suite)

---

## Phase 2: Foundational Models, Serializers & Admin Interface

**Goal**: Define all core data models (Conversation, Message, FAQ, ChatConfig), create migrations, implement serializers, and configure Django Admin for management.

**Acceptance Criteria**:
- ✅ All 4 models defined with correct fields, relationships, and constraints
- ✅ Initial migration created and applies without errors
- ✅ Django Admin interface displays all models with appropriate admin classes
- ✅ All serializers implement correct fields and validation
- ✅ No blocking errors on `python manage.py makemigrations` or `migrate`

**Test Criteria**:
```bash
python manage.py makemigrations chatbot
python manage.py migrate
python manage.py shell
# Test model creation interactively
from chatbot.models import Conversation, Message, FAQ, ChatConfig
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.first()
c = Conversation.objects.create(customer=u)
m = Message.objects.create(conversation=c, customer=u, text="Hi", sender="customer")
print(c, m)  # Verify objects created
```

---

### Phase 2 Tasks

- [ ] T005 Define `Conversation` model in `chatbot/models.py` with fields: id (UUID), customer (FK), started_at, ended_at, status (enum), metadata (JSON)

- [ ] T006 Define `Message` model in `chatbot/models.py` with fields: id (UUID), conversation (FK), customer (FK), text, timestamp, sender (enum)

- [ ] T007 Define `FAQ` model in `chatbot/models.py` with fields: id (UUID), question (unique), answer, order (int), is_active (bool), created_at, updated_at

- [ ] T008 Define `ChatConfig` singleton model in `chatbot/models.py` with fields: id (UUID), rag_api_url, rag_api_key (encrypted), fallback_message, polling_interval_ms, rag_api_timeout_seconds; implement `load()` classmethod

- [ ] T009 Create initial migration: `python manage.py makemigrations chatbot --name 0001_initial && python manage.py migrate chatbot`

- [ ] T010 [P] Create `ConversationAdmin` class in `chatbot/admin.py` with list_display, list_filter, search_fields, readonly_fields

- [ ] T011 [P] Create `MessageAdmin` class in `chatbot/admin.py` with list_display, list_filter, search_fields, readonly_fields for message history review

- [ ] T012 [P] Create `FAQAdmin` class in `chatbot/admin.py` with list_display, list_filter, search_fields for FAQ management (add, edit, delete, reorder)

- [ ] T013 [P] Create `ChatConfigAdmin` class in `chatbot/admin.py` to manage singleton config (RAG API endpoint, fallback message, polling interval)

- [ ] T014 Register all admin classes in `chatbot/admin.py` with `@admin.register(Model)` decorator

- [ ] T015 [P] Create `ConversationSerializer` in `chatbot/serializers.py` with fields: id, status, started_at, ended_at, message_count (computed)

- [ ] T016 [P] Create `MessageSerializer` in `chatbot/serializers.py` with fields: id, conversation_id, text, timestamp, sender, faq_matched (computed, optional)

- [ ] T017 [P] Create `FAQSerializer` in `chatbot/serializers.py` with fields: id, question, answer, order, is_active

- [ ] T018 [P] Create `ChatConfigSerializer` in `chatbot/serializers.py` with fields: polling_interval_ms, fallback_message (readonly to non-admin)

- [ ] T019 Verify all model constraints and relationships: test Conversation cascade delete, Message immutability, ChatConfig singleton load behavior

---

## Phase 3: User Story 1 — Core Chatbot Widget & Message Endpoints (Priority P1)

**Goal**: Build the foundational chat experience where signed-in customers can open VasiliasBot, send questions, and receive FAQ-based answers with feedback options.

**User Story**: Customer can open and use VasiliasBot

**Acceptance Criteria**:
- ✅ Chat widget opens when customer clicks icon in bottom-right corner
- ✅ Customer can type a message and send it via AJAX
- ✅ Bot responds with FAQ answer (if matched) or fallback message within 5 seconds
- ✅ Feedback buttons (thumbs up/down) appear below bot messages
- ✅ Conversation persists across widget open/close
- ✅ Widget styling matches website branding

**Independent Test Criteria**:
```bash
# Backend: Send message and receive response
curl -X POST http://localhost:8000/api/chatbot/messages/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{"text":"What'\''s the duration?"}'
# Expect: 200 OK with bot message

# Frontend (Playwright):
# 1. Open page as authenticated customer
# 2. Click chatbot icon
# 3. Type "What's the duration?" and press Enter
# 4. Verify bot response appears within 5 seconds
# 5. Verify feedback buttons present
```

---

### Phase 3 Tasks (User Story 1)

- [ ] T020 [P] Create `message_view()` in `chatbot/views.py` (POST /api/chatbot/messages/):
  - Extract/create Conversation, store Message (sender=customer)
  - Check FAQ match (substring or simple fuzzy match)
  - If match: Return FAQ answer immediately (faq_matched=true)
  - Else: Call RAG API (see T025); return bot Message on success, fallback on error
  - Handle 400/401/500 errors with proper messages
  - Implement 10s timeout for RAG API

- [ ] T021 [P] Create `conversations_view()` in `chatbot/views.py` (GET /api/chatbot/conversations/?status=active&limit=1):
  - Return paginated list of customer's conversations with message count
  - Support filtering by status (active/closed)
  - Sort by -started_at (most recent first)

- [ ] T022 [P] Create `get_messages_view()` in `chatbot/views.py` (GET /api/chatbot/conversations/<id>/messages/?limit=50):
  - Return paginated messages for a conversation
  - Verify customer owns conversation (403 if not)
  - Sort by timestamp (oldest first)

- [ ] T023 [P] Create `faqs_view()` in `chatbot/views.py` (GET /api/chatbot/faqs/):
  - Return list of active FAQs (is_active=true)
  - Sort by order field
  - Cache response for 1 hour (see T025 for caching strategy)

- [ ] T024 [P] Create `config_view()` in `chatbot/views.py` (GET /api/chatbot/config/):
  - Return ChatConfig singleton (polling_interval_ms, fallback_message)
  - Readonly endpoint (no POST)

- [ ] T025 Create `RAG API integration` in `chatbot/views.py`:
  - In message_view, call RAG API with POST {conversation_id, message_id, text, customer_id}
  - Use ChatConfig.rag_api_url, rag_api_key (Bearer token auth)
  - Implement 10s timeout with requests.post()
  - Handle timeout/500 errors: return fallback message + 502 BAD_GATEWAY
  - Log all RAG API calls (success and errors) with request/response body (for debugging)

- [ ] T026 Create Django URL routing in `chatbot/api_urls.py`:
  - Map `path('messages/', views.message_view)` → POST handler
  - Map `path('conversations/', views.conversations_view)` → GET handler
  - Map `path('conversations/<str:id>/messages/', views.get_messages_view)` → GET handler
  - Map `path('faqs/', views.faqs_view)` → GET handler
  - Map `path('config/', views.config_view)` → GET handler
  - Map `path('feedback/', views.feedback_view)` → POST handler (for T032)
  - Include in `YourPlanner/urls.py` as `path('api/chatbot/', include('chatbot.api_urls'))`

- [ ] T027 [P] Create Vue.js widget component in `core/static/core/js/vassbot.js`:
  - Component name: `VasiliasBot` (Vue 3 single-file or setup script)
  - Props: none (global mount)
  - State: isOpen, isLoading, messages, inputText, currentConversationId, faqs, pollingInterval
  - Methods: toggleWidget(), initializeWidget(), loadMessages(), sendMessage(), submitFeedback()
  - Polling: startPolling() / stopPolling() using setInterval
  - AJAX: fetch() calls to /api/chatbot endpoints with Bearer/session auth
  - Error handling: Log errors to console; show fallback message to user

- [ ] T028 [P] Create Vue.js widget template in `core/templates/core/_vassbot_widget.html`:
  - Chat window (350px wide, 500px tall, bottom-right corner)
  - Header with title "VasiliasBot" and close button
  - Messages list with customer/bot distinction (colors, alignment)
  - Input field for typing + Send button
  - FAQ list (if no messages yet)
  - Typing indicator (animated dots)
  - Feedback buttons (thumbs up/down) below bot messages

- [ ] T029 [P] Create widget styling in `core/static/core/css/vassbot.css`:
  - Fixed position (bottom-right corner, z-index 9999)
  - Gradient header (#667eea → #764ba2) matching site branding
  - Message bubbles: customer (blue), bot (light gray)
  - Responsive on mobile (≤350px width may stack or reduce height)
  - Smooth animations: slideIn for window, bounce for typing indicator
  - Accessibility: Focus styles for buttons, keyboard navigation

- [ ] T030 [P] Initialize Vue widget in Django template:
  - Include `_vassbot_widget.html` in `core/templates/core/base.html` (or similar base template)
  - Include script tag for `vassbot.js` with global Vue app initialization
  - Ensure widget only renders for authenticated users (conditional in template)
  - Test widget loads on page refresh

- [ ] T031 [P] Implement message persistence (local or session storage):
  - Store conversation_id in localStorage/sessionStorage on successful message send
  - Retrieve on widget open to restore conversation context
  - Clear on explicit close or session timeout

---

## Phase 4: User Story 2 — FAQ Selection & Fallback Handling (Priority P2)

**Goal**: Improve user experience by letting customers explicitly select FAQs and gracefully handling unanswerable questions.

**User Story**: FAQ selection and fallback handling

**Acceptance Criteria**:
- ✅ FAQ list displays in widget when no conversation active
- ✅ Customer can click FAQ to send question
- ✅ Bot responds with exact FAQ answer (no RAG call needed)
- ✅ If question doesn't match FAQ, fallback message shown
- ✅ Fallback suggests rephrasing or contacting support

**Independent Test Criteria**:
```bash
# Backend: FAQ endpoint
curl http://localhost:8000/api/chatbot/faqs/ -H "Cookie: sessionid=..."
# Expect: 200 OK with list of 5+ FAQs (from admin fixture)

# Test FAQ match: Send exact FAQ question
curl -X POST http://localhost:8000/api/chatbot/messages/ \
  -d '{"text":"What'\''s the typical duration of a wedding ceremony?"}' \
  -H "Cookie: sessionid=..." \
  -H "Content-Type: application/json"
# Expect: faq_matched=true, answer from FAQ

# Test fallback: Send unanswerable question (mock RAG API to error or timeout)
curl -X POST http://localhost:8000/api/chatbot/messages/ \
  -d '{"text":"What'\''s the meaning of life?"}' \
  -H "Cookie: sessionid=..." \
  -H "Content-Type: application/json"
# Expect: faq_matched=false, fallback message (RAG API not in scope for MVP tests)
```

---

### Phase 4 Tasks (User Story 2)

- [ ] T032 [P] Enhance FAQ matching in message_view (T020):
  - Implement fuzzy matching (e.g., using `difflib.SequenceMatcher` or simple keyword matching)
  - Check question similarity to all active FAQs
  - If score > 0.8: Return FAQ answer (faq_matched=true)
  - Else: Attempt RAG API call; if fails, return fallback

- [ ] T033 [P] Create fallback message strategy in ChatConfig:
  - Add field: `fallback_message` (text, editable in Admin)
  - Default: "I'm sorry, I'm not sure how to help with that. Would you like to rephrase your question? If not, you can contact your wedding planner."
  - Use in message_view on RAG API error/timeout

- [ ] T034 [P] Update Vue widget to display FAQs:
  - Show FAQ list when no messages in conversation
  - Render as clickable buttons in `.vasbot-faqs` container
  - On click: Send FAQ question as customer message, get FAQ answer from bot

- [ ] T035 [P] Test FAQ matching logic:
  - Unit test: Create 5 FAQs with different questions
  - Test: Send exact match → faq_matched=true
  - Test: Send partial/fuzzy match → faq_matched=true (if score > 0.8)
  - Test: Send completely unrelated query → faq_matched=false, fallback returned

---

## Phase 5: User Story 3 — Conversation Persistence & Interactive Feedback (Priority P3)

**Goal**: Enhance user experience with persistent conversations across page navigation, typing indicator, and transcript download.

**User Story**: Conversation persistence and UI feedback

**Acceptance Criteria**:
- ✅ Conversation history persists when user navigates between pages
- ✅ Typing indicator appears while bot is processing
- ✅ Close button clears conversation and closes widget
- ✅ Request transcript button fetches and downloads conversation as text/PDF

**Independent Test Criteria**:
```bash
# Test persistence:
# 1. Open chat, send message, verify response
# 2. Navigate to different URL (e.g., /orders/)
# 3. Return to original URL or any page
# 4. Verify conversation history still present in widget

# Test typing indicator:
# 1. Send message
# 2. Observe "..." animation for 1-3 seconds
# 3. Verify stops when bot reply arrives

# Test close & transcript:
# 1. Send messages to build conversation
# 2. Click "Download Transcript" → verify text file downloads
# 3. Click "Close Chat" → verify widget closes, conversation_id cleared from storage
```

---

### Phase 5 Tasks (User Story 3)

- [ ] T036 [P] Enhance Vue widget polling:
  - On message send, start polling every `pollingInterval` ms (from config)
  - Stop polling when: bot responds, conversation closed, widget closed, user navigates away
  - Prevent duplicate polls (use abort/cancel pattern)

- [ ] T037 [P] Implement typing indicator in Vue component:
  - Add state: `isLoading` (bool)
  - Set isLoading=true when message sent
  - Display `.vasbot-typing` container (animated dots) while isLoading=true
  - Hide when bot message received
  - Add CSS animation for bounce effect (see T029)

- [ ] T038 [P] Implement close button logic:
  - Button in widget header (X icon, top-right)
  - On click: Set isOpen=false, stop polling, clear currentConversationId from storage
  - Optional: POST to /api/chatbot/conversations/<id>/close/ to mark conversation closed (or defer to Phase 6)

- [ ] T039 [P] Implement transcript download:
  - Button in widget footer or menu: "Download Transcript"
  - On click: Fetch all messages for current conversation
  - Format as plain text: "[HH:MM] Customer: ...\n[HH:MM] Bot: ...\n"
  - Create Blob, trigger browser download (filename: vasbot-transcript-{id}.txt)
  - Alternative: Generate PDF (requires library, defer to Phase 6)

- [ ] T040 [P] Update conversation end logic in views:
  - Add optional endpoint: POST /api/chatbot/conversations/<id>/close/ (or defer)
  - Sets conversation.status = 'closed', conversation.ended_at = now()
  - Return 200 OK

---

## Phase 6: Testing, Quality & Polish

**Goal**: Ensure code quality, test coverage, and documentation completeness. Add integration tests, fix linting errors, and verify all acceptance criteria.

**Acceptance Criteria**:
- ✅ All tests pass: `pytest chatbot/tests/ --cov=chatbot --cov-min=85`
- ✅ Linting passes: `black --check chatbot/` and `ruff check chatbot/`
- ✅ Type checking passes: `mypy chatbot/` (or minimal for MVP)
- ✅ Security checks pass: No secrets in code, CSRF enabled, secure session cookies
- ✅ Documentation complete: README, API docs, setup guide

**Test Criteria**:
```bash
pytest chatbot/tests/ -v --tb=short
pytest chatbot/tests/ --cov=chatbot --cov-report=term-missing
black --check chatbot/
ruff check chatbot/
```

---

### Phase 6 Tasks

- [ ] T041 [P] Write unit tests for Conversation model in `chatbot/tests/test_models.py`:
  - Test: Create conversation with valid customer → id, status, started_at set correctly
  - Test: Conversation cascade delete when customer deleted
  - Test: Conversation metadata stored and retrieved
  - Test: status field restricted to enum values

- [ ] T042 [P] Write unit tests for Message model in `chatbot/tests/test_models.py`:
  - Test: Create message with valid fields → id, timestamp, sender set
  - Test: Message immutable after creation (attempt update, expect no-op or error)
  - Test: sender field restricted to enum (customer/bot)
  - Test: Message cascade delete when conversation deleted

- [ ] T043 [P] Write unit tests for FAQ model in `chatbot/tests/test_models.py`:
  - Test: Create FAQ with unique question → stored correctly
  - Test: question uniqueness constraint enforced (duplicate raises error)
  - Test: is_active field controls visibility
  - Test: order field controls sorting

- [ ] T044 [P] Write unit tests for ChatConfig model in `chatbot/tests/test_models.py`:
  - Test: ChatConfig.load() returns singleton instance
  - Test: load() creates default instance if not exists
  - Test: rag_api_url, fallback_message editable in Admin

- [ ] T045 [P] Write integration test for message endpoint in `chatbot/tests/test_views.py`:
  - Test: Send message as authenticated customer → 200 OK, Message created
  - Test: Unauthenticated request → 401 Unauthorized
  - Test: Empty text → 400 Bad Request
  - Test: FAQ match → faq_matched=true in response
  - Test: Non-match → RAG API called (mock) → bot response returned

- [ ] T046 [P] Write integration test for conversations endpoint in `chatbot/tests/test_views.py`:
  - Test: GET /conversations/ → returns customer's conversations only
  - Test: Filtering by status → returns active/closed conversations correctly
  - Test: Pagination → limit, offset parameters work

- [ ] T047 [P] Write integration test for faqs endpoint in `chatbot/tests/test_views.py`:
  - Test: GET /faqs/ → returns list of active FAQs
  - Test: is_active=false FAQs excluded
  - Test: Sorted by order field

- [ ] T048 [P] Write integration test for feedback endpoint in `chatbot/tests/test_views.py`:
  - Test: POST /feedback/ with valid message_id, value → calls RAG API (mock), returns 200 OK
  - Test: Invalid message_id → 404 Not Found
  - Test: Invalid value (not 'up'/'down') → 400 Bad Request
  - Test: RAG API failure → 502 BAD_GATEWAY returned

- [ ] T049 [P] Write Playwright smoke test for widget in `tests-UI/chatbot-mvp.spec.ts`:
  - Test: Open page as authenticated customer
  - Test: Chat icon visible in bottom-right
  - Test: Click icon → widget opens
  - Test: Type message, send → message appears as customer message
  - Test: Wait 5 seconds → bot message appears
  - Test: Feedback buttons visible below bot message
  - Test: Click thumbs up → feedback submitted (mock)
  - Test: Close widget → isOpen=false
  - Test: Reopen widget → conversation history still visible

- [ ] T050 Test FAQs integration in widget (Playwright):
  - Test: Open widget with no conversation
  - Test: FAQ list displayed
  - Test: Click FAQ → message sent with FAQ question
  - Test: Bot response is exact FAQ answer

- [ ] T051 Run all tests:
  - `pytest chatbot/tests/ -v --tb=short` → all pass
  - `pytest chatbot/tests/ --cov=chatbot` → coverage ≥85%
  - `black chatbot/` → code formatted
  - `ruff check chatbot/` → no linting errors
  - `mypy chatbot/ --ignore-missing-imports` → type checking passes (or deferred to Phase 2)

- [ ] T052 [P] Add docstrings and type hints to all views and models:
  - Each function: Include 1-2 line docstring + type hints on params/return
  - Models: Document field purpose and constraints
  - Views: Document request/response format in docstring

- [ ] T053 [P] Create API documentation (OpenAPI/Swagger):
  - Generate from DRF or manually document in `contracts.md`
  - Include all 6 endpoints, request/response schemas, error codes
  - Host at `/api/docs/` or in markdown in repo

- [ ] T054 Create setup/installation guide in `README_CHATBOT.md`:
  - Prerequisites: Python 3.13+, Django 5.1+, sqlite3/postgres
  - Installation steps: Clone, pip install, python manage.py migrate
  - Configuration: Set RAG API endpoint in Admin
  - Running tests: pytest command
  - Troubleshooting: Common issues (e.g., widget not loading, RAG API timeout)

- [ ] T055 [P] Add error logging and observability:
  - Log all RAG API calls (request body, response status, latency) at INFO level
  - Log FAQmatches and fallback usage at DEBUG level
  - Include request ID in logs (Django middleware or context var)
  - Test: Verify logs appear in console/file on message send, FAQ match, RAG call

- [ ] T056 [P] Configure CORS and security settings:
  - Ensure `CSRF_TRUSTED_ORIGINS` includes localhost, production domain
  - Verify `SESSION_COOKIE_SECURE = True` in production
  - Verify `SESSION_COOKIE_HTTPONLY = True`
  - Test: Widget works on same origin, blocked on different origin (CORS)

- [ ] T057 [P] Code review and final checklist:
  - Black formatting applied
  - Ruff linting clean
  - All tests passing (≥85% coverage)
  - No hardcoded secrets (API keys, passwords)
  - Docstrings and type hints complete
  - CHANGELOG.md updated with feature summary
  - Feature branch ready for PR and merge to main

---

## Dependency Graph & Execution Order

```
Phase 1 (Setup)
├─ T001 Create app
├─ T002 Register app
├─ T003 Install deps
└─ T004 Create directories

Phase 2 (Foundational)
├─ T005–T008 Define models (can run in parallel)
├─ T009 Run migrations (depends on T005–T008)
├─ T010–T013 Create admin (can run in parallel, depends on T009)
├─ T014 Register admin (depends on T010–T013)
└─ T015–T018 Create serializers (can run in parallel, depends on T005–T008)

Phase 3 (US1: Core Chatbot)
├─ T020–T024 Create views (can run in parallel, depends on T009)
├─ T025 RAG integration (depends on T020, T008)
├─ T026 URL routing (depends on T020–T025)
├─ T027–T031 Vue widget (can run in parallel, depends on T026)

Phase 4 (US2: FAQ & Fallback)
├─ T032–T034 FAQ matching & UI (depends on T020, T027)
└─ T035 FAQ tests (depends on T032)

Phase 5 (US3: Persistence)
├─ T036–T040 Persistence & UX features (depend on T027)

Phase 6 (Testing & Polish)
├─ T041–T050 All tests (depend on Phase 3+)
├─ T051 Test suite (depends on T041–T050)
└─ T052–T057 Final polish (depend on Phase 3–5)
```

---

## Parallel Execution Examples

**Day 1-2 (Phase 1)**:
- Dev A: T001, T002, T003, T004 (sequential, quick)

**Day 3-5 (Phase 2)**: Parallelize T005–T008 and T010–T013
- Dev A: T005–T008 (models) → T009 (migration) → T010–T011 (Conversation/Message Admin)
- Dev B: T015–T017 (serializers, can start after T005–T008 complete)
- Dev C: T012–T013 (FAQ/ChatConfig Admin, can start after T010 complete)

**Day 6-10 (Phase 3)**: Parallelize T020–T024 and T027–T031
- Dev A: T020, T025, T026 (views + routing)
- Dev B: T027–T028 (Vue component + template)
- Dev C: T029–T031 (styling, integration, persistence)
- Merge: T026 into main views when T027 ready

**Day 11-16 (Phases 4-5)**: Sequential or with minimal overlap
- Dev A: T032–T035 (FAQ logic)
- Dev B: T036–T040 (Persistence features)

**Day 17-20 (Phase 6)**: Parallelize T041–T050
- Dev A: T041–T044 (model tests)
- Dev B: T045–T048 (view tests)
- Dev C: T049–T050 (UI tests)
- Dev A/B: T051, T052–T057 (final checks)

---

## Task Summary

| Phase | Count | Focus | Duration (Days) |
|-------|-------|-------|-----------------|
| Phase 1 | 4 | Setup | 1-2 |
| Phase 2 | 15 | Models, serializers, admin | 3-5 |
| Phase 3 (US1) | 12 | Core widget, endpoints, FAQs | 6-10 |
| Phase 4 (US2) | 4 | FAQ selection, fallback | 11-13 |
| Phase 5 (US3) | 5 | Persistence, UX | 14-16 |
| Phase 6 | 17 | Testing, quality, documentation | 17-20 |
| **Total** | **57** | **Full MVP** | **20 days** |

---

## MVP Scope Recommendation

**Recommended MVP (Phase 1-3, 31 tasks, ~10 days)**:
- ✅ Setup and initialization
- ✅ All models and admin interface
- ✅ Core message sending and FAQ-based responses
- ✅ Vue widget with basic UI and AJAX polling
- ✅ Feedback submission to RAG API
- ⏳ Fallback/graceful error handling (defer or minimal)
- ⏳ Persistence & UX features (defer to Phase 2)
- ⏳ Comprehensive testing (defer or smoke tests only)

This delivers a working chatbot that customers can use immediately. Phases 4-6 enhance and stabilize the feature.

---

## Testing Strategy

**MVP (Phase 1-3)**: Minimal
- 5-10 smoke tests (Playwright): Widget opens, message sends, bot responds
- 3-5 integration tests (pytest): Message endpoint, FAQ list, config

**Phase 4-5**: Incremental
- Unit tests for models and utilities
- Integration tests for fallback, persistence

**Phase 6**: Complete
- Full test suite with ≥85% coverage
- All edge cases, error paths, security scenarios

---

## Success Criteria

- [ ] All 57 tasks completed in order (or as dependencies allow)
- [ ] MVP (31 tasks, Phases 1-3) delivered in ~10 days
- [ ] All tests passing: `pytest chatbot/ --cov=chatbot --cov-min=85`
- [ ] Linting clean: `black`, `ruff`, `mypy` pass
- [ ] Widget loads, sends messages, receives responses, submits feedback
- [ ] Feature branch merged to main, deployed to staging/production
- [ ] Stakeholder sign-off on UX and branding alignment

---

## Next Steps

1. **Assign tasks**: Distribute Phase 1-3 tasks among team (parallelization opportunities noted)
2. **Set up tracking**: Link tasks to GitHub Issues or project board
3. **Daily standups**: Sync on blockers, dependency completions
4. **Merge strategy**: PR each task group (T001–T004, T005–T019, etc.)
5. **Deployment**: Deploy MVP to staging after Phase 3, gather feedback, proceed to Phase 4-6

---

<!-- Generated by speckit.tasks.prompt.md on 2025-11-11 -->
