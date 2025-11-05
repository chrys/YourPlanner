# Testing the VIP Discount Implementation

## Prerequisites
Ensure all migrations have been run:
```bash
python manage.py makemigrations orders
python manage.py migrate orders
```

## Step-by-Step Testing Guide

### 1. Set Up Labels and Rules in Admin

1. Navigate to Django Admin (`/admin`)
2. Go to **Labels** app
3. Create a new Label:
   - Name: `Customer_VIP`
   - Label Type: `Customer`
   - Description: "VIP Customer for special discounts"
   - Color: `#FFD700` (gold, optional)
   - Click **Save**

4. Go to **Rules** app → **Rule Triggers**
5. Create a new RuleTrigger (if not already exists):
   - Name: `On Order Creation Trigger`
   - Code: `discount_vip`
   - Click **Save**

6. Go to **Rules** app → **Rules**
7. Create a new Rule:
   - Name: `VIP Order Discount Rule`
   - Description: `Apply 10% discount to VIP customers' new orders`
   - Status: **ENABLED**
   - Trigger: Select `On Order Creation Trigger`
   - Labels: (leave empty or select specific labels if desired)
   - Click **Save**

8. Go to **Rules** app → **Rule Conditions**
9. Create a new RuleCondition:
   - Rule: Select `VIP Order Discount Rule`
   - Entity: `CUSTOMER`
   - Operator: `HAS_LABEL`
   - Label: Select `Customer_VIP`
   - Click **Save**

10. Go to **Rules** app → **Rule Actions**
11. Create a new RuleAction:
    - Rule: Select `VIP Order Discount Rule`
    - Action Type: `DISCOUNT`
    - Action Params: Paste this JSON:
    ```json
    {"percentage": 10, "description": "VIP New Order Discount"}
    ```
    - Click **Save**

### 2. Create a Test Customer

1. Go to **Users** app → **Users**
2. Create a new User or select an existing one
3. Go to **Users** app → **Customers**
4. Create or edit a Customer profile:
   - Assign the User
   - Add `Customer_VIP` label to the **Labels** field
   - Click **Save**

### 3. Test the Discount Application

1. Log in as the VIP customer (using the test user you created)
2. Navigate to browse packages or start creating an order
3. Create a new order by either:
   - Selecting a package, OR
   - Manually adding items to an order
4. View your basket at `/orders/basket`
5. **Expected Result**: 
   - Green alert box should appear with "🎉 VIP Discount Applied!"
   - Should show: "VIP New Order Discount: -10% (€X.XX)"
   - Grand Total should be reduced by 10%

### 4. Verify Database

Check the database to confirm discount was stored:

```bash
python manage.py dbshell
```

Then query:
```sql
SELECT id, customer_id, discount_percentage, discount_amount, discount_description, total_amount 
FROM orders_order 
WHERE customer_id = <YOUR_CUSTOMER_ID> 
ORDER BY created_at DESC LIMIT 1;
```

Expected output:
```
id | customer_id | discount_percentage | discount_amount | discount_description        | total_amount
1  | 5           | 10.00              | 50.00          | VIP New Order Discount     | 450.00
```

### 5. Test Non-VIP Customer (Negative Test)

1. Create another test customer WITHOUT the VIP label
2. Create an order for this customer
3. View the basket
4. **Expected Result**: No discount alert should appear

### 6. Test Removing VIP Label

1. Go to the VIP customer's profile in admin
2. Remove the `Customer_VIP` label
3. Create a new order for this customer
4. View the basket
5. **Expected Result**: No discount should be applied

## Debugging Tips

### If discount is not applied:

1. **Check Order Creation Signal**:
   ```python
   # In Django shell
   from orders.models import Order
   order = Order.objects.latest('created_at')
   print(f"Order discount_percentage: {order.discount_percentage}")
   print(f"Order discount_amount: {order.discount_amount}")
   ```

2. **Check Customer Labels**:
   ```python
   from users.models import Customer
   customer = Customer.objects.get(user__username='testuser')
   labels = customer.labels.all()
   print(f"Customer labels: {[label.name for label in labels]}")
   ```

3. **Manually Trigger Rule Processing**:
   ```python
   from rules.engine import process_rules
   from orders.models import Order
   
   order = Order.objects.latest('created_at')
   process_rules(target_entity=order, event_code='discount_vip')
   order.refresh_from_db()
   print(f"After processing - discount: {order.discount_percentage}%")
   ```

4. **Check RuleTrigger**:
   ```python
   from rules.models import RuleTrigger
   trigger = RuleTrigger.objects.get(code='discount_vip')
   print(f"Trigger found: {trigger}")
   print(f"Rules for trigger: {trigger.rule_set.all()}")
   ```

5. **Enable Debug Logging**:
   Add to `settings.py`:
   ```python
   LOGGING = {
       'version': 1,
       'handlers': {
           'console': {
               'class': 'logging.StreamHandler',
           },
       },
       'root': {
           'handlers': ['console'],
           'level': 'DEBUG',
       },
   }
   ```

## Testing API (if applicable)

If you have REST API endpoints for order creation, test via curl:

```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "customer_id": 5,
    "items": [...]
  }'
```

Then check the response for discount fields.

## Cleanup

To reset test data:
```bash
# Delete test orders
python manage.py dbshell
DELETE FROM orders_order WHERE customer_id = <TEST_CUSTOMER_ID>;
DELETE FROM orders_orderitem WHERE order_id IN (SELECT id FROM orders_order WHERE customer_id = <TEST_CUSTOMER_ID>);

# Or reset entire test database
python manage.py flush --no-input
python manage.py migrate
```
