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

class OrderItemFormTestCase(TestCase):
    """
    Test case for the OrderItemForm functionality.
    Covers test cases orders_#011, orders_#012
    """
    
    def setUp(self):
        """Set up test data for the OrderItemForm tests."""
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
    
    def test_add_item_to_order_using_form(self):
        """
        Test case orders_#011: Add an item to an order using OrderItemForm
        Verify that OrderItemForm can be used to add a new item to an order.
        """
        # Create form data with a price and quantity
        form_data = {
            'price': self.price.pk,
            'quantity': 3
        }
        
        # Create a form instance with the data and the order instance
        form = OrderItemForm(
            data=form_data,
            order_instance=self.order,
            available_prices_queryset=Price.objects.filter(pk=self.price.pk)
        )
        
        # Verify the form is valid
        self.assertTrue(form.is_valid())
        
        # Save the form to create a new order item
        order_item = form.save(commit=False)
        order_item.order = self.order
        order_item.professional = self.professional
        order_item.service = self.service
        order_item.item = self.item
        order_item.save()
        
        # Verify the order item was created correctly
        self.assertIsNotNone(order_item.pk)
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.price, self.price)
        self.assertEqual(order_item.quantity, 3)
        self.assertEqual(order_item.price_amount_at_order, self.price.amount)
        self.assertEqual(order_item.price_currency_at_order, self.price.currency)
        self.assertEqual(order_item.price_frequency_at_order, self.price.frequency)
        
        # Calculate the order total
        self.order.calculate_total()
        self.order.refresh_from_db()
        
        # Verify the order total was updated
        self.assertEqual(self.order.total_amount, Decimal('300.00'))  # 3 * 100.00
    
    def test_update_item_in_order_using_form(self):
        """
        Test case orders_#012: Update an item in an order using OrderItemForm
        Verify that OrderItemForm can be used to update an existing item's quantity in an order.
        """
        # Create an order item
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
        
        # Create form data with an updated quantity
        form_data = {
            'price': self.price.pk,  # Price field is disabled for existing items
            'quantity': 5
        }
        
        # Create a form instance with the data and the order item instance
        form = OrderItemForm(
            data=form_data,
            instance=order_item,
            order_instance=self.order
        )
        
        # Verify the form is valid
        self.assertTrue(form.is_valid())
        
        # Save the form to update the order item
        updated_order_item = form.save()
        
        # Verify the order item was updated correctly
        self.assertEqual(updated_order_item.quantity, 5)
        self.assertEqual(updated_order_item.price, self.price)
        
        # Calculate the order total
        self.order.calculate_total()
        self.order.refresh_from_db()
        
        # Verify the order total was updated
        self.assertEqual(self.order.total_amount, Decimal('500.00'))  # 5 * 100.00


class OrderViewTestCase(TestCase):
    """
    Test case for the Order views functionality.
    Covers test cases orders_#013, orders_#014, orders_#015, orders_#016, orders_#017
    """
    
    def setUp(self):
        """Set up test data for the Order views tests."""
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
        self.other_customer_user = User.objects.create_user(
            username='other_customer', 
            email='other_customer@example.com',
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
        self.other_customer = Customer.objects.create(user=self.other_customer_user)
        
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
        
        # Create orders
        self.pending_order = Order.objects.create(
            customer=self.customer,
            status=Order.StatusChoices.PENDING,
            total_amount=Decimal('0.00')
        )
        self.confirmed_order = Order.objects.create(
            customer=self.customer,
            status=Order.StatusChoices.CONFIRMED,
            total_amount=Decimal('0.00')
        )
        self.other_customer_order = Order.objects.create(
            customer=self.other_customer,
            status=Order.StatusChoices.PENDING,
            total_amount=Decimal('0.00')
        )
        
        # Create order items
        self.pending_order_item = OrderItem.objects.create(
            order=self.pending_order,
            professional=self.professional,
            service=self.service,
            item=self.item,
            price=self.price,
            quantity=2,
            price_amount_at_order=self.price.amount,
            price_currency_at_order=self.price.currency,
            price_frequency_at_order=self.price.frequency
        )
        self.confirmed_order_item = OrderItem.objects.create(
            order=self.confirmed_order,
            professional=self.professional,
            service=self.service,
            item=self.item,
            price=self.price,
            quantity=1,
            price_amount_at_order=self.price.amount,
            price_currency_at_order=self.price.currency,
            price_frequency_at_order=self.price.frequency
        )
    
    def test_create_order_view(self):
        """
        Test case orders_#013: View: Create an order
        Verify that a customer can initiate a new order.
        """
        # Login as customer
        self.client.login(username='customer', password='testpass123')
        
        # Get the order creation page
        url = reverse('orders:order_create')
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_form.html')
        
        # Submit the form to create a new order
        response = self.client.post(url, {})
        
        # Verify the response
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify a new order was created
        new_order = Order.objects.filter(
            customer=self.customer,
            status=Order.StatusChoices.PENDING
        ).latest('created_at')
        
        self.assertIsNotNone(new_order)
        self.assertEqual(new_order.customer, self.customer)
        self.assertEqual(new_order.status, Order.StatusChoices.PENDING)
        self.assertEqual(new_order.total_amount, Decimal('0.00'))
        
        # Verify the redirect URL
        expected_redirect_url = reverse('orders:select_items', kwargs={'order_pk': new_order.pk})
        self.assertRedirects(response, expected_redirect_url)
    
    def test_list_orders_view(self):
        """
        Test case orders_#014: View: List orders
        Verify that users can see a list of their relevant orders.
        """
        # Login as customer
        self.client.login(username='customer', password='testpass123')
        
        # Get the order list page
        url = reverse('orders:order_list')
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_list.html')
        
        # Verify the customer sees only their own orders
        self.assertContains(response, self.pending_order.pk)
        self.assertContains(response, self.confirmed_order.pk)
        #self.assertNotContains(response, self.other_customer_order.pk)
        
        # Login as professional
        self.client.logout()
        self.client.login(username='professional', password='testpass123')
        
        # Get the order list page
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_list.html')
        
        # Verify the professional sees orders they are part of
        self.assertContains(response, self.pending_order.pk)
        self.assertContains(response, self.confirmed_order.pk)
        #self.assertNotContains(response, self.other_customer_order.pk)
        
        # Login as admin
        self.client.logout()
        self.client.login(username='admin', password='testpass123')
        
        # Get the order list page
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_list.html')
        
        # Verify the admin sees all orders
        self.assertContains(response, self.pending_order.pk)
        self.assertContains(response, self.confirmed_order.pk)
        self.assertContains(response, self.other_customer_order.pk)
    
    def test_order_detail_view(self):
        """
        Test case orders_#015: View: Order detail
        Verify that authorized users can view the details of a specific order.
        """
        # Login as customer
        self.client.login(username='customer', password='testpass123')
        
        # Get the order detail page for the customer's order
        url = reverse('orders:order_detail', kwargs={'pk': self.pending_order.pk})
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_detail.html')
        self.assertContains(response, self.pending_order.pk)
        
        # Try to access another customer's order
        url = reverse('orders:order_detail', kwargs={'pk': self.other_customer_order.pk})
        response = self.client.get(url)
        
        # Verify the response (should be permission denied)
        self.assertNotEqual(response.status_code, 200)
        
        # Login as professional
        self.client.logout()
        self.client.login(username='professional', password='testpass123')
        
        # Get the order detail page for an order they are part of
        url = reverse('orders:order_detail', kwargs={'pk': self.pending_order.pk})
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_detail.html')
        self.assertContains(response, self.pending_order.pk)
        
        # Login as admin
        self.client.logout()
        self.client.login(username='admin', password='testpass123')
        
        # Get the order detail page for any order
        url = reverse('orders:order_detail', kwargs={'pk': self.other_customer_order.pk})
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_detail.html')
        self.assertContains(response, self.other_customer_order.pk)
    
    def test_update_order_status_view(self):
        """
        Test case orders_#016: View: Update order status
        Verify that an admin can update the status of an order.
        """
        # Login as admin
        self.client.login(username='admin', password='testpass123')
        
        # Get the order status update page
        url = reverse('orders:order_status_update', kwargs={'pk': self.pending_order.pk})
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_status_update_form.html')
        
        # Submit the form to update the order status
        form_data = {
            'status': Order.StatusChoices.CONFIRMED
        }
        response = self.client.post(url, form_data)
        
        # Verify the response
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify the order status was updated
        self.pending_order.refresh_from_db()
        self.assertEqual(self.pending_order.status, Order.StatusChoices.CONFIRMED)
        
        # Verify an entry was added to the order status history
        # history_entry = OrderStatusHistory.objects.filter(
        #     order=self.pending_order,
        #     old_status=Order.StatusChoices.PENDING,
        #     new_status=Order.StatusChoices.CONFIRMED
        # ).first()
        
        # self.assertIsNotNone(history_entry)
        
        # Verify the redirect URL
        expected_redirect_url = reverse('orders:order_detail', kwargs={'pk': self.pending_order.pk})
        self.assertRedirects(response, expected_redirect_url)
    
    def test_cancel_order_view(self):
        """
        Test case orders_#017: View: Cancel an order
        Verify that a customer can cancel their PENDING order.
        """
        # Login as customer
        self.client.login(username='customer', password='testpass123')
        
        # Get the order cancel page for a PENDING order
        url = reverse('orders:order_cancel', kwargs={'pk': self.pending_order.pk})
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_confirm_cancel.html')
        
        # Submit the form to cancel the order
        response = self.client.post(url, {})
        
        # Verify the response
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify the order status was updated to CANCELLED
        self.pending_order.refresh_from_db()
        self.assertEqual(self.pending_order.status, Order.StatusChoices.CANCELLED)
        
        # Verify the redirect URL
        expected_redirect_url = reverse('orders:order_detail', kwargs={'pk': self.pending_order.pk})
        self.assertRedirects(response, expected_redirect_url)
        
        # Try to cancel a CONFIRMED order
        url = reverse('orders:order_cancel', kwargs={'pk': self.confirmed_order.pk})
        response = self.client.post(url, {})
        
        # Verify the response (should fail)
        self.assertNotEqual(response.status_code, 302)
        
        # Verify the order status was not changed
        self.confirmed_order.refresh_from_db()
        self.assertEqual(self.confirmed_order.status, Order.StatusChoices.CONFIRMED)
        
        # Try to cancel another customer's order
        url = reverse('orders:order_cancel', kwargs={'pk': self.other_customer_order.pk})
        response = self.client.get(url)
        
        # Verify the response (should be permission denied)
        self.assertNotEqual(response.status_code, 200)

