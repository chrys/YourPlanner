// CHANGED: Destructure from Vue and check if an app is already being mounted
const { createApp, ref, onMounted, onUnmounted, shallowRef } = Vue;

// CHANGED: Check if vasbot-app element exists before creating the app
if (document.getElementById('vasbot-app')) {
  createApp({
  setup() {
    const isOpen = ref(false);
    const isLoading = ref(false);
    const inputText = ref('');
    const messages = ref([]);
    const faqs = shallowRef([]);  // CHANGED: Use shallowRef instead of ref to avoid deep reactivity tracking
    const currentConversationId = ref(null);
    const pollingInterval = ref(2500);
    let pollTimer = null;

    // CHANGED: Added missing reactive variables for FAQ state
    const faqsLoading = ref(false);
    const faqsError = ref(null);
    const showAllFaqs = ref(false);

    const apiBaseUrl = '/api/chatbot';

    // CHANGED: Helper function to get CSRF token from hidden input
    function getCsrfToken() {
      // CHANGED: Get token from Django's hidden CSRF input (from any form on page)
      const csrfInput = document.querySelector('[name="csrfmiddlewaretoken"]');
      if (csrfInput && csrfInput.value) {
        return csrfInput.value;
      }
      
      // Fallback: get from cookie
      const name = 'csrftoken';
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            return cookieValue;
          }
        }
      }
      
      return null;
    }

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

        // CHANGED: Removed FAQ fetching on widget open
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
        const csrfToken = getCsrfToken();
        
        const res = await fetch(`${apiBaseUrl}/messages/`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken || ''
          },
          credentials: 'same-origin',
          body: JSON.stringify({
            conversation_id: currentConversationId.value || null,
            text: text.trim(),
            csrfmiddlewaretoken: csrfToken
          })
        });

        const botMessage = await res.json();

        // Add user message
        const userMsg = {
          id: `local-${Date.now()}`,
          sender: 'customer',
          text: text,
          timestamp: new Date().toISOString(),
          feedback: null
        };
        messages.value.push(userMsg);

        // Normalize bot message object
        const normalizedBotMsg = {
          id: botMessage.id,
          sender: botMessage.sender || 'bot',
          text: botMessage.text || '',
          timestamp: botMessage.timestamp || new Date().toISOString(),
          conversation_id: botMessage.conversation_id || botMessage.conversation,
          feedback: botMessage.feedback || null
        };
        
        messages.value.push(normalizedBotMsg);
        
        currentConversationId.value = normalizedBotMsg.conversation_id;

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
        const csrfToken = getCsrfToken();
        const res = await fetch(`${apiBaseUrl}/feedback/`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken  // CHANGED: Include CSRF token
          },
          credentials: 'same-origin',  // CHANGED: Include cookies in request
          body: JSON.stringify({ 
            message_id: messageId, 
            value,
            csrfmiddlewaretoken: csrfToken  // CHANGED: Also include in body as fallback
          })
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

    // CHANGED: Added fetchFaqs function to load FAQs on demand
    async function fetchFaqs() {
      try {
        faqsLoading.value = true;
        faqsError.value = null;
        
        const faqsRes = await fetch(`${apiBaseUrl}/faqs/`);
        if (!faqsRes.ok) {
          throw new Error(`HTTP ${faqsRes.status}`);
        }
        const rawData = await faqsRes.json();
        
        // CHANGED: Sanitize FAQ data - remove control characters
        const sanitized = (Array.isArray(rawData) ? rawData : []).map((faq) => ({
          ...faq,
          question: (faq.question || '').replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '').trim(),
          answer: (faq.answer || '').replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '').trim()
        }));
        
        faqs.value = sanitized;
        renderFaqsManually();
        showAllFaqs.value = false;
      } catch (error) {
        console.error('Failed to fetch FAQs:', error);
        faqsError.value = error.message || 'Failed to load FAQs';
      } finally {
        faqsLoading.value = false;
      }
    }
    
    // CHANGED: Helper function to get character code
    function ord(char) {
      return char.charCodeAt(0);
    }
    
    // CHANGED: Manual FAQ rendering to bypass Vue reactivity issues
    function renderFaqsManually() {
      const container = document.querySelector('.vasbot-faqs');
      if (!container) {
        console.log('[VasBot] FAQ container not found');
        return;
      }
      
      // Clear existing FAQ buttons (but keep header and loading)
      const existingButtons = container.querySelectorAll('.vasbot-faq-btn, .vasbot-faq-toggle');
      existingButtons.forEach(btn => btn.remove());
      
      const faqList = faqs.value || [];
      if (faqList.length === 0) {
        console.log('[VasBot] No FAQs to render');
        return;
      }
      
      // Determine how many to show
      const displayCount = showAllFaqs.value ? faqList.length : Math.min(3, faqList.length);
      const displayFaqs = faqList.slice(0, displayCount);
      
      console.log(`[VasBot] Rendering ${displayCount} FAQs manually`);
      
      // Find insertion point (after loading/error message if present)
      const loadingDiv = container.querySelector('.vasbot-faq-status');
      const insertAfter = loadingDiv || container.querySelector('p');
      
      // Create and insert FAQ buttons
      displayFaqs.forEach((faq, idx) => {
        const btn = document.createElement('button');
        btn.className = 'vasbot-faq-btn';
        btn.textContent = faq.question;
        btn.addEventListener('click', () => {
          console.log(`[VasBot] FAQ clicked: ${faq.question}`);
          sendMessage(faq.question);
        });
        
        if (insertAfter) {
          insertAfter.parentNode.insertBefore(btn, insertAfter.nextSibling);
        } else {
          container.appendChild(btn);
        }
      });
      
      // Add "Show more/less" button if needed
      if (faqList.length > 3) {
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'vasbot-faq-toggle';
        toggleBtn.textContent = showAllFaqs.value ? 'Show fewer' : 'Show more';
        toggleBtn.addEventListener('click', () => {
          showAllFaqs.value = !showAllFaqs.value;
          renderFaqsManually();
        });
        container.appendChild(toggleBtn);
      }
    }

    return {
      isOpen,
      isLoading,
      inputText,
      messages,
      faqs,
      // CHANGED: Added missing reactive variables to return
      faqsLoading,
      faqsError,
      showAllFaqs,
      toggleWidget,
      sendMessage,
      submitFeedback,
      downloadTranscript,
      fetchFaqs,
    };
  }
  // CHANGED: Mount to DOM element if it exists
  }).mount(document.querySelector('#vasbot-app') || document.body);
}
