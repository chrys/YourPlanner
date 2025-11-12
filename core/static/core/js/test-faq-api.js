// CHANGED: Simple test to verify FAQ API works
console.log('%c[FAQ-API-Test] Page loaded, testing FAQ API...', 'color: blue; font-weight: bold;');

// CHANGED: Define testFaqApi as simpler non-async function
window.testFaqApi = function() {
  console.log('%c[FAQ-API-Test] === TESTING API ===', 'color: green; font-weight: bold;');
  fetch('/api/chatbot/faqs/')
    .then(response => {
      console.log(`[FAQ-API-Test] HTTP Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      console.log('[FAQ-API-Test] API Response:', data);
      console.log(`[FAQ-API-Test] Data length: ${data.length}`);
      console.log(`[FAQ-API-Test] Data type: ${typeof data}, Is Array: ${Array.isArray(data)}`);
      if (data.length > 0) {
        console.log('[FAQ-API-Test] First FAQ:', data[0]);
        console.log('[FAQ-API-Test] First FAQ question:', data[0].question);
      }
      console.table(data);
    })
    .catch(error => {
      console.error('[FAQ-API-Test] Error:', error);
    });
};

// Run immediately
console.log('[FAQ-API-Test] Running automatic test on page load...');
window.testFaqApi();

