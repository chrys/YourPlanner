# Research: VasiliasBot MVP Implementation Decisions

**Date**: 2025-11-11 | **Feature**: Customer Chatbot MVP (VasiliasBot)

## Research Summary

This document consolidates research and technical decisions for the VasiliasBot MVP. All key unknowns from the specification and implementation plan have been resolved.

---

## 1. AJAX Polling vs. WebSockets

### Decision
**AJAX polling** with configurable interval (default 2-3 seconds), stored in `ChatConfig` model for runtime tuning.

### Rationale
- MVP scope explicitly requests AJAX polling (no WebSockets).
- Simpler architecture: no need for Django Channels, WebSocket server, or connection management.
- Easier to debug, test, and monitor.
- Graceful degradation: polling can continue even if network is unstable.
- Cost-effective: single Django process can serve many customers without socket overhead.

### Alternatives Considered
- **WebSockets** (Phase 2): Requires Django Channels, Redis message broker; adds complexity not justified for MVP.
- **Server-Sent Events (SSE)**: Unidirectional; doesn't support customer message sending well.
- **GraphQL subscriptions**: Overkill; requires GraphQL setup.

### Implementation Notes
- Use Fetch API (modern, no jQuery dependency).
- Poll only when chat widget is open (pause on minimize to save bandwidth).
- Exponential backoff on error (max 10 seconds).
- Store poll interval in `ChatConfig.polling_interval_ms` (default 2500ms).
- Admin can adjust interval per environment.

---

## 2. Vue.js 3 Integration with Django

### Decision
**Vue.js 3** with single-file components (SFC), loaded via CDN or bundled; initialize from Django template with customer ID and conversation ID.

### Rationale
- Project already uses Bootstrap 5; Vue.js 3 integrates seamlessly.
- SFC syntax (`<template>`, `<script setup>`, `<style scoped>`) is modern and maintainable.
- No build step required if using CDN (faster MVP deployment).
- Optional: Add vite/webpack later (Phase 2) for optimization.

### Alternatives Considered
- **React**: Different from project stack (already Vue).
- **Alpine.js**: Too minimal for complex chat UI (history, feedback, typing indicator).
- **Plain JavaScript**: Would require manual state management (Vue is cleaner).
- **Svelte**: Not in project stack; steeper learning curve.

### Implementation Notes
- Create `VasiliasBot.vue` single-file component in `core/static/core/js/`.
- Initialize via `<script>` tag in base template with inline config object.
- Component handles:
  - Widget toggle (open/close icon)
  - Message input and send
  - Message history display
  - Typing indicator
  - Feedback submission
  - Fallback message display
- Use axios or Fetch API for AJAX calls to Django endpoints.
- Props: `apiBaseUrl`, `customerId`, `conversationId`.

---

## 3. Conversation History Persistence

### Decision
**Hybrid approach**: localStorage for client-side cache (instant display on reload), server-side DB for source of truth.

### Rationale
- UX: Customer opens chat, history appears instantly (no spinner waiting for server).
- Data integrity: Reload from server on page load to ensure sync.
- Privacy: Server-side storage allows admin oversight; localStorage is client-only.
- Scalability: localStorage limited to ~5-10MB; server DB unlimited.

### Alternatives Considered
- **localStorage only**: Lost on browser clear; no admin visibility.
- **sessionStorage only**: Lost on browser close; degraded UX.
- **IndexedDB**: More complex; not needed for MVP chat history size.
- **Server-side session only**: Slower initial display; worse perceived UX.

### Implementation Notes
- On widget init: Check localStorage for recent conversation; fetch server state.
- On new message sent: Write to localStorage immediately; server confirms and updates DB.
- On browser reload: Fetch full conversation from server; sync with localStorage.
- Clear localStorage on logout (Django handles via template context).
- `Conversation` model includes `customer` FK; only authenticated users can access their own.

---

## 4. RAG API Integration Pattern

### Decision
**Django as middleware**: Django view receives message, forwards to RAG API (FastAPI, out of scope), stores request/response, returns to Vue client.

### Rationale
- Decouples frontend from external RAG API (no direct CORS calls).
- Hides RAG API URL and auth key from client (security).
- Allows logging, monitoring, and rate limiting in Django.
- Fallback handling: Django can serve FAQ or fallback message if RAG API fails.
- Configuration in Admin: `ChatConfig.rag_api_url`, `ChatConfig.rag_api_key`.

### Alternatives Considered
- **Direct client → RAG API**: Breaks CORS security; exposes API key.
- **WebSocket relay**: Unnecessary complexity for MVP.
- **Message queue (Celery)**: Adds async latency; MVP requires synchronous response.

### Implementation Notes
- Create `ChatConfig` model (singleton, enforced via custom manager).
- Django endpoint `/api/chatbot/messages/`:
  1. Receive customer message.
  2. Store in `Message` model (sender=customer).
  3. Check if message matches FAQ (simple substring or exact match).
  4. If match, return FAQ answer; else call RAG API.
  5. On RAG API error, return fallback message.
  6. Store bot response in `Message` model (sender=bot).
  7. Return to client with message ID.
- Timeout: 10 seconds (prevent hanging requests).
- Logging: Django structured log with request ID, latency, RAG API response status.

---

## 5. Feedback Logging & KPI Tracking

### Decision
**Send to RAG API directly (MVP)**. Feedback (thumbs up/down) is forwarded to the RAG API endpoint for logging and analysis. No local storage of feedback in MVP.

### Rationale
- RAG API owns feedback data: Feedback is the RAG framework's responsibility for analysis, retraining, and KPI tracking.
- Simplifies MVP: Eliminates Feedback model, migrations, and Admin interface for feedback.
- Real-time: Feedback sent immediately to RAG API; no async complexity.
- Future-proof: RAG API can aggregate and analyze feedback across all customers.

### Alternatives Considered
- **Store in DB then send async**: Adds complexity (Celery, queues); RAG API owns data anyway.
- **No feedback collection**: Defeats the purpose of KPI tracking and model improvement.
- **Store in DB only**: Admin visibility is nice, but RAG API needs the data for retraining.

### Implementation Notes
- No `Feedback` Django model (removed from MVP).
- Feedback submission endpoint: `POST /api/chatbot/feedback/` → calls RAG API directly, returns success/failure.
- RAG API call: Forward `{ message_id, conversation_id, customer_id, value: "up"|"down", timestamp }` to RAG API.
- Error handling: If RAG API feedback endpoint fails, return error to client (don't silently fail).
- Timeout: 5 seconds for RAG API feedback call (faster than chat message endpoint).
- No local logging or audit trail of feedback in YourPlanner DB (RAG API is source of truth).

---

## 6. Widget Styling & Branding

### Decision
**Bootstrap 5 + custom CSS** for consistency with YourPlanner site; color scheme matches site branding.

### Rationale
- YourPlanner already uses Bootstrap 5.
- Minimal additional CSS needed (bottom-right positioning, shadow, animations).
- Easy for admins to customize (CSS variables or theme settings, future).

### Implementation Notes
- Create `vassbot.css` with:
  - Widget container styling (position fixed, bottom-right).
  - Icon styling (chat bubble, size ~40px).
  - Chat window styling (width ~350px, height ~500px, responsive).
  - Message bubble styling (colors, borders, shadows).
  - Input field styling (consistent with Bootstrap form classes).
  - Typing indicator animation (three dots, 0.6s cycle).
- Use CSS custom properties (--primary-color, --text-color) for easy theming.
- Icon: Use Bootstrap icon (`bi-chat-dots`) or custom SVG (wedding-themed).

---

## 7. Error Handling & Fallback Messages

### Decision
**Graceful fallback**: When RAG API unavailable or question unanswerable, show predefined fallback message with suggestions (rephrase, email support).

### Rationale
- User experience: Never show raw error messages.
- Support flow: Suggest email to wedding planner for complex questions.
- Configurable: Fallback message stored in `ChatConfig` for admin tuning.

### Alternatives Considered
- **Silent failure**: Users confused; bad UX.
- **Technical error messages**: Confusing for customers; leaks internals.
- **Hard-coded fallback**: Inflexible; requires code change to update.

### Implementation Notes
- Default fallback: "I'm sorry, I'm not sure how to help with that. Would you like to rephrase? If not, you can always send an email to your wedding planner."
- Store in `ChatConfig.fallback_message` (editable in Admin).
- RAG API timeout or HTTP error (≥500): Return fallback.
- 404 or "no answer" from RAG: Return fallback.
- Fallback message logged separately (no Feedback record for fallbacks).

---

## 8. Accessibility (MVP Scope)

### Decision
**Basic keyboard support + ARIA labels**. Full WCAG 2.1 AA compliance deferred to Phase 2.

### Rationale
- MVP timeline: Basic a11y acceptable per Constitution (justification in plan.md).
- Core features: Keyboard close (Escape key), Tab order in input/buttons, visible focus.
- Phase 2: Add screen reader support, ARIA live regions, full keyboard navigation.

### Alternatives Considered
- **Full WCAG 2.1 AA now**: Delays MVP; can be added incrementally.
- **No a11y**: Excludes disabled users; poor optics; violates Constitution intent.

### Implementation Notes
- Escape key closes widget.
- Tab order: Icon → Input → Send Button → FAQs → Feedback buttons → Close.
- ARIA labels on buttons: `aria-label="Open chat"`, `aria-label="Send message"`.
- Typing indicator: `role="status"` with `aria-live="polite"`.
- Phase 2: Add `aria-expanded`, `role="dialog"`, full keyboard shortcuts.

---

## 9. Testing Strategy

### Decision
- **Unit tests**: Models, serializers, FAQ matching logic.
- **Integration tests**: Chat flow (send message → RAG API mock → response).
- **UI tests (Playwright)**: Open widget, send message, verify feedback options, close.
- **Coverage goal**: ≥85% (models + views), excluding migrations.

### Rationale
- Constitution requires ≥85% coverage.
- Unit tests ensure business logic correctness.
- Integration tests verify API contracts.
- UI tests catch regressions in Vue component and Django endpoints.

### Implementation Notes
- Use `unittest.mock` to mock RAG API calls.
- Fixtures: Create test customer, conversation, messages, FAQs.
- Tests for edge cases: Empty message, RAG timeout, invalid feedback, etc.
- Playwright test: Happy path (login, open chat, send message, feedback).

---

## 10. Deployment & Configuration

### Decision
- **Configuration via Django Admin**: RAG API URL, key, fallback message, polling interval.
- **Environment variables**: RAG API key encrypted in DB; retrieve via `ChatConfig`.
- **Database migrations**: Standard Django migration for models.

### Rationale
- Admin control: Non-developers can tune without code changes.
- Security: API key not in settings.py or VCS.
- Flexibility: Different RAG APIs per environment (dev, staging, prod).

### Implementation Notes
- `ChatConfig` created via data migration (singleton).
- Admin interface for `ChatConfig`, `FAQ`, `Conversation`, `Message`, `Feedback`.
- RAG API key: Use Django's `get_secret_key` utility or environment variable fallback.
- Polling interval: Default 2500ms; adjustable per environment.

---

## Summary Table

| Topic | Decision | Rationale | Phase |
|-------|----------|-----------|-------|
| Communication | AJAX polling | MVP spec; simpler than WebSockets | MVP |
| Frontend | Vue.js 3 SFC | Project stack; modern syntax | MVP |
| History | Hybrid localStorage + DB | UX + data integrity | MVP |
| RAG Integration | Django middleware | Security + decoupling | MVP |
| Feedback | DB storage + optional Phase 2 async | Simple + future-proof | MVP |
| Styling | Bootstrap 5 + custom CSS | Consistent branding | MVP |
| Fallback | Configurable message in Admin | User-friendly + flexible | MVP |
| A11y | Basic keyboard + ARIA | Constitution-compliant MVP scope | MVP |
| Testing | Unit + integration + UI | ≥85% coverage | MVP |
| Config | Django Admin | Non-developer control | MVP |

---

## Unknowns Resolved

✅ All unknowns from specification and plan have been researched and resolved.

---

<!-- Changes: Phase 0 research complete; all technical decisions documented and justified. -->
