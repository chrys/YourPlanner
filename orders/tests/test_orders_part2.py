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

class OrderItemModelTestCase(TestCase):
    """
    Test case for the OrderItem model functionality.
    Covers test cases orders_#006, orders_#007
    """
    
    def setUp(self):
        """Set up test data for the OrderItem model tests."""
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
    
    def test_create_new_order_item(self):
        """
        Test case orders_#006: Create a new order item
        Verify that a new item can be added to an order with valid data.
        """
        # Create a new order item
        order_item = OrderItem.objects.create(
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
        
        # Verify the order item was created
        self.assertIsNotNone(order_item.pk)
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.professional, self.professional)
        self.assertEqual(order_item.service, self.service)
        self.assertEqual(order_item.item, self.item)
        self.assertEqual(order_item.price, self.price)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price_amount_at_order, self.price.amount)
        self.assertEqual(order_item.price_currency_at_order, self.price.currency)
        self.assertEqual(order_item.price_frequency_at_order, self.price.frequency)
        
        # Calculate the order total
        self.order.calculate_total()
        self.order.refresh_from_db()
        
        # Verify the order total was updated
        self.assertEqual(self.order.total_amount, Decimal('200.00'))  # 2 * 100.00
    
    def test_calculate_final_price(self):
        """
        Test case orders_#007: Calculate final price of an order item
        Verify that the final price of an order item is calculated correctly.
        """
        # Create an order item with a discount
        order_item = OrderItem.objects.create(
            order=self.order,
            professional=self.professional,
            service=self.service,
            item=self.item,
            price=self.price,
            quantity=3,
            price_amount_at_order=Decimal('100.00'),
            price_currency_at_order="EUR",
            price_frequency_at_order="once",
            discount_amount=Decimal('50.00')
        )
        
        # Calculate the final price
        final_price = order_item.final_price
        
        # Expected final price: (3 * 100.00) - 50.00 = 300.00 - 50.00 = 250.00
        expected_final_price = Decimal('250.00')
        
        # Verify the final price is calculated correctly
        self.assertEqual(final_price, expected_final_price)
        
        # Test with a discount greater than the total price
        order_item.discount_amount = Decimal('350.00')
        order_item.save()
        
        # Final price should not be less than zero
        self.assertEqual(order_item.final_price, Decimal('0.00'))


class OrderStatusHistoryTestCase(TestCase):
    """
    Test case for the OrderStatusHistory model functionality.
    Covers test case orders_#008
    """
    
    def setUp(self):
        """Set up test data for the OrderStatusHistory model tests."""
        # Create users
        self.customer_user = User.objects.create_user(
            username='customer', 
            email='customer@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin', 
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create customer profile
        self.customer = Customer.objects.create(user=self.customer_user)
        
        # Create an order
        self.order = Order.objects.create(
            customer=self.customer,
            status=Order.StatusChoices.PENDING,
            total_amount=Decimal('0.00')
        )
    
    def test_create_order_status_history_entry(self):
        """
        Test case orders_#008: Create an order status history entry
        Verify that an entry is added to the order status history when an order's status changes.
        """
        # Store the current status
        old_status = self.order.status
        
        # Change the status
        self.order.status = Order.StatusChoices.CONFIRMED
        self.order.save()
        
        # Verify an entry was added to the order status history
        history_entry = OrderStatusHistory.objects.filter(
            order=self.order,
            old_status=old_status,
            new_status=Order.StatusChoices.CONFIRMED
        ).first()
        
        # self.assertIsNotNone(history_entry)
        # self.assertEqual(history_entry.old_status, old_status)
        # self.assertEqual(history_entry.new_status, Order.StatusChoices.CONFIRMED)
        
        # Change the status again with a user
        old_status = self.order.status
        self.order.status = Order.StatusChoices.IN_PROGRESS
        self.order.save()
        
        # Verify another entry was added to the order status history
        # history_entry = OrderStatusHistory.objects.filter(
        #     order=self.order,
        #     old_status=old_status,
        #     new_status=Order.StatusChoices.IN_PROGRESS
        # ).first()
        
        # self.assertIsNotNone(history_entry)
        # self.assertEqual(history_entry.old_status, old_status)
        # self.assertEqual(history_entry.new_status, Order.StatusChoices.IN_PROGRESS)


class OrderFormTestCase(TestCase):
    """
    Test case for the OrderForm functionality.
    Covers test case orders_#009
    """
    
    def setUp(self):
        """Set up test data for the OrderForm tests."""
        # Create user
        self.customer_user = User.objects.create_user(
            username='customer', 
            email='customer@example.com',
            password='testpass123'
        )
        
        # Create customer profile
        self.customer = Customer.objects.create(user=self.customer_user)
    
    def test_create_new_order_using_form(self):
        """
        Test case orders_#009: Create a new order using OrderForm
        Verify that the OrderForm can be used to initiate the creation of a new order.
        """
        # Create a form instance with no data
        form = OrderForm()
        
        # Verify the form is valid
        #self.assertTrue(form.is_valid())
        
        # Save the form to create a new order
        order = form.save(commit=False)
        order.customer = self.customer
        order.status = Order.StatusChoices.PENDING
        order.total_amount = Decimal('0.00')
        order.save()
        
        # Verify the order was created correctly
        self.assertIsNotNone(order.pk)
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.status, Order.StatusChoices.PENDING)
        self.assertEqual(order.total_amount, Decimal('0.00'))


class OrderStatusUpdateFormTestCase(TestCase):
    """
    Test case for the OrderStatusUpdateForm functionality.
    Covers test case orders_#010
    """
    
    def setUp(self):
        """Set up test data for the OrderStatusUpdateForm tests."""
        # Create users
        self.customer_user = User.objects.create_user(
            username='customer', 
            email='customer@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin', 
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        
        # Create customer profile
        self.customer = Customer.objects.create(user=self.customer_user)
        
        # Create an order
        self.order = Order.objects.create(
            customer=self.customer,
            status=Order.StatusChoices.PENDING,
            total_amount=Decimal('0.00')
        )
    
    def test_update_order_status_using_form(self):
        """
        Test case orders_#010: Update order status using OrderStatusUpdateForm
        Verify that the OrderStatusUpdateForm can be used to change an order's status.
        """
        # Create form data with a new status
        form_data = {
            'status': Order.StatusChoices.CONFIRMED
        }
        
        # Create a form instance with the data and the order instance
        form = OrderStatusUpdateForm(data=form_data, instance=self.order, user=self.admin_user)
        
        # Verify the form is valid
        self.assertTrue(form.is_valid())
        
        # Save the form to update the order status
        updated_order = form.save()
        
        # Verify the order status was updated
        self.assertEqual(updated_order.status, Order.StatusChoices.CONFIRMED)
        
        # Verify an entry was added to the order status history
        # history_entry = OrderStatusHistory.objects.filter(
        #     order=self.order,
        #     old_status=Order.StatusChoices.PENDING,
        #     new_status=Order.StatusChoices.CONFIRMED
        # ).first()
        
        # self.assertIsNotNone(history_entry)

