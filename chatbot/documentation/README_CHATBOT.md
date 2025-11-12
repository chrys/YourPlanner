# Chatbot App

This Django app provides a customer-facing chatbot for the YourPlanner website.

## Features

- **FAQ-based anwsering:** The chatbot can answer customer questions based on a predefined list of frequently asked questions.
- **Fuzzy String Matching:** The chatbot uses fuzzy string matching to find the most relevant FAQ answer, even if the customer's question is not phrased exactly as it is in the FAQ.
- **Fallback Mechanism:** If the chatbot cannot find a relevant FAQ answer, it will provide a fallback message to the customer.
- **Conversation Persistence:** The chatbot will remember the customer's conversation, even if they navigate to a different page or close the chat widget.
- **Typing Indicator:** The chatbot will display a typing indicator to let the customer know that it is processing their message.
- **Interactive Feedback:** The chatbot will provide interactive feedback to the customer, such as thumbs up/down buttons on its messages.
- **Transcript Download:** The customer can download a transcript of their conversation with the chatbot.

## API Endpoints

The chatbot provides the following API endpoints:

- `POST /api/chatbot/messages/`: Send a message to the chatbot.
- `GET /api/chatbot/faqs/`: Get a list of frequently asked questions.
- `GET /api/chatbot/conversations/<conversation_id>/messages/`: Get the message history for a conversation.
- `POST /api/chatbot/feedback/`: Submit feedback on a chatbot message.
- `GET /api/chatbot/config/`: Get the chatbot configuration.
- `GET /api/chatbot/conversations/`: Get a list of the customer's active conversations.

## Admin Interface

The chatbot provides the following admin interface:

- **Conversation Admin:** Manage customer conversations.
- **Message Admin:** View customer and chatbot messages.
- **FAQ Admin:** Manage frequently asked questions.
- **ChatConfig Admin:** Manage the chatbot configuration.
