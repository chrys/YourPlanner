from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from core.models import TimeStampedModel
from users.models import Agent 

class Order(TimeStampedModel):
    """ Represents an order placed by a Customer. """
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending Confirmation'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        # Add other statuses as needed
    
    class PaymentStatusChoices(models.TextChoices):
        UNPAID = 'UNPAID', 'Unpaid'
        PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially Paid'
        PAID = 'PAID', 'Paid'
        REFUNDED = 'REFUNDED', 'Refunded'
        FAILED = 'FAILED', 'Payment Failed'

    customer = models.ForeignKey(
        'users.Customer', # String notation
        on_delete=models.PROTECT, # Don't delete orders if customer deleted
        related_name='orders', # customer.orders.all()
        null=True,
        blank=True,
    )
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    payment_status = models.CharField(
        max_length=15,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.UNPAID
    )
    # Store total calculated from items, or allow manual override?
    # Defaulting to null=True, blank=True allows calculation later.
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    
    
    template = models.ForeignKey(                      
        'packages.Template',
        on_delete=models.PROTECT,
        null=True,                                      
        blank=True,
        related_name='orders'
    )
    template_guest_count = models.PositiveIntegerField( 
        default=0,                                      
        blank=True
    )
    template_total_amount = models.DecimalField(        
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    currency = models.CharField(max_length=3, default='EUR', blank=True) # Should match item currencies
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about this order")
    labels = models.ManyToManyField(
        'labels.Label',
        blank=True,
        related_name='orders',
        help_text="Optional labels to categorize this order"
    )
    
    assigned_agent = models.ForeignKey(  # CHANGE: Optional agent assigned to this order
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders',  # agent.assigned_orders.all()
        help_text="Agent assigned to handle this order"
    )
    
    # created_at and updated_at are inherited from TimeStampedModel

    def __str__(self):
        return f"Order #{self.pk} by {self.customer} on {self.order_date.strftime('%Y-%m-%d')}"

    def calculate_total(self):
        from django.db.models import F, Sum, DecimalField, ExpressionWrapper
        total = self.items.aggregate(  # type: ignore[attr-defined]  # Changed: Added type ignore comment for dynamic Django reverse relation
            total=Sum(
                ExpressionWrapper(
                    F('quantity') * F('price_amount_at_order'), # This correctly uses pre-discount amount
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )['total'] or Decimal('0.00')
        self.total_amount = total
        # self.save(update_fields=['total_amount']) # The view should handle saving the order instance
        return total # Return the total so the view can decide to save or use it

    
    @property
    def order_age(self):
        """
        Returns the age of the order in days.
        """
        return (timezone.now() - self.order_date).days
    
    def can_be_cancelled(self):
        """
        Determines if an order can be cancelled based on its status.
        """
        return self.status in [self.StatusChoices.PENDING, self.StatusChoices.CONFIRMED]

    class Meta:  # type: ignore[misc]  # Changed: Added type ignore for Django Meta override pattern
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['order_date']),
            models.Index(fields=['customer', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['customer'],
                condition=models.Q(status='PENDING'),
                name='unique_pending_order_per_customer'
            ),
        ]
    @property
    def currency_display_symbol(self):
        symbols = {
            'EUR': '€',
            'USD': '$',
            'GBP': '£',
        }
        return symbols.get(self.currency, self.currency)    
    

class OrderItem(TimeStampedModel):
    """ Represents a specific item included within an Order. """
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'
        RETURNED = 'RETURNED', 'Returned'
    
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
        related_name='order_items',
        null=True, # Allow null for items that might not be directly linked
        blank=True, # Useful for cases where item is not directly applicable
    )
    price = models.ForeignKey(
        'services.Price',
        on_delete=models.PROTECT, # Keep record even if price definition changes/deleted
        related_name='order_items'
    )

    # Store the price details AT THE TIME of order for historical accuracy
    quantity = models.PositiveIntegerField(default=1)
    price_amount_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    price_currency_at_order = models.CharField(max_length=3, blank=True, default='EUR')
    price_frequency_at_order = models.CharField(max_length=10) # Store frequency from Price model
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Discount amount applied to this item"
    )
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    position = models.PositiveIntegerField(
        default=0,
        help_text="Position of this item in the order display"
    )
    labels = models.ManyToManyField(
        'labels.Label',
        blank=True,
        related_name='order_items',
        help_text="Optional labels to categorize this order item"
    )
    # created_at is inherited from TimeStampedModel
    # No updated_at needed typically for line items once created?

    def __str__(self):
        item_title = self.item.title if self.item else "No Item"  # Changed: Added null check for item
        return f"{self.quantity} x {item_title} in Order #{self.order.pk}"  # Changed: Use item_title variable

    def save(self, *args, **kwargs):
        # Automatically capture price and related entity details when the item is first added
        if not self.pk and self.price: # If creating and price is set
            self.price_amount_at_order = self.price.amount
            self.price_currency_at_order = self.price.currency
            self.price_frequency_at_order = self.price.frequency
            
            # Populate related item, service, and professional if not already set
            # This makes the model more robust, complementing the view logic.
            if not self.item and self.price.item: # Changed: Use field name instead of item_id
                self.item = self.price.item
            if not self.service and self.price.item and self.price.item.service: # Changed: Use field name instead of service_id
                self.service = self.price.item.service
            if not self.professional and self.price.item and self.price.item.service and self.price.item.service.professional: # Changed: Use field name instead of professional_id
                self.professional = self.price.item.service.professional
                
        super().save(*args, **kwargs)

    @property
    def subtotal_before_discount(self):
        """
        Calculate the subtotal before any discount.
        This is useful for display and for the Order.calculate_total method's logic.
        """
        if self.price_amount_at_order is not None and self.quantity is not None:
            return self.price_amount_at_order * self.quantity
        return Decimal('0.00')

    @property
    def final_price(self): # Your existing final_price is good
        """
        Calculate the final price after discount.
        """
        item_total = self.quantity * self.price_amount_at_order
        return max(Decimal('0.00'), item_total - self.discount_amount)

    class Meta:  # type: ignore[misc]  # Changed: Added type ignore for Django Meta override pattern
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ['order', 'position', 'created_at']
        # Optional: Ensure item from a specific service/pro isn't added twice?
        # constraints = [
        #     models.UniqueConstraint(fields=['order', 'item'], name='unique_order_item')
        # ]


class OrderStatusHistory(TimeStampedModel):
    """
    Tracks the history of status changes for an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(
        max_length=15,
        choices=Order.StatusChoices.choices,
        null=True,
        blank=True
    )
    new_status = models.CharField(
        max_length=15,
        choices=Order.StatusChoices.choices
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_status_changes'
    )
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Order #{self.order.pk} status changed from {self.old_status or 'None'} to {self.new_status}"
    
    class Meta:  # type: ignore[misc]  # Changed: Added type ignore for Django Meta override pattern
        verbose_name = "Order Status History"
        verbose_name_plural = "Order Status Histories"
        ordering = ['-created_at']
