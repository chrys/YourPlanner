from django.db.models import Q
from .models import Rule, RuleCondition, RuleAction, RuleTrigger
from labels.models import Label
from decimal import Decimal  # Changed: Added import for Decimal to handle discount percentages

# Placeholder for actual entity type checking and label access
# You'll need to adapt this based on how your entities are structured
# and how labels are related to them.

def get_entity_labels(entity_instance):
    """
    Placeholder function to get labels associated with an entity instance.
    This needs to be implemented based on your project's structure.
    Example: if your entity has a 'labels' ManyToManyField.
    """
    if hasattr(entity_instance, 'labels') and hasattr(entity_instance.labels, 'all'):
        return list(entity_instance.labels.all())
    return []

def check_condition(condition, target_entity):
    """
    Evaluates a single rule condition against a target entity.
    """
    entity_labels = get_entity_labels(target_entity)
    entity_label_ids = [label.id for label in entity_labels]

    # Check if the condition's entity type matches the target_entity's type
    # This is a simplified check. You might need a more robust way to compare entity types.
    entity_class = condition.entity_class_for_label_type()
    if entity_class and not isinstance(target_entity, entity_class):
         # If condition.entity (e.g. "CUSTOMER") does not match target_entity (e.g. Professional)
         # then this condition is not met.
         return False


    if condition.operator == 'HAS_LABEL':
        return condition.label_id in entity_label_ids
    elif condition.operator == 'NOT_LABEL':
        return condition.label_id not in entity_label_ids

    # Potentially add more operators here
    # elif condition.operator == 'EQUALS':
    #     return getattr(target_entity, condition.field_name) == condition.value
    # elif condition.operator == 'GREATER_THAN':
    #     # Ensure field value and condition value are of comparable types
    #     return getattr(target_entity, condition.field_name) > condition.value

    return False # Default if operator is unknown or condition not met

def execute_action(action, target_entity):
    """
    Executes a single rule action on a target entity.
    Currently supports:
    - DISCOUNT: Calculate and return discount for an Order without saving to database
    
    Returns:
    - dict with discount information if applicable, None otherwise
    """
    # Changed: Implemented DISCOUNT action type for VIP customers (calculated on the fly)
    if action.action_type == 'DISCOUNT':
        # For DISCOUNT actions, we calculate discount without persisting to database
        # The target_entity should be an Order, and we check if its customer is VIP
        from orders.models import Order
        from users.models import Customer
        
        if isinstance(target_entity, Order):
            # Changed: Check if customer has the VIP label and return discount info
            customer = target_entity.customer
            if customer and isinstance(customer, Customer):
                # Get the discount parameters from action_params
                discount_percentage = action.action_params.get('percentage', 0)
                discount_description = action.action_params.get('description', 'Discount Applied')
                
                if discount_percentage > 0:
                    # Changed: Calculate discount on the fly without saving
                    # Get current order total
                    current_total = target_entity.total_amount or Decimal('0.00')
                    discount_amount = current_total * (Decimal(str(discount_percentage)) / Decimal('100'))
                    discount_amount = discount_amount.quantize(Decimal('0.01'))
                    final_total = current_total - discount_amount
                    
                    # Return discount info instead of saving
                    discount_info = {
                        'discount_percentage': Decimal(str(discount_percentage)),
                        'discount_amount': discount_amount,
                        'discount_description': discount_description,
                        'final_total': final_total,
                        'original_total': current_total
                    }
                    print(f"Calculated {discount_percentage}% discount for Order #{target_entity.pk}: {discount_description}")
                    print(f"Discount amount: {discount_amount}, Final total: {final_total}")
                    return discount_info
        else:
            # Changed: If target entity is not an Order, we cannot apply discount
            print(f"Discount action cannot be applied to {type(target_entity).__name__}. Expected Order.")
    else:
        # Changed: Log for other action types that are not yet implemented
        print(f"Executing action: {action.action_type} for entity: {target_entity} with params: {action.action_params}")
    
    return None


def process_rules(target_entity, event_code):
    """
    Processes all active rules for a given target entity and event.
    Changed: Returns discount info if applicable, None otherwise
    Changed: For Order entities, extracts customer and checks customer labels
    """
    try:
        trigger = RuleTrigger.objects.get(code=event_code)
    except RuleTrigger.DoesNotExist:
        print(f"RuleTrigger with code '{event_code}' does not exist.")
        return None

    # CHANGED: Extract customer from order if target_entity is an Order
    entity_to_check = target_entity
    from orders.models import Order
    if isinstance(target_entity, Order) and target_entity.customer:
        entity_to_check = target_entity.customer
        print(f"[DEBUG] Order detected. Using Customer {target_entity.customer} for rule evaluation.")
    
    # Initial filter for rules: active, matching trigger
    # Q objects for complex queries
    query = Q(status='ENABLED') & Q(trigger=trigger)

    # CHANGED: Get labels of the entity to check (customer, not order)
    target_entity_labels = get_entity_labels(entity_to_check)
    target_entity_label_ids = [label.id for label in target_entity_labels]
    print(f"[DEBUG] Entity labels: {[label.name for label in target_entity_labels]}")

    applicable_rules = []
    # Fetch all rules matching the trigger and status first
    rules_for_trigger = Rule.objects.filter(query).prefetch_related('conditions', 'actions', 'labels')

    for rule in rules_for_trigger:
        if not rule.labels.exists(): # Rule has no specific labels, so it's potentially applicable
            applicable_rules.append(rule)
        else:
            # Rule has specific labels, check if the target_entity has any of them
            rule_label_ids = [label.id for label in rule.labels.all()]
            if any(label_id in target_entity_label_ids for label_id in rule_label_ids):
                applicable_rules.append(rule)

    print(f"Found {len(applicable_rules)} applicable rules for event '{event_code}' and entity '{entity_to_check}'.")

    # Changed: Collect all discount info from actions
    discount_info = None
    for rule in applicable_rules:
        all_conditions_met = True
        if not rule.conditions.exists(): # If a rule has no conditions, it's considered met
            pass
        else:
            for condition in rule.conditions.all():
                # CHANGED: Check condition against the extracted entity (customer)
                if not check_condition(condition, entity_to_check):
                    all_conditions_met = False
                    break # Stop checking conditions for this rule

        if all_conditions_met:
            print(f"All conditions met for rule: '{rule.name}'. Executing actions.")
            for action in rule.actions.all():
                # Changed: Capture discount info from action execution
                # CHANGED: Pass original order to execute_action, not the customer
                action_result = execute_action(action, target_entity)
                if action_result and isinstance(action_result, dict):
                    discount_info = action_result
        else:
            print(f"Not all conditions met for rule: '{rule.name}'.")
    
    # Changed: Return discount info if calculated
    return discount_info
