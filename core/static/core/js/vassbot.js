const { createApp, ref, onMounted, onUnmounted } = Vue;

createApp({
  setup() {
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

    // Download transcript
    function downloadTranscript() {
      if (!currentConversationId.value) return;

      let transcript = `Conversation Transcript (ID: ${currentConversationId.value})\\n\\n`;
      messages.value.forEach(message => {
        const date = new Date(message.timestamp).toLocaleTimeString();
        transcript += `[${date}] ${message.sender}: ${message.text}\\n`;
      });

      const blob = new Blob([transcript], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `vasbot-transcript-${currentConversationId.value}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    }

    return {
      isOpen,
      isLoading,
      inputText,
      messages,
      faqs,
      toggleWidget,
      sendMessage,
      submitFeedback,
      downloadTranscript,
    };
  }
}).mount('#vasbot-app');
