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
