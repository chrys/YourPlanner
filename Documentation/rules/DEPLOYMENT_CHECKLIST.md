# VIP Discount Implementation - Deployment Checklist

## Pre-Deployment

### Code Changes ✓
- [x] Modified `orders/models.py` - Added discount fields to Order model
- [x] Modified `orders/models.py` - Updated `calculate_total()` method
- [x] Created `orders/signals.py` - Signal handler for rule processing
- [x] Modified `orders/apps.py` - Registered signals in ready() method
- [x] Modified `rules/engine.py` - Implemented `execute_action()` for DISCOUNT
- [x] Modified `rules/engine.py` - Added Decimal import
- [x] Modified `orders/views.py` - Enhanced BasketView context
- [x] Modified `orders/templates/orders/basket.html` - Added discount display
- [x] Modified `labels/models.py` - Added lazy-loaded associations
- [x] Modified `rules/models.py` - Updated entity_class_for_label_type()

### Code Quality
- [x] No syntax errors in key files
- [x] All imports are correct
- [x] No circular import issues
- [x] Comments added per development guidelines
- [x] Code follows PascalCase for classes, camelCase for functions

## Deployment Steps

### 1. Database Migration
```bash
# Generate migration for new Order fields
python manage.py makemigrations orders

# Review migration file
cat orders/migrations/000X_auto_YYYYMMDD_HHMM.py

# Apply migration to database
python manage.py migrate orders

# Verify migration applied
python manage.py showmigrations orders
```

### 2. Admin Setup (Manual via UI)
```
Django Admin Dashboard (/admin)

1. Create Label:
   - Labels > Labels > Add Label
   - Name: Customer_VIP
   - Label Type: Customer
   - Save

2. Create RuleTrigger:
   - Rules > Rule Triggers > Add Rule Trigger
   - Name: On Order Creation Trigger
   - Code: discount_vip
   - Save

3. Create Rule:
   - Rules > Rules > Add Rule
   - Name: VIP Order Discount Rule
   - Description: Apply 10% discount to VIP customers' new orders
   - Status: ENABLED
   - Trigger: On Order Creation Trigger
   - Labels: (leave blank)
   - Save

4. Create RuleCondition:
   - Rules > Rule Conditions > Add Rule Condition
   - Rule: VIP Order Discount Rule
   - Entity: CUSTOMER
   - Operator: HAS_LABEL
   - Label: Customer_VIP
   - Save

5. Create RuleAction:
   - Rules > Rule Actions > Add Rule Action
   - Rule: VIP Order Discount Rule
   - Action Type: DISCOUNT
   - Action Params: {"percentage": 10, "description": "VIP New Order Discount"}
   - Save
```

### 3. Backup Database (Production)
```bash
# Create backup before applying changes
python manage.py dumpdata > backup_before_discount_feature.json

# Or for production
pg_dump yourplanner_db > backup_before_discount_feature.sql
```

### 4. Restart Services
```bash
# If using gunicorn/uwsgi
systemctl restart yourplanner

# If using runserver (development)
# No restart needed, Django auto-reloads
```

### 5. Cache Clearing (if applicable)
```bash
# Clear Django cache
python manage.py clear_cache

# Clear staticfiles cache
python manage.py collectstatic --noinput

# Clear Redis cache (if using)
redis-cli FLUSHDB
```

## Post-Deployment Verification

### Quick Tests
- [ ] Can access Django admin without errors
- [ ] Can view customer profiles
- [ ] Can create new orders
- [ ] Can view basket page without errors

### Functional Tests
- [ ] Create non-VIP customer → create order → no discount shown ✓
- [ ] Create VIP customer (with label) → create order → discount shown ✓
- [ ] Verify discount amount is correctly calculated (10%)
- [ ] Verify database stores discount fields correctly
- [ ] Verify discount displays in green alert in basket
- [ ] Remove VIP label from customer → new order has no discount ✓

### Database Validation
```bash
# Check discount fields exist
python manage.py dbshell
\d orders_order

# Check sample order with discount
SELECT id, discount_percentage, discount_amount, discount_description, total_amount 
FROM orders_order 
WHERE discount_percentage > 0 
LIMIT 1;

# Verify customer labels
SELECT customer_id, label_id FROM labels_label
WHERE name = 'Customer_VIP';
```

### Error Logs
```bash
# Check for any signal errors
tail -f logs/django.log | grep -i "signal\|discount\|rule"

# Check for import errors
tail -f logs/django.log | grep -i "import"

# Check for database errors
tail -f logs/django.log | grep -i "database\|migration"
```

## Rollback Plan (if needed)

### Option 1: Reverse Migration
```bash
# Show recent migrations
python manage.py showmigrations orders

# Reverse to previous migration
python manage.py migrate orders 000X_previous_migration_name

# Delete migration files (be careful!)
rm orders/migrations/000X_auto_YYYYMMDD_HHMM.py

# Revert code changes (git)
git checkout orders/models.py
```

### Option 2: Full Database Restore
```bash
# From JSON backup
python manage.py loaddata backup_before_discount_feature.json

# From SQL backup (PostgreSQL)
psql yourplanner_db < backup_before_discount_feature.sql
```

### Option 3: Partial Rollback
```bash
# If only rule configuration is wrong, delete in admin:
1. Delete RuleAction
2. Delete RuleCondition
3. Delete Rule
4. Delete RuleTrigger
5. Delete Label (if not used elsewhere)

# Keep code and database schema changes
```

## Monitoring

### Key Metrics to Track
- [ ] Order creation rate (should remain stable)
- [ ] Average order value (should decrease for VIP customers if discount applies)
- [ ] VIP customer conversion rate
- [ ] Error rate in logs

### Alerts to Set Up
```bash
# Monitor for discount application errors
grep -i "discount.*error" logs/django.log

# Monitor for rule processing failures
grep -i "rule.*error\|rule.*failed" logs/django.log

# Monitor for signal errors
grep -i "post_save.*error\|signal.*error" logs/django.log
```

### Performance Impact
- [x] Signal handlers: Minimal overhead (post_save is instant)
- [x] Rule processing: Fast for small rule sets
- [x] Database queries: Added 1 reverse relation lookup for customer labels
- [x] Template rendering: Added 3-4 context variables

## Documentation

### Updated Docs
- [x] VIP_DISCOUNT_IMPLEMENTATION.md - Overall implementation
- [x] TESTING_VIP_DISCOUNT.md - Testing procedures
- [x] IMPLEMENTATION_CHANGES.md - Technical details
- [x] VIP_DISCOUNT_FLOW_DIAGRAMS.md - Visual flow diagrams

### Team Communication
- [ ] Notify team of changes
- [ ] Share documentation links
- [ ] Schedule demo/training session
- [ ] Add to team wiki/knowledge base

## Post-Deployment Support

### Common Issues & Fixes

**Issue**: Discount not applying
- **Check**: Is customer labeled as VIP?
- **Check**: Is RuleTrigger code 'discount_vip'?
- **Check**: Is Rule status 'ENABLED'?
- **Fix**: See Debugging Tips in TESTING_VIP_DISCOUNT.md

**Issue**: Discount applied to non-VIP customers
- **Check**: Rule conditions are correct
- **Check**: Customer doesn't have VIP label assigned
- **Fix**: Verify Label associations in Customer admin

**Issue**: Database migration failed
- **Check**: Django version compatibility
- **Check**: Existing orders don't have null discount fields
- **Fix**: Run `python manage.py migrate --plan` first

**Issue**: Signal not triggering
- **Check**: Is orders.signals imported in orders/apps.py?
- **Check**: Is OrdersConfig set as default app in INSTALLED_APPS?
- **Fix**: Restart Django server

## Sign-Off

- [ ] Code review completed
- [ ] Tests passed
- [ ] Admin configuration complete
- [ ] Database backup taken
- [ ] Deployment executed
- [ ] Post-deployment verification passed
- [ ] Team notified
- [ ] Monitoring set up
- [ ] Documentation reviewed

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-05 | Initial implementation of VIP discount system |

---

## Contact & Support

For issues or questions about the VIP discount implementation:
1. Check TESTING_VIP_DISCOUNT.md for debugging tips
2. Review VIP_DISCOUNT_FLOW_DIAGRAMS.md to understand the flow
3. Check rule engine code in rules/engine.py
4. Check order signal in orders/signals.py
