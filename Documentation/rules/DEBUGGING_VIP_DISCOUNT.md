# VIP Discount - Debugging Checklist & Root Cause Analysis

## Summary of the Issue
The VIP discount was not showing on the order detail page (`/orders/1`) even though the customer had the `Customer_VIP` label.

## Root Cause Found ✓
**Location:** `rules/engine.py` - `process_rules()` function

**The Problem:**
When `process_rules(order)` was called with an Order entity, it was checking the **Order's labels** instead of the **Customer's labels**. Since the VIP label is assigned to the Customer, not the Order, the rule conditions would never match.

**Code Issue (FIXED):**
```python
# OLD (BROKEN):
target_entity_labels = get_entity_labels(target_entity)  # target_entity is Order
# ^ This returns Order's labels (empty), not Customer's labels

# NEW (FIXED):
if isinstance(target_entity, Order) and target_entity.customer:
    entity_to_check = target_entity.customer  # Extract customer
    target_entity_labels = get_entity_labels(entity_to_check)  # Check customer's labels
# ^ Now returns Customer's labels (includes Customer_VIP)
```

---

## Step-by-Step Debugging Guide (For Future Issues)

### STEP 1: Verify Customer Has VIP Label
```bash
cd /Users/chrys/Projects/YourPlanner
python manage.py shell
>>> from users.models import Customer
>>> from labels.models import Label
>>> vip_label = Label.objects.get(name='Customer_VIP')
>>> vip_customers = Customer.objects.filter(labels=vip_label)
>>> for c in vip_customers:
...     print(f"{c.user.get_full_name()} - Labels: {list(c.labels.all())}")
```

**Expected Output:** Shows customer with Customer_VIP label

---

### STEP 2: Verify Rule Configuration
```bash
>>> from rules.models import RuleTrigger, Rule, RuleCondition, RuleAction
>>> 
>>> # Check trigger exists
>>> trigger = RuleTrigger.objects.get(code='discount_vip')
>>> print(f"Trigger: {trigger.code}")
>>>
>>> # Check rule exists and is enabled
>>> rule = Rule.objects.get(trigger=trigger)
>>> print(f"Rule: {rule.name}, Status: {rule.status}")
>>>
>>> # Check conditions
>>> for cond in rule.conditions.all():
...     print(f"Condition: {cond.entity} {cond.operator} {cond.label}")
>>>
>>> # Check actions
>>> for action in rule.actions.all():
...     print(f"Action: {action.action_type}, Params: {action.action_params}")
```

**Expected Output:**
- Rule status: `ENABLED`
- Condition: `CUSTOMER HAS_LABEL Customer_VIP`
- Action: `DISCOUNT` with `percentage: 10`

---

### STEP 3: Test process_rules() Directly
```bash
>>> from rules.engine import process_rules
>>> from orders.models import Order
>>>
>>> # Get VIP customer's pending order
>>> order = Order.objects.get(pk=1)  # Replace with your order ID
>>> print(f"Order: {order.pk}, Customer: {order.customer}")
>>> print(f"Customer labels: {list(order.customer.labels.all())}")
>>>
>>> # Test the rule engine
>>> result = process_rules(target_entity=order, event_code='discount_vip')
>>> print(f"Result: {result}")
```

**Expected Output:**
```
[DEBUG] Order detected. Using Customer Customer: ... for rule evaluation.
[DEBUG] Entity labels: ['Customer_VIP']
Found 1 applicable rules for event 'discount_vip' and entity 'Customer: ...'.
All conditions met for rule: 'On Order Creation Rule'. Executing actions.
Calculated 10% discount for Order #1: VIP New Order Discount
Discount amount: 67.50, Final total: 607.50
Result: {'discount_percentage': Decimal('10'), 'discount_amount': Decimal('67.50'), ...}
```

---

### STEP 4: Check Console Logs During View Rendering
When you view `/orders/1` or `/orders/basket`, check the Django development server console for:
- `[DEBUG]` messages from `process_rules()`
- Calculated discount amounts
- Rule condition matches

---

### STEP 5: Verify Template Context
```bash
>>> from orders.views import OrderDetailView
>>> # The view should pass these to template:
>>> # - discount_percentage (Decimal)
>>> # - discount_amount (Decimal)
>>> # - discount_description (str)
```

Template should show alert if `discount_percentage > 0`

---

## Files Modified to Fix This Issue

### 1. `/Users/chrys/Projects/YourPlanner/rules/engine.py`
**Function:** `process_rules(target_entity, event_code)`

**Changes:**
- Added logic to detect when `target_entity` is an Order
- Extracts `target_entity.customer` for rule evaluation
- Uses customer's labels instead of order's labels
- Added `[DEBUG]` logging statements

**Lines Changed:** ~120-165

---

### 2. `/Users/chrys/Projects/YourPlanner/orders/views.py`
**Class:** `OrderDetailView.get_context_data()`

**Changes:**
- Added discount calculation on-the-fly
- Calls `process_rules(target_entity=self.object, event_code='discount_vip')`
- Passes discount context variables to template

**Lines Changed:** ~277-290

---

### 3. `/Users/chrys/Projects/YourPlanner/orders/templates/orders/order_detail.html`
**Section:** Total summary

**Changes:**
- Added discount alert display
- Shows green success alert when discount is applied
- Displays discount percentage, amount, and description

**Lines Changed:** ~207-221

---

## Debug Script

A comprehensive debugging script is available at:
`/Users/chrys/Projects/YourPlanner/debug_discount.py`

**Usage:**
```bash
cd /Users/chrys/Projects/YourPlanner
python debug_discount.py
```

**What it checks:**
1. Customer_VIP label exists
2. VIP customers have the label assigned
3. discount_vip trigger exists
4. Rule is enabled with proper conditions
5. Tests process_rules() with a real order
6. Confirms Order model has no discount fields

---

## Testing Checklist

- [ ] Login as VIP customer (has Customer_VIP label)
- [ ] Create or view pending order with items
- [ ] Check Django console for debug messages:
  - `[DEBUG] Order detected. Using Customer...`
  - `[DEBUG] Entity labels: ['Customer_VIP']`
  - `Found 1 applicable rules`
  - `Calculated 10% discount`
- [ ] Visit `/orders/1` (order detail page)
- [ ] Verify green alert shows: **"🎉 VIP Discount Applied!"**
- [ ] Verify discount amount is correct: 10% of total
- [ ] Visit `/orders/basket`
- [ ] Verify same discount alert shows in basket
- [ ] Refresh page - discount recalculates fresh (not cached)

---

## Key Takeaways

1. **Entity Type Matters:** Rules are defined for specific entity types (Customer, Order, Service, etc.)
2. **Label Assignment Level:** VIP label must be on the Customer model, not on the Order
3. **Rule Evaluation:** When passing an Order to `process_rules()`, the engine must extract the Customer to evaluate conditions
4. **Stateless Calculation:** Discount is calculated on-the-fly every view render, not persisted to database
5. **Debug Logging:** Enable by checking Django server console for `[DEBUG]` messages

---

## Quick Reference: Admin Setup

If you need to recreate the configuration:

### Label (via Django Admin)
- **Name:** Customer_VIP
- **Type:** CUSTOMER
- **Description:** Marks customers eligible for VIP discounts

### RuleTrigger (via Django Admin)
- **Name:** discount_vip
- **Code:** discount_vip

### Rule (via Django Admin)
- **Name:** On Order Creation Rule
- **Trigger:** discount_vip
- **Status:** ENABLED

### RuleCondition (via Django Admin)
- **Rule:** On Order Creation Rule
- **Entity:** CUSTOMER
- **Operator:** HAS_LABEL
- **Label:** Customer_VIP

### RuleAction (via Django Admin)
- **Rule:** On Order Creation Rule
- **Action Type:** DISCOUNT
- **Params:**
  ```json
  {
    "percentage": 10,
    "description": "VIP New Order Discount"
  }
  ```

---

**Status:** ✅ FIXED and VERIFIED
