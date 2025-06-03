from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from django.db import transaction

from users.models import Customer, Professional
from services.models import Service, Item, Price
from orders.models import Order, OrderItem, OrderStatusHistory
from orders.forms import OrderForm, OrderStatusUpdateForm, OrderItemForm

User = get_user_model()

class OrderModelTestCase(TestCase):
    """
    Test case for the Order model functionality.
    Covers test cases orders_#001, orders_#002, orders_#003, orders_#004, orders_#005
    """
    
    def setUp(self):
        """Set up test data for the Order model tests."""
        # Create users
        self.customer_user = User.objects.create_user(
            username='customer', 
            email='customer@example.com',
            password='testpass123'
        )
        self.professional_user = User.objects.create_user(
            username='professional', 
            email='professional@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin', 
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create profiles
        self.customer = Customer.objects.create(user=self.customer_user)
        self.professional = Professional.objects.create(
            user=self.professional_user,
            title="Test Professional",
            specialization="Testing",
            bio="Test bio"
        )
        
        # Create service, item, and price
        self.service = Service.objects.create(
            professional=self.professional,
            title="Test Service",
            description="Test service description",
            is_active=True
        )
        self.item = Item.objects.create(
            service=self.service,
            title="Test Item",
            description="Test item description",
            is_active=True
        )
        self.price = Price.objects.create(
            item=self.item,
            amount=Decimal('100.00'),
            currency="EUR",
            frequency="once",
            is_active=True
        )
        
        # Create an order
        self.order = Order.objects.create(
            customer=self.customer,
            status=Order.StatusChoices.PENDING,
            total_amount=Decimal('0.00')
        )
        
        # Create order items
        self.order_item = OrderItem.objects.create(
            order=self.order,
            professional=self.professional,
            service=self.service,
            item=self.item,
            price=self.price,
            quantity=2,
            price_amount_at_order=self.price.amount,
            price_currency_at_order=self.price.currency,
            price_frequency_at_order=self.price.frequency
        )
    
    def test_create_new_order(self):
        """
        Test case orders_#001: Create a new order
        Verify that a new order can be created with valid data.
        """
        new_order = Order.objects.create(
            customer=self.customer,
            status=Order.StatusChoices.PENDING,
            total_amount=Decimal('0.00')
        )
        
        # Verify the order was created
        self.assertIsNotNone(new_order.pk)
        self.assertEqual(new_order.customer, self.customer)
        self.assertEqual(new_order.status, Order.StatusChoices.PENDING)
        self.assertEqual(new_order.total_amount, Decimal('0.00'))
        
        # Add an item to the order
        order_item = OrderItem.objects.create(
            order=new_order,
            professional=self.professional,
            service=self.service,
            item=self.item,
            price=self.price,
            quantity=1,
            price_amount_at_order=self.price.amount,
            price_currency_at_order=self.price.currency,
            price_frequency_at_order=self.price.frequency
        )
        
        # Verify the item was added correctly
        self.assertEqual(new_order.items.count(), 1)
        self.assertEqual(order_item.order, new_order)
        self.assertEqual(order_item.price_amount_at_order, self.price.amount)
        
        # Calculate the total amount
        new_order.calculate_total()
        new_order.refresh_from_db()
        
        # Verify the total amount is calculated correctly
        self.assertEqual(new_order.total_amount, Decimal('100.00'))
    
    def test_calculate_total_amount(self):
        """
        Test case orders_#002: Calculate total amount of an order
        Verify that the total amount of an order is calculated correctly.
        """
        # Create a second item with a different price
        item2 = Item.objects.create(
            service=self.service,
            title="Test Item 2",
            description="Test item 2 description",
            is_active=True
        )
        price2 = Price.objects.create(
            item=item2,
            amount=Decimal('50.00'),
            currency="EUR",
            frequency="once",
            is_active=True
        )
        
        # Add the second item to the order
        OrderItem.objects.create(
            order=self.order,
            professional=self.professional,
            service=self.service,
            item=item2,
            price=price2,
            quantity=3,
            price_amount_at_order=price2.amount,
            price_currency_at_order=price2.currency,
            price_frequency_at_order=price2.frequency
        )
        
        # Calculate the total amount
        total = self.order.calculate_total()
        
        # Expected total: (2 * 100.00) + (3 * 50.00) = 200.00 + 150.00 = 350.00
        expected_total = Decimal('350.00')
        
        # Verify the total amount is calculated correctly
        self.assertEqual(total, expected_total)
        self.assertEqual(self.order.total_amount, expected_total)
    
    def test_can_be_cancelled(self):
        """
        Test case orders_#003: Check if an order can be cancelled
        Verify that an order can be cancelled only if its status allows cancellation.
        """
        # Test with PENDING status (should be cancellable)
        self.order.status = Order.StatusChoices.PENDING
        self.order.save()
        self.assertTrue(self.order.can_be_cancelled())
        
        # Test with CONFIRMED status (should be cancellable)
        self.order.status = Order.StatusChoices.CONFIRMED
        self.order.save()
        self.assertTrue(self.order.can_be_cancelled())
        
        # Test with IN_PROGRESS status (should not be cancellable)
        self.order.status = Order.StatusChoices.IN_PROGRESS
        self.order.save()
        self.assertFalse(self.order.can_be_cancelled())
        
        # Test with COMPLETED status (should not be cancellable)
        self.order.status = Order.StatusChoices.COMPLETED
        self.order.save()
        self.assertFalse(self.order.can_be_cancelled())
        
        # Test with CANCELLED status (should not be cancellable)
        self.order.status = Order.StatusChoices.CANCELLED
        self.order.save()
        self.assertFalse(self.order.can_be_cancelled())
    
    def test_change_order_status(self):
        """
        Test case orders_#004: Change the status of an order
        Verify that the status of an order can be changed.
        """
        # Initial status is PENDING
        self.assertEqual(self.order.status, Order.StatusChoices.PENDING)
        
        # Change status to CONFIRMED
        self.order.status = Order.StatusChoices.CONFIRMED
        self.order.save()
        
        # Verify the status was changed
        self.assertEqual(self.order.status, Order.StatusChoices.CONFIRMED)
        
        # Verify an entry was added to the order status history
        history_entry = OrderStatusHistory.objects.filter(
            order=self.order,
            old_status=Order.StatusChoices.PENDING,
            new_status=Order.StatusChoices.CONFIRMED
        ).first()
        
        self.assertIsNotNone(history_entry)
        self.assertEqual(history_entry.old_status, Order.StatusChoices.PENDING)
        self.assertEqual(history_entry.new_status, Order.StatusChoices.CONFIRMED)
    
    def test_change_payment_status(self):
        """
        Test case orders_#005: Change the payment status of an order
        Verify that the payment status of an order can be changed.
        """
        # Initial payment status is UNPAID
        self.assertEqual(self.order.payment_status, Order.PaymentStatusChoices.UNPAID)
        
        # Change payment status to PAID
        self.order.payment_status = Order.PaymentStatusChoices.PAID
        self.order.save()
        
        # Verify the payment status was changed
        self.assertEqual(self.order.payment_status, Order.PaymentStatusChoices.PAID)
        
        # Change payment status to REFUNDED
        self.order.payment_status = Order.PaymentStatusChoices.REFUNDED
        self.order.save()
        
        # Verify the payment status was changed
        self.assertEqual(self.order.payment_status, Order.PaymentStatusChoices.REFUNDED)

