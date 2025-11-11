# Feature Specification: Customer Chatbot MVP (VasiliasBot)

**Feature Branch**: `[customer-chatbot-mvp]`  
**Created**: [2024-06-09]  
**Status**: Draft  
**Input**: User description: "I want my django website to have a chatbot. The chatbot should be available to all signed in Customers. The objective is to provide customer support by answering questions based on a RAG application. The RAG application is out of the scope of this development. Django will integrate with the RAG application through an API. The Chatbot should have a thumbs up/thumbs down after each reply. Thumbs up will be used as a KPI to measure success and thumbs down will be used to log replies. Again, logging of replies will be used by an external RAG application through an API. The chatbot will be user-initiated as a small, non-intrusive icon in the bottom-right corner. The widget's colors, fonts, and icon should match the website's design. The chatbot will be called VasiliasBot. It should also have an option to answer FAQ questions - design appropriate UI for the Customer to choose a question. The conversation should persist as the user navigates between pages. An interaction element should be a typing indicator (...) to show the bot is 'thinking.' Another interaction element should be a clear way for the user to close the chat or request a transcript. Fallback / Error Handling: A graceful response when it doesn't understand a query (e.g., 'I'm sorry, I'm not sure how to help with that. Would you like to rephrase? If not, you can always send an email to your wedding planner. The frontend JavaScript sends messages to a Django view. Django acts as a middleware, forwarding the message to an API that is defined in Admin. Use Vue for the chat widget. Use AJAX polling instead of WebSockets to simplify initial setup. Integrate with a RAG application through an API using FastAPI. API endpoints should be defined in admin. Existing databases will be used. sqlite3 for development and postgres for production. We will implement the MVP only now.'

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Customer can open and use VasiliasBot (Priority: P1)

A signed-in Customer sees a chatbot icon in the bottom-right corner. Clicking it opens the VasiliasBot chat widget, styled to match the site. The Customer can type a question or select from a list of FAQs. The bot responds with an answer, and the Customer can give thumbs up/down feedback on each reply.

**Why this priority**: This is the core value proposition—providing instant support to Customers via a branded, accessible chatbot.

**Independent Test**: Can be fully tested by logging in as a Customer, opening the chat, asking a question, and receiving a response with feedback options.

**Acceptance Scenarios**:

1. **Given** a signed-in Customer, **When** they click the chatbot icon, **Then** the VasiliasBot widget opens and is styled to match the site.
2. **Given** the chat widget is open, **When** the Customer asks a question or selects an FAQ, **Then** the bot responds and feedback options are shown.

---

### User Story 2 - FAQ selection and fallback (Priority: P2)

The Customer can view and select from a list of FAQs. If the bot cannot answer a question, it gracefully responds with a fallback message and suggests rephrasing or contacting support.

**Why this priority**: Ensures the bot is useful even if the RAG API is unavailable or the question is out of scope.

**Independent Test**: Can be tested by selecting an FAQ and by asking an unanswerable question.

**Acceptance Scenarios**:

1. **Given** the chat widget is open, **When** the Customer selects an FAQ, **Then** the bot provides the answer.
2. **Given** the Customer asks an unanswerable question, **When** the bot cannot answer, **Then** a fallback message is shown with next steps.

---

### User Story 3 - Conversation persistence and UI feedback (Priority: P3)

The conversation persists as the Customer navigates between pages. The widget shows a typing indicator when the bot is processing, and provides clear options to close the chat or request a transcript.

**Why this priority**: Improves user experience and trust by making the chat feel continuous and interactive.

**Independent Test**: Can be tested by chatting, navigating to another page, and confirming the conversation is still present.

**Acceptance Scenarios**:

1. **Given** an ongoing chat, **When** the Customer navigates to another page, **Then** the conversation history remains.
2. **Given** the bot is processing, **When** the Customer is waiting, **Then** a typing indicator is shown.
3. **Given** the chat widget is open, **When** the Customer clicks close or request transcript, **Then** the appropriate action occurs.

---

## Functional Requirements

- The chatbot (VasiliasBot) is available to all signed-in Customers as a floating icon in the bottom-right corner.
- The chat widget is built with Vue.js 3 and styled to match the website (colors, fonts, icon).
- The widget supports both free-text questions and FAQ selection.
- Each bot reply includes thumbs up/down feedback; thumbs up is logged as KPI, thumbs down is logged for review (API integration for logging).
- The frontend uses AJAX polling to communicate with a Django view (no WebSockets in MVP).
- Django acts as middleware, forwarding messages to a RAG API endpoint (configurable in Admin, FastAPI-based, out of scope).
- FAQ content and RAG API endpoint are editable in Django Admin.
- Conversation persists as the user navigates between pages (localStorage or session).
- Typing indicator is shown while waiting for a response.
- Widget provides clear controls to close chat and request transcript.
- Fallback message is shown if the bot cannot answer or on error.
- Uses existing databases: sqlite3 (dev), postgres (prod).

## Non-Functional Requirements

- Widget must be non-intrusive and performant.
- All user interactions are secure and respect authentication.
- Branding is consistent with the rest of the site.
- Error handling is user-friendly and logs issues for review.

## Out of Scope

- RAG API implementation (assume endpoint exists)
- WebSockets (reserved for future phase)
- Admin analytics dashboard (future phase)
- Integration with external CRM/helpdesk (future phase)


## Clarifications

- Q: Should we explicitly define the core data entities (e.g., Message, Feedback, FAQ) and their key attributes? → A: Explicitly define the main data entities (Message, Feedback, FAQ, etc.) and their key fields.
- Q: Do we need a model for chat history (Conversation)? → A: Yes, add a Conversation entity to group messages and enable history per user/session.

## Data Model


**Entities:**

- **Conversation**: Represents a chat session/history for a user.
	- Fields: id (UUID), user (FK to Customer, nullable for anonymous), started_at (datetime), ended_at (datetime, nullable), status (enum: active/closed), metadata (JSON, optional)
- **Message**: Represents a single chat message.
	- Fields: id (UUID), conversation (FK to Conversation), user (FK to Customer), text (string), timestamp (datetime), sender (enum: customer/bot)
- **Feedback**: Represents thumbs up/down on a bot reply.
	- Fields: id (UUID), message (FK to Message), user (FK to Customer), value (enum: up/down), timestamp (datetime)
- **FAQ**: Represents a frequently asked question/answer pair.
	- Fields: id (UUID), question (string), answer (string), order (int), is_active (bool)

**Identity & Uniqueness:**
- Conversation, Message, and Feedback use UUIDs for uniqueness.
- FAQ uniqueness by question text.

**Relationships:**
- Conversation has many Messages.
- Message belongs to a Conversation and a Customer.
- Feedback is linked to a Message and a Customer.
- FAQ is standalone but referenced in UI.

**Lifecycle/State:**
- Message: created on send/receive, immutable after creation.
- Feedback: created per reply, can be updated by user (one per user per message).
- FAQ: managed in Admin, can be activated/deactivated.

**Data Volume/Scale:**
- MVP expects low to moderate volume (single-digit messages per user per session, <1000 FAQs, <10k feedbacks in dev).

## Open Questions

- Should transcript requests be emailed or just downloaded?
- Should feedback logging be visible in Django Admin or only sent to the RAG API?

---

<!-- Changes: Initial MVP spec for VasiliasBot chatbot. -->
