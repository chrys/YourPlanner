from django.contrib import admin
from .models import Rule, RuleCondition, RuleAction, RuleTrigger

class RuleConditionInline(admin.TabularInline):
    model = RuleCondition
    extra = 1

class RuleActionInline(admin.TabularInline):
    model = RuleAction
    extra = 1

class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'trigger')
    list_filter = ('status', 'trigger')
    search_fields = ('name', 'description')
    inlines = [RuleConditionInline, RuleActionInline]

admin.site.register(Rule, RuleAdmin)
admin.site.register(RuleTrigger)
