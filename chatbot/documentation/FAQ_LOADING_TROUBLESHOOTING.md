# FAQ Loading Troubleshooting & Fixes

## Issue

FAQ questions were not displaying in the VasiliasBot widget despite being:
1. ✅ Loaded in the database (10 FAQs exist)
2. ✅ Accessible via API (`/api/chatbot/faqs/` returns 200 OK with full JSON)
3. ✅ Properly serialized

## Root Causes Identified

### 1. **Silent JavaScript Errors** (Most Likely)
   - The Vue.js fetch calls might fail silently without proper error handling
   - Errors in one request could block FAQs from loading
   - Original code had minimal error handling

### 2. **Race Condition / Timing Issue**
   - FAQs might load after the template renders
   - Vue might need explicit state initialization

### 3. **Incomplete Error Information**
   - No way to debug from the frontend console
   - No visibility into what was actually happening

## Changes Made to Fix

### 1. Enhanced Error Handling in JavaScript (`vassbot.js`)

**CHANGED:** Wrapped each fetch call in a try-catch block with detailed logging:

```javascript
// BEFORE: Single catch-all that swallows errors
try {
  const faqsRes = await fetch(`${apiBaseUrl}/faqs/`);
  faqs.value = await faqsRes.json();
} catch (error) {
  console.error('Failed to initialize widget:', error);
}

// AFTER: Granular error handling for each endpoint
try {
  const faqsRes = await fetch(`${apiBaseUrl}/faqs/`);
  if (!faqsRes.ok) {
    console.error('[VasBot] FAQs fetch failed:', faqsRes.status);
    return;
  }
  const faqData = await faqsRes.json();
  
  if (Array.isArray(faqData)) {
    faqs.value = faqData;
    console.log('[VasBot] FAQs set successfully:', faqs.value);
  } else {
    console.error('[VasBot] FAQs data is not an array:', faqData);
  }
} catch (e) {
  console.error('[VasBot] Error loading FAQs:', e);
}
```

### 2. Added Comprehensive Debug Logging (`vassbot.js`)

**CHANGED:** Added console logs at each step:
- Config load status
- Conversation list status
- FAQ fetch status with count
- Data validation
- Vue state updates

**Added Global Debug Function:**
```javascript
window.debugVasBot()  // Call in browser console to troubleshoot
```

This function directly fetches FAQs and logs the response without Vue.

### 3. Improved Template Feedback (`_vassbot_widget.html`)

**CHANGED:** Added loading states and debug info:

```html
<div v-if="faqs.length === 0" style="...">
  Loading questions...
</div>
<div v-else-if="faqs.length > 0" style="...">
  {{ faqs.length }} question(s) available
</div>
```

This shows:
- "Loading questions..." while FAQs are being fetched
- "10 question(s) available" once loaded
- Then displays all FAQ buttons

### 4. Backend Logging (`views.py`)

**CHANGED:** Added logging to FAQ endpoint:

```python
@api_view(['GET'])
def faq_list_view(request):
    faqs = FAQ.objects.filter(is_active=True).order_by('order')
    logger.info(f'[VasBot] FAQ list view called. Found {faqs.count()} active FAQs')
    serializer = FAQSerializer(faqs, many=True)
    logger.info(f'[VasBot] Serialized {len(serializer.data)} FAQs')
    return Response(serializer.data)
```

### 5. Explicit State Initialization (`vassbot.js`)

**CHANGED:** Explicitly set empty messages when no conversation exists:

```javascript
if (conversations && conversations.length > 0) {
  // Load existing conversation
} else {
  console.log('[VasBot] No existing conversations');
  messages.value = [];  // CHANGED: Explicitly set empty
}
```

## How to Debug Now

### In Browser Console

1. **Quick check - Run the debug function:**
   ```javascript
   window.debugVasBot()
   ```
   This will show you exactly what the API returns.

2. **Monitor initialization:**
   - Open the browser console (F12)
   - Click the chatbot icon
   - Watch for logs starting with `[VasBot]`
   - Look for any error messages

3. **Check FAQs array in Vue:**
   ```javascript
   // In console, after opening widget
   console.log(vm.faqs)  // Should show array of 10 FAQs
   ```

### In Django Logs

Look for logs like:
```
[VasBot] FAQ list view called. Found 10 active FAQs
[VasBot] Serialized 10 FAQs
```

This confirms the backend is working correctly.

### API Testing

```bash
curl http://localhost:8000/api/chatbot/faqs/
```

Should return JSON array with 10 FAQ objects.

## Expected Behavior After Fixes

1. **Widget Opens:**
   - Console shows `[VasBot] Initializing widget...`

2. **Config Loads:**
   - Console shows `[VasBot] Config loaded: {...}`

3. **Conversations Check:**
   - Console shows `[VasBot] Conversations loaded: [...]`
   - Or `[VasBot] No existing conversations`

4. **FAQs Load:**
   - Console shows `[VasBot] FAQs fetched: [...]`
   - Console shows `[VasBot] FAQ count: 10`
   - Console shows `[VasBot] FAQs set successfully`
   - Widget displays: "10 question(s) available"
   - Widget then displays all 10 FAQ buttons

5. **Click FAQ:**
   - Console shows message being sent
   - Message appears in chat
   - Bot should respond with FAQ answer

## Verification Checklist

- [ ] Open browser console (F12)
- [ ] Click chatbot icon
- [ ] Check console for `[VasBot]` logs
- [ ] Verify no errors in console
- [ ] Look for "10 question(s) available" in widget
- [ ] See FAQ buttons with text
- [ ] Click a button, message should send

## If FAQs Still Don't Load

1. **Check browser console:**
   - Run `window.debugVasBot()`
   - Look for any error messages
   - Note the HTTP status code

2. **Check Django logs:**
   - Look for `[VasBot]` entries
   - Verify 10 FAQs are found
   - Check for any exceptions

3. **Test API directly:**
   ```bash
   curl http://localhost:8000/api/chatbot/faqs/
   ```
   - Should return 10 objects
   - Each with `id`, `question`, `answer`, `order`

4. **Check Vue.js is loaded:**
   - In console: `typeof Vue` should be `'object'`
   - In console: `typeof Vue.createApp` should be `'function'`

5. **Check scripts are loaded:**
   - In browser DevTools Network tab
   - Look for `vassbot.js` (should have 304 Not Modified or 200 OK)
   - Look for `vue.global.js` from unpkg.com

## Files Modified

- **`core/static/core/js/vassbot.js`**
  - Added granular error handling
  - Added detailed logging
  - Added debug function
  - Explicit state initialization

- **`core/templates/core/_vassbot_widget.html`**
  - Added loading state display
  - Added debug info display
  - Better user feedback

- **`chatbot/views.py`**
  - Added logging to FAQ endpoint
  - Added logger import

## Files NOT Changed

- `chatbot/models.py` - FAQ model is correct
- `chatbot/serializers.py` - FAQSerializer is correct
- `chatbot/api_urls.py` - Routes are correct
- `chatbot/admin.py` - Admin is configured

## Next Steps

1. **Clear browser cache** (Ctrl+F5 or Cmd+Shift+R)
2. **Reload page**
3. **Open browser console**
4. **Click chatbot icon**
5. **Monitor logs and debug**
6. **Report any errors you see**

---

**Date:** 2025-11-12  
**Status:** Debugging enhancements applied - awaiting verification  
**Next:** Monitor console logs to identify specific failure point
