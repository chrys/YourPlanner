from django.db.models import Q
from .models import Rule, RuleCondition, RuleAction, RuleTrigger
from labels.models import Label

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
    This is a placeholder and needs to be expanded based on actual action types and parameters.
    """
    print(f"Executing action: {action.action_type} for entity: {target_entity} with params: {action.action_params}")
    # Example for 'STATUS_CHANGE'
    # if action.action_type == 'STATUS_CHANGE':
    #     new_status = action.action_params.get('new_status')
    #     if new_status and hasattr(target_entity, 'status'):
    #         target_entity.status = new_status
    #         target_entity.save()
    #         print(f"Changed status of {target_entity} to {new_status}")

    # Example for 'DISCOUNT'
    # if action.action_type == 'DISCOUNT':
    #     # This is highly dependent on how discounts are applied in your system.
    #     # It might involve creating a discount record, modifying an order, etc.
    #     print(f"Applying discount: {action.action_params} to {target_entity}")
    #     pass


def process_rules(target_entity, event_code):
    """
    Processes all active rules for a given target entity and event.
    """
    try:
        trigger = RuleTrigger.objects.get(code=event_code)
    except RuleTrigger.DoesNotExist:
        print(f"RuleTrigger with code '{event_code}' does not exist.")
        return

    # Initial filter for rules: active, matching trigger
    # Q objects for complex queries
    query = Q(status='ENABLED') & Q(trigger=trigger)

    # Get labels of the target entity
    target_entity_labels = get_entity_labels(target_entity)
    target_entity_label_ids = [label.id for label in target_entity_labels]

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

    print(f"Found {len(applicable_rules)} applicable rules for event '{event_code}' and entity '{target_entity}'.")

    for rule in applicable_rules:
        all_conditions_met = True
        if not rule.conditions.exists(): # If a rule has no conditions, it's considered met
            pass
        else:
            for condition in rule.conditions.all():
                if not check_condition(condition, target_entity):
                    all_conditions_met = False
                    break # Stop checking conditions for this rule

        if all_conditions_met:
            print(f"All conditions met for rule: '{rule.name}'. Executing actions.")
            for action in rule.actions.all():
                execute_action(action, target_entity)
        else:
            print(f"Not all conditions met for rule: '{rule.name}'.")
