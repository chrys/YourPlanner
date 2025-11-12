# VasiliasBot Chatbot FAQ Loading Guide

## Overview

The VasiliasBot chatbot uses a FAQ (Frequently Asked Questions) database to provide quick answers to customers. This guide explains how to load FAQ data into the Django database.

## FAQ Model

The `FAQ` model is defined in `chatbot/models.py` with the following fields:

- `id` (UUID): Unique identifier
- `question` (TextField, unique): The FAQ question
- `answer` (TextField): The FAQ answer
- `order` (IntegerField): Display order (for sorting in UI)
- `is_active` (BooleanField): Whether the FAQ is visible to customers
- `created_at` (DateTimeField): Creation timestamp
- `updated_at` (DateTimeField): Last update timestamp

## Methods to Load FAQ Data

### Method 1: Using the Management Command (Recommended for Development)

The custom management command `load_faq` is the easiest way to load sample FAQ data:

```bash
python manage.py load_faq
```

**Features:**
- Checks if FAQs already exist to prevent duplicates
- Creates 10 sample FAQ entries for a wedding planning business
- Outputs success/error messages
- Safe to run multiple times (won't create duplicates)

**Sample Output:**
```
Successfully created 10 FAQ entries
```

### Method 2: Using Django Fixtures

Load FAQ data from the fixture file:

```bash
python manage.py loaddata chatbot/fixtures/faq.json
```

**Features:**
- Uses JSON fixture file (`chatbot/fixtures/faq.json`)
- Standard Django way to load data
- Useful for reproducible deployments

**Note:** This method may fail if FAQs already exist (depends on fixture syntax).

### Method 3: Django Admin Interface

1. Go to the Django admin: `http://localhost:8000/admin/`
2. Navigate to "Chatbot" → "FAQs"
3. Click "Add FAQ" button
4. Fill in:
   - Question
   - Answer
   - Order (display order)
   - Is active (checkbox)
5. Click "Save"

**Advantages:**
- Manual control
- Can edit/delete FAQs easily
- Visual feedback

### Method 4: Manual Database Insert (Django Shell)

```bash
python manage.py shell
```

Then in the shell:

```python
from chatbot.models import FAQ

# Create a single FAQ
FAQ.objects.create(
    question="What is your company name?",
    answer="We are a professional wedding planning service.",
    order=1,
    is_active=True
)

# Create multiple FAQs
faqs = [
    FAQ(question="Question 1", answer="Answer 1", order=1, is_active=True),
    FAQ(question="Question 2", answer="Answer 2", order=2, is_active=True),
]
FAQ.objects.bulk_create(faqs)

# Verify creation
print(FAQ.objects.count())  # Should show number of FAQs
```

## Sample FAQ Data

The default FAQ data loaded by the management command includes:

1. **What services do you offer?** - Overview of wedding planning services
2. **How far in advance should I book?** - Booking timeline recommendation
3. **What is the typical duration of a ceremony?** - Ceremony length information
4. **Do you offer custom packages?** - Package customization options
5. **What is your cancellation policy?** - Refund and cancellation terms
6. **What payment methods do you accept?** - Payment options
7. **Can you help with destination weddings?** - Destination wedding capability
8. **How many weddings do you handle per year?** - Volume and quality information
9. **Do you provide day-of coordination?** - Coordination services
10. **What is the typical cost of your services?** - Pricing information

## API Endpoint

After loading FAQ data, access it via the REST API:

```bash
# Get all active FAQs
curl http://localhost:8000/api/chatbot/faqs/

# Response example:
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "question": "What services do you offer?",
    "answer": "We offer comprehensive wedding planning services...",
    "order": 1
  },
  ...
]
```

## Troubleshooting

### Command not found: `python manage.py load_faq`

**Solution:** Ensure the management command file exists at:
```
chatbot/management/commands/load_faq.py
```

And that `__init__.py` files exist in:
```
chatbot/management/__init__.py
chatbot/management/commands/__init__.py
```

### FAQs not appearing in admin

**Solution:** 
1. Ensure `FAQ` model is registered in `chatbot/admin.py`
2. Run migrations: `python manage.py migrate chatbot`
3. Reload the admin page

### Duplicate FAQ entries

**Solution:** 
1. Delete duplicates via admin or shell
2. Re-run `python manage.py load_faq` (it checks for existing FAQs)

### UnicodeDecodeError loading fixture

**Solution:** Ensure `faq.json` is saved with UTF-8 encoding.

## Maintenance

### Update an FAQ

```bash
python manage.py shell
```

```python
from chatbot.models import FAQ

faq = FAQ.objects.get(id='550e8400-e29b-41d4-a716-446655440000')
faq.answer = "Updated answer text"
faq.save()
```

### Delete an FAQ

```bash
python manage.py shell
```

```python
from chatbot.models import FAQ

FAQ.objects.filter(question="Question to delete").delete()
```

### Deactivate an FAQ (hide from customers)

```bash
python manage.py shell
```

```python
from chatbot.models import FAQ

faq = FAQ.objects.get(question="Question to hide")
faq.is_active = False
faq.save()
```

### Reorder FAQs

Edit the `order` field in admin or via shell:

```python
from chatbot.models import FAQ

faq = FAQ.objects.get(id='...')
faq.order = 5  # New order
faq.save()
```

## Testing

To verify FAQ loading worked:

1. **Via Django admin:**
   - Go to `/admin/chatbot/faq/`
   - Should see 10 FAQ entries listed

2. **Via Django shell:**
   ```bash
   python manage.py shell
   from chatbot.models import FAQ
   print(FAQ.objects.count())  # Should be 10 (or more)
   ```

3. **Via API:**
   ```bash
   curl http://localhost:8000/api/chatbot/faqs/
   # Should return JSON list of FAQs
   ```

4. **Via Vue.js widget:**
   - Open the chatbot widget
   - FAQs should appear in the initial FAQ list
   - Clicking an FAQ should send it as a question

## Next Steps

After loading FAQs:

1. ✅ Test the chatbot widget with FAQ questions
2. ✅ Verify FAQ matching in the message endpoint
3. ✅ Customize FAQs to match your business content
4. ✅ Monitor FAQ usage metrics (via RAG API feedback)
5. ✅ Iterate and improve FAQ content based on customer interactions

---

**Last Updated:** 2025-11-12  
**Related Files:**
- `chatbot/models.py` - FAQ model definition
- `chatbot/admin.py` - FAQ admin interface
- `chatbot/management/commands/load_faq.py` - Load command
- `chatbot/fixtures/faq.json` - Fixture data
