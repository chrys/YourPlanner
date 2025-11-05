# VIP Discount System - Refactored to Calculate On-The-Fly

## Summary of Changes

You requested to calculate discount on-the-fly instead of persisting to the database, and move all documentation to `Documentation/rules/` directory. This has been completed.

## What Changed

### 1. **Order Model** (`orders/models.py`)
**REVERTED** - Removed the following fields that were added:
- ❌ `discount_percentage`
- ❌ `discount_amount`
- ❌ `discount_description`

**Result**: Order model now has NO discount-related fields. All discount data is calculated at display time.

### 2. **Order.calculate_total()** (`orders/models.py`)
**REVERTED** to original state:
- Removed discount calculation logic
- Now only sums order items without any discount application
- Discount is calculated separately by rule engine on-the-fly

### 3. **Rule Engine** (`rules/engine.py`)

#### `execute_action()` function
**CHANGED** to calculate and RETURN discount info instead of saving:
```python
# Before: Saved discount to Order object
# Now: Returns discount info as a dictionary

Returns:
{
    'discount_percentage': Decimal,
    'discount_amount': Decimal,
    'discount_description': str,
    'final_total': Decimal,
    'original_total': Decimal
}
```

**Key changes**:
- ✅ Calculates discount based on order's current total
- ✅ Does NOT save to database
- ✅ Returns discount info for view to use
- ✅ Returns `None` if no discount applies

#### `process_rules()` function
**CHANGED** to return discount info:
- ✅ Now returns `discount_info` dict instead of void
- ✅ Collects and returns discount from `execute_action()`
- ✅ Returns `None` if no discount found

### 4. **Signal Handler** (`orders/signals.py`)
**CHANGED** to use returned discount info:
- ✅ Calls `process_rules()` and captures returned discount info
- ✅ Logs discount info but does NOT save to database
- ✅ Discount info is calculated fresh each time it's needed

### 5. **Basket View** (`orders/views.py` - BasketView)
**CHANGED** to calculate discount dynamically:

```python
# Before: Retrieved discount from Order model fields
# Now: Calculates discount on-the-fly in get_context_data()

if current_order:
    from rules.engine import process_rules
    discount_info = process_rules(target_entity=current_order, event_code='discount_vip')
    
    if discount_info:
        discount_percentage = discount_info.get('discount_percentage')
        discount_amount = discount_info.get('discount_amount')
        discount_description = discount_info.get('discount_description')
        grand_total = discount_info.get('final_total')
```

**Key changes**:
- ✅ Calls rule engine each time basket is viewed
- ✅ No database persistence
- ✅ Always shows current/accurate discount
- ✅ Template context includes discount variables for display

### 6. **Documentation Organization**
**MOVED** all 8 documentation files to `Documentation/rules/`:

```
Documentation/
├── rules/
│   ├── README_VIP_DISCOUNT.md
│   ├── VIP_DISCOUNT_COMPLETE_GUIDE.md
│   ├── VIP_DISCOUNT_IMPLEMENTATION.md
│   ├── TESTING_VIP_DISCOUNT.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── VIP_DISCOUNT_FLOW_DIAGRAMS.md
│   ├── IMPLEMENTATION_CHANGES.md
│   └── CHANGES_SUMMARY.md
├── (other existing docs)
```

## How It Works Now

### User Flow
1. **VIP Customer creates order**
   - Order saved (no discount fields)
   - Signal fires
   - Rule engine evaluates VIP status
   - Discount info returned and logged (not saved)

2. **Customer views basket**
   - `BasketView.get_context_data()` called
   - Rule engine calculates discount on-the-fly
   - Discount info passed to template
   - Template displays discount alert with calculated values

3. **Template renders**
   - Shows discount percentage, amount, and description
   - Shows final total with discount applied
   - All values calculated, not from database

## Benefits of This Approach

✅ **No Database Schema Changes**: Order model remains clean
✅ **Always Current**: Discount calculated fresh each view
✅ **Reversible**: Can change discount rules without migrations
✅ **Flexible**: Discount calculation happens only when needed
✅ **Clean Separation**: Rule engine handles business logic

## Technical Details

### Discount Calculation Flow

```
BasketView.get_context_data()
    ↓
process_rules(order, 'discount_vip')
    ↓
Find applicable rules
    ↓
Evaluate conditions (Customer HAS_LABEL VIP)
    ↓
execute_action(DISCOUNT)
    ├─ Get current order total
    ├─ Calculate: discount_amount = total * (percentage / 100)
    └─ Return: {discount_percentage, discount_amount, final_total, ...}
    ↓
Return discount info to view
    ↓
Template renders with discount values
```

## Database Impact

**NO migration needed!**

The Order model has NO new fields, so:
- ✅ No database schema changes
- ✅ No migrations required
- ✅ Existing data unaffected
- ✅ Code is backward compatible

## Testing Considerations

When testing the discount:

1. **Discount applied on view render**, not on order creation
2. **Each basket view** recalculates discount fresh
3. **VIP label still required** on customer
4. **Rule trigger code** must be 'discount_vip'
5. **No database fields** to check - only view context

## Migration Path (if you change your mind)

If you later decide to persist discount to database:

1. Add discount fields back to Order model
2. Create migration
3. Update `execute_action()` to save fields
4. Update `process_rules()` to save after action execution
5. Update `BasketView` to read from Order instead of calculating

## Documentation Location

All documentation is now in: `Documentation/rules/`

**Key files**:
- `README_VIP_DISCOUNT.md` - Quick start guide
- `VIP_DISCOUNT_COMPLETE_GUIDE.md` - Full reference
- `TESTING_VIP_DISCOUNT.md` - How to test
- `VIP_DISCOUNT_IMPLEMENTATION.md` - Technical details
- `VIP_DISCOUNT_FLOW_DIAGRAMS.md` - Visual flows

## Summary

✅ Discount calculation moved from database persistence to on-the-fly calculation
✅ Order model reverted to original state (no discount fields)
✅ Rule engine updated to return discount info instead of saving
✅ Basket view updated to calculate discount dynamically
✅ All documentation moved to `Documentation/rules/`
✅ **No database migration needed**

---

**Implementation Date**: November 5, 2025  
**Status**: ✅ Complete - No migrations required  
**Architecture**: Stateless on-the-fly calculation
