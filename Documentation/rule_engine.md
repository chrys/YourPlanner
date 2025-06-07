# Rule Engine Documentation

The `rules` app provides a flexible system for creating and managing rules that can be applied to various entities within the application. These rules are defined by conditions and trigger actions when those conditions are met.

## Core Concepts

The rule engine is built around the following main components:

*   **Labels**: Rules are associated with one or more labels. The `labels` app is used to manage these labels.
*   **Rules**: A rule defines a set of conditions and actions.
*   **Rule Triggers**: Specify when a rule should be evaluated.
*   **Rule Conditions**: The specific criteria that must be met for a rule's actions to be executed.
*   **Rule Actions**: The operations to be performed if all of a rule's conditions are satisfied.

## Models

### `RuleTrigger`

Represents when a rule evaluation is triggered.

*   **Fields**:
    *   `name`: (CharField) A descriptive name for the trigger (e.g., "On Entity Creation", "Daily Check").
    *   `code`: (CharField, Unique) A unique code for programmatic access (e.g., `ON_CREATION`, `DAILY`).
*   **Admin Management**: Rule Triggers can be managed via the Django admin panel. It's generally expected that these are predefined and not frequently changed.

### `Rule`

Represents a single rule that associates labels with a set of conditions and actions, triggered at a specific point.

*   **Fields**:
    *   `name`: (CharField) A descriptive name for the rule (e.g., "VIP Customer Discount", "New Order Alert").
    *   `description`: (TextField, Optional) A more detailed explanation of what the rule does.
    *   `status`: (CharField) The current status of the rule.
        *   Choices: `ENABLED`, `DISABLED`
        *   Default: `DISABLED`
    *   `trigger`: (ForeignKey to `RuleTrigger`) Defines when this rule should be evaluated.
    *   `labels`: (ManyToManyField to `labels.Label`) The labels this rule is associated with. A rule can be linked to multiple labels, or none if it's a general rule.
*   **Admin Management**: Rules are managed through the Django admin panel. Here, you can define the rule's name, description, status, select its trigger, and associate labels. Crucially, you also define its conditions and actions in inline sections.

### `RuleCondition`

Defines a specific condition that must be met for a rule to be triggered. A rule can have multiple conditions, and all conditions must be true (logical AND) for the rule's actions to execute.

*   **Fields**:
    *   `rule`: (ForeignKey to `Rule`) The rule this condition belongs to.
    *   `entity`: (CharField) The type of entity being evaluated.
        *   Choices: `Professional`, `Customer`, `Service`, `Item`, `Price`, `Order` (derived from `labels.models.LABEL_TYPES`).
    *   `operator`: (CharField) The comparison operator.
        *   Choices: `HAS_LABEL`, `NOT_LABEL`.
    *   `label`: (ForeignKey to `labels.Label`) The specific label to check for with the chosen operator.
*   **Admin Management**: Rule Conditions are managed inline within the `Rule` creation/editing page in the admin panel. For each condition, you specify the entity, the operator, and the relevant label.

### `RuleAction`

Defines an action to be performed if all conditions of a rule are met. A rule can have multiple actions.

*   **Fields**:
    *   `rule`: (ForeignKey to `Rule`) The rule this action belongs to.
    *   `action_type`: (CharField) The type of action to perform.
        *   Choices: `DISCOUNT`, `STATUS_CHANGE`.
    *   `action_params`: (JSONField) A JSON object containing parameters needed for the action.
        *   Example for `DISCOUNT`: `{"discount_percentage": 10}`
        *   Example for `STATUS_CHANGE`: `{"new_status": "active"}`
*   **Admin Management**: Rule Actions are managed inline within the `Rule` creation/editing page in the admin panel. For each action, you select the action type and provide the necessary parameters in JSON format.

## Admin Panel Usage

1.  **Access the Admin Panel**: Navigate to your Django admin interface (e.g., `/admin/`).
2.  **Manage Rule Triggers**:
    *   Go to "Rules" -> "Rule Triggers".
    *   Add or modify triggers. Typically, these are set up once.
3.  **Manage Rules**:
    *   Go to "Rules" -> "Rules".
    *   Click "Add Rule".
    *   **Fill in Rule Details**:
        *   `Name`: A clear name for your rule.
        *   `Description`: (Optional)
        *   `Status`: Set to `ENABLED` to activate the rule.
        *   `Trigger`: Select when the rule should be checked.
        *   `Labels`: (Optional) Select any labels this rule directly pertains to.
    *   **Add Rule Conditions**:
        *   In the "Rule Conditions" inline section, click "Add another Rule Condition".
        *   `Entity`: Choose the entity type (e.g., Customer).
        *   `Operator`: Choose `HAS_LABEL` or `NOT_LABEL`.
        *   `Label`: Select the label to check against (e.g., "VIP").
        *   Add more conditions as needed (they will be ANDed).
    *   **Add Rule Actions**:
        *   In the "Rule Actions" inline section, click "Add another Rule Action".
        *   `Action type`: Choose the action (e.g., `DISCOUNT`).
        *   `Action parameters`: Enter the JSON parameters. For a 15% discount: `{"discount_percentage": 15}`. For changing status to "shipped": `{"new_status": "shipped"}`.
        *   Add more actions as needed.
    *   **Save the Rule**.

The system is now set up to allow administrators to define complex rule logic through the Django admin panel. The actual execution of these rules (i.e., applying discounts, changing statuses) will be handled by separate logic that queries these models.
