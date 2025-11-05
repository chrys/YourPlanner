from django.db import models
from django.db.models import JSONField
# from labels.models import LABEL_TYPES_ASSOCIATIONS # This will be defined in labels/models.py
# We will import it inside the method to avoid circular dependencies if models are loading
from labels.models import Label, LABEL_TYPES


class RuleTrigger(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)  # e.g., 'ON_CREATION', 'ON_LABEL_LINK', 'DAILY', 'MONTHLY'

    def __str__(self):
        return self.name

class Rule(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=(('ENABLED', 'Enabled'), ('DISABLED', 'Disabled')),
        default='DISABLED'
    )
    trigger = models.ForeignKey(RuleTrigger, on_delete=models.PROTECT)
    labels = models.ManyToManyField(Label, blank=True, related_name='rules')

    def __str__(self):
        return self.name

class RuleCondition(models.Model):
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='conditions')
    entity = models.CharField(max_length=50, choices=LABEL_TYPES)
    operator = models.CharField(
        max_length=20,
        choices=(('HAS_LABEL', 'Has Label'), ('NOT_LABEL', 'Not Label'))
    )
    label = models.ForeignKey(Label, on_delete=models.PROTECT)

    def __str__(self):
        return f"Condition for {self.rule}: {self.entity} {self.operator} {self.label}"

    def entity_class_for_label_type(self):
        from labels.models import get_label_type_associations  # Changed: Use lazy-loaded associations
        # This method assumes LABEL_TYPES_ASSOCIATIONS maps the string codes
        # from LABEL_TYPES to actual model classes.
        # e.g., {'CUSTOMER': CustomerModel, 'PROFESSIONAL': ProfessionalModel}
        associations = get_label_type_associations()  # Changed: Call function to get associations
        klass = associations.get(self.entity)
        if not klass:
            # Fallback or error handling if the entity string doesn't map to a known class
            # This could involve trying to use django.apps.apps.get_model if self.entity
            # is in the format "app_label.ModelName"
            # For now, raise an error or return None if not found.
            # raise ValueError(f"Could not determine model class for entity type: {self.entity}")
            print(f"Warning: Could not determine model class for entity type: {self.entity}")
            return None # Or handle as an error
        return klass

class RuleAction(models.Model):
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(
        max_length=50,
        choices=(('DISCOUNT', 'Discount'), ('STATUS_CHANGE', 'Status Change'))
    )
    action_params = JSONField()

    def __str__(self):
        return f"Action for {self.rule}: {self.action_type}"
