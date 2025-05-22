from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class Order(models.Model):
    """ Represents an order placed by a Customer. """
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending Confirmation'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        # Add other statuses as needed

    customer = models.ForeignKey(
        'users.Customer', # String notation
        on_delete=models.PROTECT, # Don't delete orders if customer deleted
        related_name='orders' # customer.orders.all()
    )
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    # Store total calculated from items, or allow manual override?
    # Defaulting to null=True, blank=True allows calculation later.
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    currency = models.CharField(max_length=3, default='EUR') # Should match item currencies
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.customer} on {self.order_date.strftime('%Y-%m-%d')}"

    # Optional: Method to calculate total based on items
    def calculate_total(self):
        from django.db.models import F, Sum, DecimalField, ExpressionWrapper
        total = self.items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('quantity') * F('price_amount_at_order'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )['total'] or Decimal('0.00')
        self.total_amount = total
        self.save(update_fields=['total_amount'])
        return total

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-order_date']


class OrderItem(models.Model):
    """ Represents a specific item included within an Order. """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE, # If order deleted, delete its items
        related_name='items' # order.items.all()
    )
    # Link directly to the specific elements chosen at the time of order
    professional = models.ForeignKey(
        'users.Professional',
        on_delete=models.PROTECT, # Keep record even if professional leaves
        related_name='order_items'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.PROTECT, # Keep record even if service definition changes/deleted
        related_name='order_items'
    )
    item = models.ForeignKey(
        'services.Item',
        on_delete=models.PROTECT, # Keep record even if item definition changes/deleted
        related_name='order_items'
    )
    price = models.ForeignKey(
        'services.Price',
        on_delete=models.PROTECT, # Keep record even if price definition changes/deleted
        related_name='order_items'
    )

    # Store the price details AT THE TIME of order for historical accuracy
    quantity = models.PositiveIntegerField(default=1)
    price_amount_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    price_currency_at_order = models.CharField(max_length=3)
    price_frequency_at_order = models.CharField(max_length=10) # Store frequency from Price model

    created_at = models.DateTimeField(auto_now_add=True)
    # No updated_at needed typically for line items once created?

    def __str__(self):
        return f"{self.quantity} x {self.item.title} in Order #{self.order.pk}"

    def save(self, *args, **kwargs):
        # Automatically capture price details when the item is first added
        if not self.pk and self.price: # If creating and price is set
            self.price_amount_at_order = self.price.amount
            self.price_currency_at_order = self.price.currency
            self.price_frequency_at_order = self.price.frequency
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ['order', 'created_at']
        # Optional: Ensure item from a specific service/pro isn't added twice?
        # constraints = [
        #     models.UniqueConstraint(fields=['order', 'item'], name='unique_order_item')
        # ]