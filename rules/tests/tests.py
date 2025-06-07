from django.test import TestCase
from django.contrib.auth.models import User # Using User as a stand-in for a generic model if needed
from ..models import Rule, RuleCondition, RuleAction, RuleTrigger
from labels.models import Label, LABEL_TYPES, LABEL_TYPES_ASSOCIATIONS
from ..engine import process_rules

# Mock models for testing purposes, to be used with LABEL_TYPES_ASSOCIATIONS
# These should ideally mirror the structure expected by get_entity_labels
class MockCustomer:
    def __init__(self, name="Test Customer"):
        self.name = name
        self.labels = [] # Simulate a 'labels' ManyToManyField

    def __str__(self):
        return self.name

class MockProfessional:
    def __init__(self, name="Test Pro"):
        self.name = name
        self.labels = []

    def __str__(self):
        return self.name

# Update LABEL_TYPES_ASSOCIATIONS for the test environment
# This is crucial for the tests to run correctly with the mock models
LABEL_TYPES_ASSOCIATIONS['CUSTOMER'] = MockCustomer
LABEL_TYPES_ASSOCIATIONS['PROFESSIONAL'] = MockProfessional
# If other types are used in tests, they need to be added here too.

# Mock implementation for get_entity_labels for testing
# This should be consistent with how MockCustomer/MockProfessional store labels
def mock_get_entity_labels(entity_instance):
    if hasattr(entity_instance, 'labels'):
        return entity_instance.labels
    return []

# Original get_entity_labels from engine for monkeypatching
original_get_entity_labels = None

class RuleEngineTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        global original_get_entity_labels
        # Monkey patch get_entity_labels for testing
        # It's important to do this before any rule processing is called
        from .. import engine # Import the engine module
        original_get_entity_labels = engine.get_entity_labels
        engine.get_entity_labels = mock_get_entity_labels

        # --- Create Labels ---
        cls.vip_label = Label.objects.create(name="VIP", label_type="CUSTOMER")
        cls.new_label = Label.objects.create(name="New", label_type="CUSTOMER")
        cls.pro_badge_label = Label.objects.create(name="Pro Badge", label_type="PROFESSIONAL")

        # --- Create RuleTrigger ---
        cls.on_create_trigger = RuleTrigger.objects.create(name="On Creation", code="ON_CREATE")
        cls.on_update_trigger = RuleTrigger.objects.create(name="On Update", code="ON_UPDATE")

        # --- Rule 1: VIP Customer gets a discount on creation ---
        cls.rule_vip_discount = Rule.objects.create(
            name="VIP Discount on Creation",
            status="ENABLED",
            trigger=cls.on_create_trigger
        )
        # This rule applies if the customer is VIP
        RuleCondition.objects.create(
            rule=cls.rule_vip_discount,
            entity="CUSTOMER", # From LABEL_TYPES
            operator="HAS_LABEL",
            label=cls.vip_label
        )
        RuleAction.objects.create(
            rule=cls.rule_vip_discount,
            action_type="APPLY_DISCOUNT",
            action_params={"percentage": 10}
        )

        # --- Rule 2: New Customer (non-VIP) gets welcome email ---
        cls.rule_new_welcome = Rule.objects.create(
            name="New Customer Welcome Email",
            status="ENABLED",
            trigger=cls.on_create_trigger
        )
        RuleCondition.objects.create(
            rule=cls.rule_new_welcome,
            entity="CUSTOMER",
            operator="HAS_LABEL",
            label=cls.new_label
        )
        RuleCondition.objects.create( # Must also NOT be VIP
            rule=cls.rule_new_welcome,
            entity="CUSTOMER",
            operator="NOT_LABEL",
            label=cls.vip_label
        )
        RuleAction.objects.create(
            rule=cls.rule_new_welcome,
            action_type="SEND_EMAIL",
            action_params={"template": "welcome_new_customer"}
        )

        # --- Rule 3: Rule with no conditions (always applies if trigger matches) ---
        cls.rule_always_log = Rule.objects.create(
            name="Log All Creations",
            status="ENABLED",
            trigger=cls.on_create_trigger
        )
        RuleAction.objects.create(
            rule=cls.rule_always_log,
            action_type="LOG_EVENT",
            action_params={"event_type": "entity_creation"}
        )

        # --- Rule 4: Rule specific to Professionals ---
        cls.rule_pro_badge_award = Rule.objects.create(
            name="Award Pro Badge",
            status="ENABLED",
            trigger=cls.on_update_trigger # Different trigger
        )
        cls.rule_pro_badge_award.labels.add(cls.pro_badge_label) # Rule itself is linked to a label
        RuleCondition.objects.create(
            rule=cls.rule_pro_badge_award,
            entity="PROFESSIONAL",
            operator="HAS_LABEL",
            label=cls.pro_badge_label # Condition: Professional must have the pro_badge_label
        )
        RuleAction.objects.create(
            rule=cls.rule_pro_badge_award,
            action_type="AWARD_BADGE",
            action_params={"badge_name": "Top Professional"}
        )

        # --- Rule 5: Disabled Rule ---
        cls.rule_disabled = Rule.objects.create(
            name="Disabled Rule",
            status="DISABLED",
            trigger=cls.on_create_trigger
        )
        RuleCondition.objects.create(
            rule=cls.rule_disabled,
            entity="CUSTOMER",
            operator="HAS_LABEL",
            label=cls.new_label
        )
        RuleAction.objects.create(
            rule=cls.rule_disabled,
            action_type="DO_NOTHING",
            action_params={}
        )

    @classmethod
    def tearDownClass(cls):
        global original_get_entity_labels
        # Restore original get_entity_labels
        from .. import engine
        engine.get_entity_labels = original_get_entity_labels
        super().tearDownClass()

    def setUp(self):
        # Mock the execute_action function to track calls
        self.executed_actions = []
        self.original_execute_action = None

        from .. import engine # Import the engine module where execute_action is defined
        self.original_execute_action = engine.execute_action

        def mock_execute_action(action, target_entity):
            self.executed_actions.append({
                "action_type": action.action_type,
                "params": action.action_params,
                "rule_name": action.rule.name,
                "target_entity_name": str(target_entity)
            })
            # Call original placeholder if needed for print statements, or just pass
            # self.original_execute_action(action, target_entity)
            print(f"Mock Executing action: {action.action_type} for rule {action.rule.name}")

        engine.execute_action = mock_execute_action


    def tearDown(self):
        # Restore original execute_action
        from .. import engine
        engine.execute_action = self.original_execute_action

    def test_vip_customer_discount(self):
        vip_customer = MockCustomer(name="VIP Moira")
        vip_customer.labels.append(self.vip_label) # Moira is VIP

        process_rules(target_entity=vip_customer, event_code="ON_CREATE")

        self.assertTrue(any(
            action["action_type"] == "APPLY_DISCOUNT" and \
            action["rule_name"] == "VIP Discount on Creation"
            for action in self.executed_actions
        ))
        # Ensure welcome email for non-VIPs is NOT sent
        self.assertFalse(any(
            action["action_type"] == "SEND_EMAIL" and \
            action["rule_name"] == "New Customer Welcome Email"
            for action in self.executed_actions
        ))

    def test_new_customer_welcome_email(self):
        new_customer = MockCustomer(name="New Norman")
        new_customer.labels.append(self.new_label) # Norman is New, but not VIP

        process_rules(target_entity=new_customer, event_code="ON_CREATE")

        self.assertTrue(any(
            action["action_type"] == "SEND_EMAIL" and \
            action["rule_name"] == "New Customer Welcome Email"
            for action in self.executed_actions
        ))
        # Ensure VIP discount is NOT applied
        self.assertFalse(any(
            action["action_type"] == "APPLY_DISCOUNT" and \
            action["rule_name"] == "VIP Discount on Creation"
            for action in self.executed_actions
        ))

    def test_rule_with_no_conditions_always_runs(self):
        any_customer = MockCustomer(name="Any Alex")
        # No specific labels needed for the "Log All Creations" rule

        process_rules(target_entity=any_customer, event_code="ON_CREATE")

        self.assertTrue(any(
            action["action_type"] == "LOG_EVENT" and \
            action["rule_name"] == "Log All Creations"
            for action in self.executed_actions
        ))

    def test_disabled_rule_does_not_run(self):
        customer = MockCustomer(name="Regular Rita")
        customer.labels.append(self.new_label)

        process_rules(target_entity=customer, event_code="ON_CREATE")

        self.assertFalse(any(
            action["action_type"] == "DO_NOTHING" and \
            action["rule_name"] == "Disabled Rule"
            for action in self.executed_actions
        ))

    def test_wrong_trigger_no_rules_run(self):
        customer = MockCustomer(name="Updated Ursula")
        customer.labels.append(self.vip_label)

        process_rules(target_entity=customer, event_code="ON_UPDATE") # ON_UPDATE trigger

        # No actions should be executed because customer rules are for ON_CREATE
        # except for rules that might be for ON_UPDATE and match customer type
        # In this setup, rule_pro_badge_award is ON_UPDATE but for PROFESSIONAL.
        # So, for a CUSTOMER entity with ON_UPDATE, no rules should fire.
        relevant_actions = [
            action for action in self.executed_actions
            if action['target_entity_name'] == str(customer)
        ]
        self.assertEqual(len(relevant_actions), 0)


    def test_professional_rule_specific_label_and_trigger(self):
        pro_user = MockProfessional(name="Pro Paula")
        pro_user.labels.append(self.pro_badge_label) # Paula has the pro badge label

        # This rule is also filtered by the rule.labels field
        # process_rules will check if the entity has one of the labels in rule_pro_badge_award.labels

        process_rules(target_entity=pro_user, event_code="ON_UPDATE")

        self.assertTrue(any(
            action["action_type"] == "AWARD_BADGE" and \
            action["rule_name"] == "Award Pro Badge" and \
            action["target_entity_name"] == "Pro Paula"
            for action in self.executed_actions
        ))
        # Ensure no customer rules ran
        self.assertFalse(any(
            action["rule_name"] == "VIP Discount on Creation" for action in self.executed_actions
        ))

    def test_professional_rule_entity_does_not_have_rule_label(self):
        # This professional does not have the 'pro_badge_label' which is on the Rule itself.
        # The rule `rule_pro_badge_award` is associated with `cls.pro_badge_label`.
        # If the entity doesn't have this label, the rule should not be picked up by `process_rules`.
        other_pro = MockProfessional(name="Other Oscar")
        # Oscar does NOT have self.pro_badge_label, which rule_pro_badge_award is tied to.

        process_rules(target_entity=other_pro, event_code="ON_UPDATE")

        self.assertFalse(any(
            action["action_type"] == "AWARD_BADGE" and \
            action["rule_name"] == "Award Pro Badge"
            for action in self.executed_actions
        ), "Action should not run if entity doesn't match rule's own labels.")

    def test_entity_type_mismatch_for_condition(self):
        # A Professional entity being processed by a rule for CUSTOMER entity type
        pro_for_customer_rule = MockProfessional(name="Pro trying Customer rule")
        # It might have labels that customer rules look for, but type is different
        pro_for_customer_rule.labels.append(self.vip_label)

        process_rules(target_entity=pro_for_customer_rule, event_code="ON_CREATE")

        # No actions for customer rules should be executed because the entity is Professional
        self.assertFalse(any(
            action["rule_name"] == "VIP Discount on Creation"
            for action in self.executed_actions
        ))
        self.assertFalse(any(
            action["rule_name"] == "New Customer Welcome Email"
            for action in self.executed_actions
        ))

        # The generic "Log All Creations" rule (rule_always_log) has NO conditions.
        # The rule engine's process_rules function:
        # - Filters rules by trigger.
        # - Filters rules by rule.labels (if entity has one of them). rule_always_log has no labels.
        # - Then checks conditions. rule_always_log has no conditions.
        # Therefore, rule_always_log should still run.
        self.assertTrue(any(
            action["action_type"] == "LOG_EVENT" and \
            action["rule_name"] == "Log All Creations" and \
            action["target_entity_name"] == str(pro_for_customer_rule)
            for action in self.executed_actions
        ), "Log All Creations rule (no conditions) should run for any entity type if trigger matches.")
