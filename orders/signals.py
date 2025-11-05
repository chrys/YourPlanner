# Changed: Created signals.py to integrate the rule engine with Order creation
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from rules.engine import process_rules


@receiver(post_save, sender=Order)
def process_rules_on_order_creation(sender, instance, created, **kwargs):
    """
    Signal handler that triggers rule processing when an Order is created.
    Changed: Calculates discount on the fly and stores in session for display.
    """
    if created:
        # Changed: Process rules and get discount info without saving to database
        if instance.customer:
            discount_info = process_rules(target_entity=instance, event_code='discount_vip')
            
            # Changed: Store discount info in a cache-like structure if needed for later retrieval
            # (e.g., in a request context or session when accessed from a view)
            if discount_info:
                print(f"Discount calculated for Order #{instance.pk}: {discount_info}")

