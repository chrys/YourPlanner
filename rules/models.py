from django.db import models
from django.db.models import JSONField
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

class RuleAction(models.Model):
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(
        max_length=50,
        choices=(('DISCOUNT', 'Discount'), ('STATUS_CHANGE', 'Status Change'))
    )
    action_params = JSONField()

    def __str__(self):
        return f"Action for {self.rule}: {self.action_type}"
