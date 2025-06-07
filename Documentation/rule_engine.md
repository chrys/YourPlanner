# Rule Engine

The rule engine is a core component designed to automate actions based on predefined conditions related to various entities within the application.

## Purpose

The primary purpose of the rule engine is to:

1.  Take a **target entity** (e.g., Professionals, Customers, Services, Items, Prices, and Orders).
2.  Find all **active rules** that might apply to this entity, often based on a **Label** already associated with it or a specific **event/trigger**.
3.  For each rule, **evaluate its conditions** against the target entity.
4.  If all conditions for a rule are met, **execute its actions**.

## Models

The rule engine relies on the following Django models defined in the `rules` app:

### `RuleTrigger`

Defines when a rule's evaluation process should be initiated.

-   `name`: A human-readable name for the trigger (e.g., "On Entity Creation", "On Label Assignment", "Daily Check").
-   `code`: A unique machine-readable code for the trigger (e.g., `ON_CREATION`, `ON_LABEL_LINK`, `DAILY`).

### `Rule`

Represents an individual rule.

-   `name`: A descriptive name for the rule.
-   `description`: (Optional) A more detailed explanation of what the rule does.
-   `status`: Indicates whether the rule is active (`ENABLED`) or inactive (`DISABLED`).
-   `trigger`: A ForeignKey to a `RuleTrigger` model, specifying when this rule should be considered.
-   `labels`: A ManyToManyField to `Label` models. If specified, the rule is only considered if the target entity is associated with one of these labels.

### `RuleCondition`

Defines the conditions that must be met for a rule's actions to be executed. A rule can have multiple conditions, and all must evaluate to true.

-   `rule`: A ForeignKey to the `Rule` this condition belongs to.
-   `entity`: The type of entity this condition applies to (choices defined in `labels.models.LABEL_TYPES`).
-   `operator`: The type of check to perform. Currently supported:
    -   `HAS_LABEL`: Checks if the target entity has a specific label.
    -   `NOT_LABEL`: Checks if the target entity does not have a specific label.
-   `label`: A ForeignKey to a `Label` model, used in conjunction with the `operator`.

### `RuleAction`

Defines the actions to be performed if all of a rule's conditions are met. A rule can have multiple actions.

-   `rule`: A ForeignKey to the `Rule` this action belongs to.
-   `action_type`: The type of action to perform. Examples:
    -   `DISCOUNT`: Apply a discount.
    -   `STATUS_CHANGE`: Change the status of an entity.
-   `action_params`: A JSONField containing parameters specific to the `action_type`. For example, for `DISCOUNT`, this might include `{"percentage": 10}` or `{"fixed_amount": 50}`.

## How It Works (Conceptual)

1.  **Event Occurs**: An event happens in the system, for example, a new `Order` is created, or a `Label` is added to a `Professional`. This event is associated with a `RuleTrigger` code.
2.  **Rule Retrieval**: The rule engine fetches all `Rule`s that are `ENABLED` and match the `RuleTrigger` code. If the rule has `labels` specified, it further filters to ensure the target entity has at least one of those labels.
3.  **Condition Evaluation**: For each retrieved rule, the engine iterates through its `RuleCondition`s:
    -   It checks if the condition's `entity` type matches the target entity's type.
    -   It evaluates the condition based on the `operator` and `label`. For instance, if the operator is `HAS_LABEL`, it checks if the target entity is linked to the specified `label`.
4.  **Action Execution**: If all conditions for a rule evaluate to true, the engine executes all `RuleAction`s associated with that rule. This involves:
    -   Interpreting the `action_type`.
    -   Using the `action_params` to perform the specific action on the target entity.

## Example Usage

### Scenario: Apply a 10% discount to VIP Customers on new orders.

1.  **Define Labels**:
    -   Ensure a `Label` exists for "VIP Customer" (e.g., `name="VIP Customer"`, `type="CUSTOMER"`).
2.  **Define `RuleTrigger`**:
    -   Ensure a `RuleTrigger` for "Order Creation" exists (e.g., `name="On Order Creation"`, `code="ON_ORDER_CREATION"`).
3.  **Define `Rule`**:
    -   `name="VIP Discount on New Orders"`
    -   `status="ENABLED"`
    -   `trigger`: Link to "On Order Creation" trigger.
    -   `labels`: Link to "VIP Customer" label. (This assumes the Customer, who is the subject of the VIP label, is accessible from the Order entity, or the Order itself gets a temporary VIP label).
4.  **Define `RuleCondition`**:
    -   `rule`: Link to "VIP Discount on New Orders".
    -   `entity`: `"CUSTOMER"` (or the entity type that holds the VIP label and is accessible from the order).
    -   `operator`: `"HAS_LABEL"`
    -   `label`: Link to "VIP Customer" label.
5.  **Define `RuleAction`**:
    -   `rule`: Link to "VIP Discount on New Orders".
    -   `action_type`: `"DISCOUNT"`
    -   `action_params`: `{"percentage": 10, "description": "VIP New Order Discount"}`

## Integration (Guidance)

To integrate the rule engine:

-   Identify points in your application where rule processing should occur (e.g., after a model's `save()` method, in response to specific API calls, or as part of a periodic task).
-   At these points, call the main processing function of the rule engine (e.g., `process_rules(target_entity, event_code)`), passing the relevant entity and the appropriate trigger code.

For example, in a Django signal handler for when an `Order` is created:

```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order # Assuming Order is in the same app
from rules.engine import process_rules # Assuming process_rules is in rules.engine

@receiver(post_save, sender=Order)
def handle_new_order(sender, instance, created, **kwargs):
    if created:
        process_rules(target_entity=instance, event_code='ON_ORDER_CREATION')
```

This documentation provides a foundational understanding of the rule engine. Specific implementation details of action executions will depend on the application's architecture and the capabilities of the entities involved.
