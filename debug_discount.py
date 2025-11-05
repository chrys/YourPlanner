#!/usr/bin/env python
"""
Comprehensive debugging script for VIP discount system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YourPlanner.settings.base')
django.setup()

from django.contrib.auth.models import User
from users.models import Customer
from labels.models import Label
from rules.models import RuleTrigger, Rule, RuleCondition, RuleAction
from orders.models import Order
from rules.engine import process_rules
from decimal import Decimal

print("\n" + "="*80)
print("VIP DISCOUNT DEBUGGING SCRIPT")
print("="*80)

# STEP 1: Check if Customer_VIP label exists
print("\n[STEP 1] Checking if 'Customer_VIP' label exists...")
try:
    vip_label = Label.objects.get(name='Customer_VIP')
    print(f"✓ Label found: {vip_label.name} (ID: {vip_label.pk}, Type: {vip_label.label_type})")
except Label.DoesNotExist:
    print("✗ Label 'Customer_VIP' NOT FOUND in database!")
    print("  ACTION: Create it via Django admin or use:")
    print("  Label.objects.create(name='Customer_VIP', label_type='CUSTOMER')")

# STEP 2: Find all customers with VIP label
print("\n[STEP 2] Finding customers with 'Customer_VIP' label...")
try:
    vip_label = Label.objects.get(name='Customer_VIP')
    vip_customers = Customer.objects.filter(labels=vip_label)
    if vip_customers.exists():
        for customer in vip_customers:
            print(f"✓ VIP Customer: {customer.user.get_full_name()} ({customer.user.username})")
    else:
        print("✗ No customers have the 'Customer_VIP' label!")
        print("  ACTION: Assign the label to a customer via Django admin")
except Label.DoesNotExist:
    print("✗ Cannot check - 'Customer_VIP' label doesn't exist")

# STEP 3: Check rule configuration
print("\n[STEP 3] Checking rule trigger 'discount_vip'...")
try:
    trigger = RuleTrigger.objects.get(code='discount_vip')
    print(f"✓ RuleTrigger found: {trigger.code} (ID: {trigger.pk})")
except RuleTrigger.DoesNotExist:
    print("✗ RuleTrigger 'discount_vip' NOT FOUND!")
    print("  ACTION: Create it via Django admin")

# STEP 4: Check if Rule exists for this trigger
print("\n[STEP 4] Checking Rule for 'discount_vip' trigger...")
try:
    trigger = RuleTrigger.objects.get(code='discount_vip')
    rules = Rule.objects.filter(trigger=trigger, status='ENABLED')
    if rules.exists():
        for rule in rules:
            print(f"✓ Rule found: {rule.name} (ID: {rule.pk}, Status: {rule.status})")
            
            # Check conditions
            conditions = RuleCondition.objects.filter(rule=rule)
            if conditions.exists():
                for condition in conditions:
                    print(f"  ├─ Condition: Entity={condition.entity}, Operator={condition.operator}")
                    print(f"  │  Label: {condition.label}")
            else:
                print(f"  ├─ ✗ No conditions found for this rule!")
            
            # Check actions
            actions = RuleAction.objects.filter(rule=rule)
            if actions.exists():
                for action in actions:
                    print(f"  └─ Action: Type={action.action_type}")
                    print(f"     Params: {action.action_params}")
            else:
                print(f"  └─ ✗ No actions found for this rule!")
    else:
        print("✗ No ENABLED rules found for 'discount_vip' trigger!")
        print("  ACTION: Create a rule via Django admin or enable existing one")
except RuleTrigger.DoesNotExist:
    print("✗ Cannot check - 'discount_vip' trigger doesn't exist")

# STEP 5: Test process_rules() with a VIP customer
print("\n[STEP 5] Testing process_rules() with a VIP customer order...")
try:
    vip_label = Label.objects.get(name='Customer_VIP')
    vip_customers = Customer.objects.filter(labels=vip_label)
    
    if vip_customers.exists():
        customer = vip_customers.first()
        # Get or create a pending order
        pending_order = Order.objects.filter(customer=customer, status='PENDING').first()
        
        if pending_order and pending_order.total_amount > 0:
            print(f"Using order: {pending_order.pk} (Total: {pending_order.total_amount})")
            discount_info = process_rules(target_entity=pending_order, event_code='discount_vip')
            
            if discount_info:
                print(f"✓ Discount applied!")
                print(f"  Percentage: {discount_info.get('discount_percentage')}%")
                print(f"  Amount: {discount_info.get('discount_amount')}")
                print(f"  Description: {discount_info.get('discount_description')}")
                print(f"  Final Total: {discount_info.get('final_total')}")
            else:
                print("✗ process_rules() returned None - no discount applied!")
                print("  This means the rule conditions did not match!")
        else:
            print("✗ No valid pending order found for testing")
            print("  ACTION: Create an order with items first")
    else:
        print("✗ No VIP customers found to test with")
except Exception as e:
    print(f"✗ Error testing process_rules(): {e}")
    import traceback
    traceback.print_exc()

# STEP 6: Check Order model
print("\n[STEP 6] Checking Order model for discount fields...")
from orders.models import Order as OrderModel
if hasattr(OrderModel, 'discount_percentage'):
    print("✗ Order model has 'discount_percentage' field (should be removed!)")
else:
    print("✓ Order model does NOT have 'discount_percentage' field (correct)")

print("\n" + "="*80)
print("END OF DEBUG REPORT")
print("="*80 + "\n")
