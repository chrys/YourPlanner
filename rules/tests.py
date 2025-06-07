from django.test import TestCase
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db.models.deletion import ProtectedError

from .models import Rule, RuleCondition, RuleAction, RuleTrigger
from labels.models import Label, LABEL_TYPES

class RuleEngineTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create Labels
        cls.label_vip = Label.objects.create(name='VIP Customer', type='CUSTOMER', color='gold')
        cls.label_new = Label.objects.create(name='New Order', type='ORDER', color='blue')
        cls.label_internal = Label.objects.create(name='Internal Review', type='SERVICE', color='gray')

        # Create RuleTriggers
        cls.trigger_on_creation = RuleTrigger.objects.create(name='On Entity Creation', code='ON_CREATION')
        cls.trigger_daily = RuleTrigger.objects.create(name='Daily Check', code='DAILY')
        cls.trigger_on_label = RuleTrigger.objects.create(name='On Label Link', code='ON_LABEL_LINK')

    def test_create_rule_trigger(self):
        trigger = RuleTrigger.objects.create(name='Monthly Review', code='MONTHLY')
        self.assertEqual(trigger.name, 'Monthly Review')
        self.assertEqual(trigger.code, 'MONTHLY')
        self.assertEqual(str(trigger), 'Monthly Review')
        self.assertEqual(RuleTrigger.objects.count(), 4) # 3 from setUpTestData + 1 new

    def test_create_rule(self):
        rule = Rule.objects.create(
            name='VIP Discount Rule',
            trigger=self.trigger_on_creation,
            status='ENABLED'
        )
        rule.labels.add(self.label_vip)

        self.assertEqual(rule.name, 'VIP Discount Rule')
        self.assertEqual(rule.status, 'ENABLED')
        self.assertEqual(rule.trigger, self.trigger_on_creation)
        self.assertEqual(rule.labels.count(), 1)
        self.assertIn(self.label_vip, rule.labels.all())
        self.assertEqual(str(rule), 'VIP Discount Rule')

        # Test adding multiple labels
        rule_multi_label = Rule.objects.create(
            name='Multi-label Rule',
            trigger=self.trigger_daily
        )
        rule_multi_label.labels.add(self.label_new, self.label_internal)
        self.assertEqual(rule_multi_label.labels.count(), 2)
        self.assertIn(self.label_new, rule_multi_label.labels.all())
        self.assertIn(self.label_internal, rule_multi_label.labels.all())
        self.assertEqual(Rule.objects.count(), 2)

    def test_create_rule_condition(self):
        rule = Rule.objects.create(name='Test Condition Rule', trigger=self.trigger_on_creation)
        condition = RuleCondition.objects.create(
            rule=rule,
            entity='CUSTOMER', # Example from LABEL_TYPES
            operator='HAS_LABEL',
            label=self.label_vip
        )
        self.assertEqual(condition.rule, rule)
        self.assertEqual(condition.entity, 'CUSTOMER')
        self.assertEqual(condition.operator, 'HAS_LABEL')
        self.assertEqual(condition.label, self.label_vip)
        self.assertEqual(str(condition), f"Condition for {rule}: CUSTOMER HAS_LABEL {self.label_vip}")

        # Test different entity and operator
        condition_not_label = RuleCondition.objects.create(
            rule=rule,
            entity='ORDER', # Example from LABEL_TYPES
            operator='NOT_LABEL',
            label=self.label_new
        )
        self.assertEqual(condition_not_label.entity, 'ORDER')
        self.assertEqual(condition_not_label.operator, 'NOT_LABEL')
        self.assertEqual(RuleCondition.objects.count(), 2)

        # Test invalid entity choice (if LABEL_TYPES is strictly enforced by choices)
        # This requires the model field to have choices set for validation to fail at model level
        # If not, this would be a form validation or serializer validation concern.
        # For now, assuming direct model validation might not catch this unless choices are exhaustive and final.

    def test_create_rule_action(self):
        rule = Rule.objects.create(name='Test Action Rule', trigger=self.trigger_daily)
        action_params_discount = {"discount_percentage": 10, "reason": "VIP Welcome"}
        action = RuleAction.objects.create(
            rule=rule,
            action_type='DISCOUNT',
            action_params=action_params_discount
        )
        self.assertEqual(action.rule, rule)
        self.assertEqual(action.action_type, 'DISCOUNT')
        self.assertEqual(action.action_params, action_params_discount)
        self.assertEqual(str(action), f"Action for {rule}: DISCOUNT")

        # Test different action_type and params
        action_params_status = {"new_status": "processed", "notify_user": True}
        action_status_change = RuleAction.objects.create(
            rule=rule,
            action_type='STATUS_CHANGE',
            action_params=action_params_status
        )
        self.assertEqual(action_status_change.action_type, 'STATUS_CHANGE')
        self.assertEqual(action_status_change.action_params, action_params_status)
        self.assertEqual(RuleAction.objects.count(), 2)

    def test_rule_relationships(self):
        rule = Rule.objects.create(name='Complex Rule', trigger=self.trigger_on_label)
        RuleCondition.objects.create(rule=rule, entity='CUSTOMER', operator='HAS_LABEL', label=self.label_vip)
        RuleCondition.objects.create(rule=rule, entity='ORDER', operator='NOT_LABEL', label=self.label_new)
        RuleAction.objects.create(rule=rule, action_type='DISCOUNT', action_params={"discount_value": 5})
        RuleAction.objects.create(rule=rule, action_type='STATUS_CHANGE', action_params={"new_status": "flagged"})

        self.assertEqual(rule.conditions.count(), 2)
        self.assertEqual(rule.actions.count(), 2)

    def test_rule_status_default(self):
        rule = Rule.objects.create(name='Default Status Rule', trigger=self.trigger_on_creation)
        self.assertEqual(rule.status, 'DISABLED') # Default as per model definition

    def test_action_params_json(self):
        rule = Rule.objects.create(name='JSON Params Test Rule', trigger=self.trigger_daily)
        complex_params = {
            "target_entity_id": 123,
            "updates": [
                {"field": "priority", "value": "high"},
                {"field": "assigned_to", "value": "support_team"}
            ],
            "notification_required": True
        }
        action = RuleAction.objects.create(
            rule=rule,
            action_type='STATUS_CHANGE', # Or a more generic type if needed
            action_params=complex_params
        )
        retrieved_action = RuleAction.objects.get(id=action.id)
        self.assertEqual(retrieved_action.action_params, complex_params)
        self.assertTrue(retrieved_action.action_params["notification_required"])
        self.assertEqual(len(retrieved_action.action_params["updates"]), 2)

    def test_label_association_in_rule(self):
        rule = Rule.objects.create(name='Label Association Rule', trigger=self.trigger_on_creation)
        rule.labels.add(self.label_vip, self.label_new)

        retrieved_rule = Rule.objects.get(id=rule.id)
        self.assertEqual(retrieved_rule.labels.count(), 2)
        self.assertIn(self.label_vip, retrieved_rule.labels.all())
        self.assertIn(self.label_new, retrieved_rule.labels.all())

        # Test removing a label
        rule.labels.remove(self.label_new)
        self.assertEqual(retrieved_rule.labels.count(), 1)
        self.assertNotIn(self.label_new, retrieved_rule.labels.all())


    def test_on_delete_cascades_and_protects(self):
        # Test PROTECT for RuleTrigger
        rule_for_trigger_test = Rule.objects.create(name='Rule for Trigger Deletion Test', trigger=self.trigger_on_creation)
        with self.assertRaises(ProtectedError):
            self.trigger_on_creation.delete()

        # Clean up the rule that would prevent trigger deletion if test failed or was different
        rule_for_trigger_test.delete()

        # Test PROTECT for Label in RuleCondition
        rule_for_condition_label_test = Rule.objects.create(name='Rule for Condition Label Deletion', trigger=self.trigger_daily)
        condition_for_label_protect = RuleCondition.objects.create(
            rule=rule_for_condition_label_test,
            entity='CUSTOMER',
            operator='HAS_LABEL',
            label=self.label_vip
        )
        with self.assertRaises(ProtectedError):
            self.label_vip.delete()

        # Clean up the condition and rule
        condition_for_label_protect.delete()
        rule_for_condition_label_test.delete()

        # Test CASCADE for RuleCondition and RuleAction when Rule is deleted
        cascading_rule = Rule.objects.create(name='Cascading Delete Rule', trigger=self.trigger_daily)
        condition_to_cascade = RuleCondition.objects.create(
            rule=cascading_rule, entity='ORDER', operator='HAS_LABEL', label=self.label_new
        )
        action_to_cascade = RuleAction.objects.create(
            rule=cascading_rule, action_type='DISCOUNT', action_params={"amount": 5}
        )

        rule_id = cascading_rule.id
        condition_id = condition_to_cascade.id
        action_id = action_to_cascade.id

        self.assertTrue(Rule.objects.filter(id=rule_id).exists())
        self.assertTrue(RuleCondition.objects.filter(id=condition_id).exists())
        self.assertTrue(RuleAction.objects.filter(id=action_id).exists())

        cascading_rule.delete()

        self.assertFalse(Rule.objects.filter(id=rule_id).exists())
        self.assertFalse(RuleCondition.objects.filter(id=condition_id).exists()) # Should be deleted by cascade
        self.assertFalse(RuleAction.objects.filter(id=action_id).exists())     # Should be deleted by cascade

        # Recreate protected items if other tests need them, or ensure test isolation
        # For setUpTestData, items are generally not deleted, so this is fine.
        # If label_vip was deleted in a non-ProtectedError test, it would affect other tests.
        # Here, we specifically test protection, so the item isn't actually deleted.
        # If we had a test that *successfully* deleted a shared label, we'd need to recreate it or structure tests differently.
        # Since label_vip was protected, it's still there. We can verify:
        self.assertTrue(Label.objects.filter(id=self.label_vip.id).exists())
        self.assertTrue(RuleTrigger.objects.filter(id=self.trigger_on_creation.id).exists())
