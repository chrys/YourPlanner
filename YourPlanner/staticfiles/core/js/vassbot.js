const { createApp, ref, onMounted, onUnmounted, shallowRef } = Vue;

    // CHANGED: Helper function to get CSRF token from data attribute or cookie
    function getCsrfToken() {
      // CHANGED: First try to get token from data attribute (set by Django template)
      const tokenFromData = document.querySelector('#vasbot-app')?.dataset.csrfToken;
      if (tokenFromData) {
        console.log('[VasBot] CSRF token retrieved from data attribute');
        return tokenFromData;
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
            break;
          }
        }
      }
      // CHANGED: Added debugging for CSRF token
      console.log('[VasBot] CSRF token retrieved:', { length: cookieValue?.length, value: cookieValue?.substring(0, 20) + '...' });
      return cookieValue;
    }

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
    
    // CHANGED: Save to window for debugging
    window.__vasbot_state.isOpen = isOpen;
    window.__vasbot_state.messages = messages;
    window.__vasbot_state.faqs = faqs;

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
        // CHANGED: Added debug logging
        console.log('[VasBot] Initializing widget...');

        // Fetch config
        try {
          const configRes = await fetch(`${apiBaseUrl}/config/`);
          if (!configRes.ok) {
            console.error('[VasBot] Config fetch failed:', configRes.status);
          }
          const config = await configRes.json();
          pollingInterval.value = config.polling_interval_ms;
          console.log('[VasBot] Config loaded:', config);
        } catch (e) {
          console.error('[VasBot] Error loading config:', e);
        }

        // Fetch active conversations
        try {
          const convsRes = await fetch(`${apiBaseUrl}/conversations/?status=active&limit=1`, {
            credentials: 'same-origin'  // CHANGED: Include cookies for authentication
          });
          if (!convsRes.ok) {
            console.error('[VasBot] Conversations fetch failed:', convsRes.status);
          }
          const conversations = await convsRes.json();
          console.log('[VasBot] Conversations loaded:', conversations);

          if (conversations && conversations.length > 0) {
            currentConversationId.value = conversations[0].id;
            await loadMessages();
            startPolling();
          } else {
            console.log('[VasBot] No existing conversations');
            messages.value = []; // CHANGED: Explicitly set empty messages
          }
        } catch (e) {
          console.error('[VasBot] Error loading conversations:', e);
        }

        // CHANGED: Removed FAQ fetching on widget open
      } catch (error) {
        console.error('[VasBot] Initialization error:', error);
      }
    }

    // Load messages for current conversation
    async function loadMessages() {
      if (!currentConversationId.value) return;

      try {
        const res = await fetch(
          `${apiBaseUrl}/conversations/${currentConversationId.value}/messages/?limit=50`,
          {
            credentials: 'same-origin'  // CHANGED: Include cookies for authentication
          }
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

      console.log('[VasBot] Sending message:', text);
      inputText.value = '';
      isLoading.value = true;

      try {
        console.log('[VasBot] POST to:', `${apiBaseUrl}/messages/`);
        const csrfToken = getCsrfToken();
        console.log('[VasBot] CSRF token:', csrfToken ? 'found' : 'not found');
        
        const res = await fetch(`${apiBaseUrl}/messages/`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken || ''  // CHANGED: Add CSRF token
          },
          credentials: 'same-origin',  // CHANGED: Include cookies for authentication
          body: JSON.stringify({
            conversation_id: currentConversationId.value || null,
            text: text.trim()
          })
        });

        console.log('[VasBot] Response status:', res.status);
        
        if (!res.ok) {
          console.error('[VasBot] Request failed:', res.status, res.statusText);
          const errorData = await res.json();
          console.error('[VasBot] Error response:', errorData);
          isLoading.value = false;
          return;
        }

        const botMessage = await res.json();
        console.log('[VasBot] Bot message received:', botMessage);

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
        
        console.log('[VasBot] Messages updated. Total:', messages.value.length);
        console.log('[VasBot] All messages:', messages.value);

        // Scroll to bottom
        setTimeout(() => {
          const messagesEl = document.querySelector('.vasbot-messages');
          if (messagesEl) {
            messagesEl.scrollTop = messagesEl.scrollHeight;
          }
        }, 100);

      } catch (error) {
        console.error('[VasBot] Error sending message:', error);
        console.error('[VasBot] Error stack:', error.stack);
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
            'X-CSRFToken': csrfToken || ''  // CHANGED: Add CSRF token
          },
          credentials: 'same-origin',  // CHANGED: Include cookies for authentication
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

    // CHANGED: Added fetchFaqs function to load FAQs on demand
    async function fetchFaqs() {
      try {
        // CHANGED: Set loading state and clear error
        faqsLoading.value = true;
        faqsError.value = null;
        
        const faqsRes = await fetch(`${apiBaseUrl}/faqs/`);
        // CHANGED: Added response validation before parsing JSON
        if (!faqsRes.ok) {
          throw new Error(`HTTP ${faqsRes.status}`);
        }
        const rawData = await faqsRes.json();
        
        console.log('[VasBot] Raw FAQ data received');
        
        // CHANGED: Detailed inspection of raw data
        if (Array.isArray(rawData)) {
          rawData.forEach((faq, idx) => {
            console.log(`[VasBot] FAQ ${idx}:`, {
              id: faq.id,
              questionLen: (faq.question || '').length,
              answerLen: (faq.answer || '').length,
              questionChars: Array.from(faq.question || '').map(c => `${c}(${ord(c)})`)
            });
          });
        }
        
        // CHANGED: Sanitize FAQ data - remove control characters
        const sanitized = (Array.isArray(rawData) ? rawData : []).map((faq, idx) => {
          const q = (faq.question || '').replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '').trim();
          const a = (faq.answer || '').replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '').trim();
          
          console.log(`[VasBot] FAQ ${idx} after sanitization:`, {
            question: q,
            answer: a.substring(0, 50) + '...'
          });
          
          return { ...faq, question: q, answer: a };
        });
        
        console.log('[VasBot] Sanitized FAQ data, count:', sanitized.length);
        
        // CHANGED: Inspect each item before assignment
        console.log('[VasBot] Detailed inspection before assignment:');
        sanitized.forEach((faq, idx) => {
          // Check for invalid characters
          const hasInvalid = /[\x00-\x08\x0B\x0C\x0E-\x1F]/.test(faq.question + faq.answer);
          console.log(`[VasBot] FAQ ${idx} - hasInvalid: ${hasInvalid}, Q:"${faq.question}", A:"${faq.answer.substring(0,30)}..."`);
        });
        
      // CHANGED: Try assignment with try-catch
      console.log('[VasBot] About to assign to faqs.value');
      try {
        faqs.value = sanitized;
        console.log('[VasBot] FAQs assigned successfully');
        
        // CHANGED: Use manual rendering instead of Vue template
        console.log('[VasBot] Attempting manual FAQ rendering');
        renderFaqsManually();
      } catch (assignError) {
        console.error('[VasBot] Error during assignment:', assignError);
        console.error('[VasBot] Assignment error message:', assignError.message);
        throw assignError;
      }        // CHANGED: Reset to show limited FAQs (not all)
        showAllFaqs.value = false;
        console.log('[VasBot] FAQs loaded successfully');
      } catch (error) {
        console.error('[VasBot] Failed to fetch FAQs:', error);
        console.error('[VasBot] Error message:', error.message);
        console.error('[VasBot] Full error object:', error);
        // CHANGED: Set error message for user feedback
        faqsError.value = error.message || 'Failed to load FAQs';
      } finally {
        // CHANGED: Always clear loading state
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
      
      console.log('[VasBot] Manual FAQ rendering complete');
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
      // CHANGED: Added debug data for troubleshooting
      apiBaseUrl,
      currentConversationId,
    };
  }
// CHANGED: Mount to DOM element if it exists
}).mount(document.querySelector('#vasbot-app') || document.body);

// CHANGED: Global debug function - improved to test both API and component state
window.debugVasBot = async function() {
  console.log('%c=== VasBot Complete Debug Info ===', 'color: blue; font-weight: bold; font-size: 14px;');
  
  // Check if state was saved
  console.log('%c--- Component State ---', 'color: purple; font-weight: bold;');
  if (window.__vasbot_state && window.__vasbot_state.faqs) {
    console.log('FAQs ref object:', window.__vasbot_state.faqs);
    console.log('FAQs value:', window.__vasbot_state.faqs.value);
    console.log('FAQs length:', window.__vasbot_state.faqs.value ? window.__vasbot_state.faqs.value.length : 0);
    if (window.__vasbot_state.faqs.value && window.__vasbot_state.faqs.value.length > 0) {
      console.log('First FAQ:', window.__vasbot_state.faqs.value[0]);
    }
  } else {
    console.log('State not found - component may not be initialized yet');
  }
  
  // Test 1: API endpoint
  console.log('%c--- Testing API Endpoint ---', 'color: green; font-weight: bold;');
  try {
    const res = await fetch('/api/chatbot/faqs/');
    console.log(`Status: ${res.status}`);
    const apiData = await res.json();
    console.log('API returned count:', apiData.length);
    if (apiData.length > 0) {
      console.log('First FAQ from API:', apiData[0]);
      console.log('First FAQ question field:', apiData[0].question);
    }
  } catch (e) {
    console.error('API Error:', e);
  }
  
  // Test 2: Direct DOM inspection
  console.log('%c--- DOM Inspection ---', 'color: blue; font-weight: bold;');
  const buttons = document.querySelectorAll('.vasbot-faq-btn');
  console.log(`Found ${buttons.length} FAQ buttons in DOM`);
  if (buttons.length > 0) {
    buttons.forEach((btn, i) => {
      console.log(`Button ${i}:`);
      console.log(`  - text: "${btn.textContent}"`);
      console.log(`  - title: "${btn.title}"`);
      console.log(`  - innerHTML: "${btn.innerHTML}"`);
      console.log(`  - has children: ${btn.children.length}`);
      if (btn.children.length > 0) {
        console.log(`  - first child: ${btn.children[0].tagName}, text: "${btn.children[0].textContent}"`);
      }
    });
  }
};

console.log('%c[VasBot] Run window.debugVasBot() in console for full diagnostic info', 'color: green;');
