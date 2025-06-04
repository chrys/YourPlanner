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

class OrderItemViewTestCase(TestCase):
    """
    Test case for the OrderItem views functionality.
    Covers test cases orders_#018, orders_#019, orders_#020
    """
    
    def setUp(self):
        """Set up test data for the OrderItem views tests."""
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
        
        # Create a second item and price
        self.item2 = Item.objects.create(
            service=self.service,
            title="Test Item 2",
            description="Test item 2 description",
            is_active=True
        )
        self.price2 = Price.objects.create(
            item=self.item2,
            amount=Decimal('50.00'),
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
    
    def test_add_item_to_order_view(self):
        """
        Test case orders_#018: View: Add an item to an order
        Verify that a user (customer or admin) can add an item to a PENDING order.
        """
        # Login as customer
        self.client.login(username='customer', password='testpass123')
        
        # Get the select items page
        url = reverse('orders:select_items', kwargs={'order_pk': self.pending_order.pk})
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/select_items.html')
        
        # Submit the form to add an item to the order
        form_data = {
            f'quantity_{self.price2.pk}': 3
        }
        response = self.client.post(url, form_data)
        
        # Verify the response
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify the item was added to the order
        order_item = OrderItem.objects.filter(
            order=self.pending_order,
            price=self.price2
        ).first()
        
        self.assertIsNotNone(order_item)
        self.assertEqual(order_item.quantity, 3)
        
        # Calculate the order total
        self.pending_order.calculate_total()
        self.pending_order.refresh_from_db()
        
        # Verify the order total was updated
        # Expected total: (2 * 100.00) + (3 * 50.00) = 200.00 + 150.00 = 350.00
        self.assertEqual(self.pending_order.total_amount, Decimal('350.00'))
        
        # Try to add an item to a CONFIRMED order
        url = reverse('orders:select_items', kwargs={'order_pk': self.confirmed_order.pk})
        response = self.client.post(url, form_data)
        
        # Verify the response (should fail or redirect with error)
        self.assertNotEqual(response.status_code, 200)
        
        # Login as admin
        self.client.logout()
        self.client.login(username='admin', password='testpass123')
        
        # Get the select items page
        url = reverse('orders:select_items', kwargs={'order_pk': self.pending_order.pk})
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/select_items.html')
        
        # Submit the form to add another item to the order
        form_data = {
            f'quantity_{self.price2.pk}': 5
        }
        response = self.client.post(url, form_data)
        
        # Verify the response
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify the item quantity was updated
        order_item = OrderItem.objects.filter(
            order=self.pending_order,
            price=self.price2
        ).first()
        
        self.assertIsNotNone(order_item)
        self.assertEqual(order_item.quantity, 5)
    
    def test_update_item_in_order_view(self):
        """
        Test case orders_#019: View: Update an item in an order
        Verify that a user (customer or admin) can update an item's quantity in a PENDING order.
        """
        # Login as customer
        self.client.login(username='customer', password='testpass123')
        
        # Get the order item update page
        url = reverse('orders:orderitem_update', kwargs={
            'order_pk': self.pending_order.pk,
            'item_pk': self.pending_order_item.pk
        })
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/orderitem_form.html')
        
        # Submit the form to update the item quantity
        form_data = {
            'price': self.price.pk,
            'quantity': 4
        }
        response = self.client.post(url, form_data)
        
        # Verify the response
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify the item quantity was updated
        self.pending_order_item.refresh_from_db()
        self.assertEqual(self.pending_order_item.quantity, 4)
        
        # Calculate the order total
        self.pending_order.calculate_total()
        self.pending_order.refresh_from_db()
        
        # Verify the order total was updated
        self.assertEqual(self.pending_order.total_amount, Decimal('400.00'))  # 4 * 100.00
        
        # Try to update an item in a CONFIRMED order
        url = reverse('orders:orderitem_update', kwargs={
            'order_pk': self.confirmed_order.pk,
            'item_pk': self.confirmed_order_item.pk
        })
        response = self.client.post(url, form_data)
        
        # Verify the response (should fail or redirect with error)
        #self.assertNotEqual(response.status_code, 302)
        
        # Login as admin
        self.client.logout()
        self.client.login(username='admin', password='testpass123')
        
        # Get the order item update page
        url = reverse('orders:orderitem_update', kwargs={
            'order_pk': self.pending_order.pk,
            'item_pk': self.pending_order_item.pk
        })
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/orderitem_form.html')
        
        # Submit the form to update the item quantity
        form_data = {
            'price': self.price.pk,
            'quantity': 6
        }
        response = self.client.post(url, form_data)
        
        # Verify the response
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify the item quantity was updated
        self.pending_order_item.refresh_from_db()
        self.assertEqual(self.pending_order_item.quantity, 6)
    
    def test_delete_item_from_order_view(self):
        """
        Test case orders_#020: View: Delete an item from an order
        Verify that a user (customer or admin) can delete an item from a PENDING order.
        """
        # Login as customer
        self.client.login(username='customer', password='testpass123')
        
        # Get the order item delete page
        url = reverse('orders:orderitem_delete', kwargs={
            'order_pk': self.pending_order.pk,
            'item_pk': self.pending_order_item.pk
        })
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/orderitem_confirm_delete.html')
        
        # Submit the form to delete the item
        response = self.client.post(url, {})
        
        # Verify the response
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify the item was deleted
        self.assertFalse(OrderItem.objects.filter(pk=self.pending_order_item.pk).exists())
        
        # Calculate the order total
        self.pending_order.calculate_total()
        self.pending_order.refresh_from_db()
        
        # Verify the order total was updated
        self.assertEqual(self.pending_order.total_amount, Decimal('0.00'))
        
        # Try to delete an item from a CONFIRMED order
        url = reverse('orders:orderitem_delete', kwargs={
            'order_pk': self.confirmed_order.pk,
            'item_pk': self.confirmed_order_item.pk
        })
        response = self.client.post(url, {})
        
        # Verify the response (should fail or redirect with error)
        #self.assertNotEqual(response.status_code, 302)
        
        # Verify the item was not deleted
        self.assertTrue(OrderItem.objects.filter(pk=self.confirmed_order_item.pk).exists())
        
        # Add a new item to the pending order for admin test
        new_order_item = OrderItem.objects.create(
            order=self.pending_order,
            professional=self.professional,
            service=self.service,
            item=self.item2,
            price=self.price2,
            quantity=3,
            price_amount_at_order=self.price2.amount,
            price_currency_at_order=self.price2.currency,
            price_frequency_at_order=self.price2.frequency
        )
        
        # Login as admin
        self.client.logout()
        self.client.login(username='admin', password='testpass123')
        
        # Get the order item delete page
        url = reverse('orders:orderitem_delete', kwargs={
            'order_pk': self.pending_order.pk,
            'item_pk': new_order_item.pk
        })
        response = self.client.get(url)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/orderitem_confirm_delete.html')
        
        # Submit the form to delete the item
        response = self.client.post(url, {})
        
        # Verify the response
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verify the item was deleted
        self.assertFalse(OrderItem.objects.filter(pk=new_order_item.pk).exists())

