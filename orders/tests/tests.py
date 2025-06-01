from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Customer, Professional, ProfessionalCustomerLink
from services.models import Service, Item, Price
from orders.models import Order, OrderItem
from django.urls import reverse

User = get_user_model()
'''
These tests cover:

Selecting items and updating the basket
Removing items from the basket
Viewing the basket
Order total calculation'''

class OrdersAppTests(TestCase):
    NON_EXISTENT_ITEM_ID = 99999

    def setUp(self):
        # Create users
        self.user = User.objects.create_user(username='customer', password='testpass')
        self.prof_user = User.objects.create_user(username='pro', password='testpass')
        # Create profiles
        self.customer = Customer.objects.create(user=self.user)
        self.professional = Professional.objects.create(user=self.prof_user, title="Pro", specialization="Test", bio="Bio")
        # Link customer and professional
        self.link = ProfessionalCustomerLink.objects.create(
            customer=self.customer,
            professional=self.professional,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        )
        # Create service, item, price
        self.service = Service.objects.create(professional=self.professional, title="Service1", description="Desc", is_active=True)
        self.item = Item.objects.create(service=self.service, title="Item1", description="ItemDesc")
        self.price = Price.objects.create(item=self.item, amount=100, currency="USD", frequency="once", is_active=True)
        # Login customer
        self.client.login(username='customer', password='testpass')

    def test_select_items_view_get_authenticated_user(self):
        """Test GET request to select-items view for authenticated user."""
        url = reverse('select-items')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select Items")

    def test_select_items_view_get_unauthenticated_user(self):
        """Test GET request to select-items view for unauthenticated user."""
        self.client.logout()
        url = reverse('select-items')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_basket_view_get_unauthenticated_user(self):
        """Test GET request to basket view for unauthenticated user."""
        self.client.logout()
        url = reverse('basket') # Assuming 'basket' is the name from urls.py
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_select_items_add_to_basket(self):
        """Test adding items to the basket via POST to select-items view."""
        url = reverse('select-items')
        # Simulate selecting 2 of the item
        response = self.client.post(url, {
            f'item_{self.item.id}': 2
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        order = Order.objects.get(customer=self.customer, status=Order.StatusChoices.CONFIRMED)
        order_item = order.items.get(item=self.item)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price_amount_at_order, self.price.amount)

    def test_select_items_remove_from_basket(self):
        """Test removing items from the basket by setting quantity to 0."""
        # Add item first
        order = Order.objects.create(customer=self.customer, status=Order.StatusChoices.CONFIRMED)
        order_item = OrderItem.objects.create(
            order=order,
            professional=self.professional,
            service=self.service,
            item=self.item,
            price=self.price,
            quantity=2,
            price_amount_at_order=self.price.amount,
            price_currency_at_order=self.price.currency,
            price_frequency_at_order=self.price.frequency
        )
        url = reverse('select-items')
        # Simulate setting quantity to 0 (removal)
        response = self.client.post(url, {
            f'item_{self.item.id}': 0
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertFalse(order.items.filter(item=self.item).exists())

    def test_order_total_calculation_and_basket_items_presence(self):
        """Test calculation of order total and that items appear in basket context."""
        order = Order.objects.create(customer=self.customer, status=Order.StatusChoices.CONFIRMED)
        # Create a second item and price
        item2 = Item.objects.create(service=self.service, title="Item2", description="Second item")
        # Use the existing self.item for the first item
        price1 = Price.objects.create(item=self.item, amount=50, currency="USD", frequency="once", is_active=True)
        price2 = Price.objects.create(item=item2, amount=30, currency="USD", frequency="once", is_active=True)

        oi1 = OrderItem.objects.create(
            order=order,
            professional=self.professional,
            service=self.service,
            item=self.item, # Existing item
            price=price1,
            quantity=2,
            price_amount_at_order=price1.amount, # Make sure to set this
            price_currency_at_order=price1.currency,
            price_frequency_at_order=price1.frequency
        )
        oi2 = OrderItem.objects.create(
            order=order,
            professional=self.professional,
            service=self.service,
            item=item2, # New item
            price=price2,
            quantity=1,
            price_amount_at_order=price2.amount, # Make sure to set this
            price_currency_at_order=price2.currency,
            price_frequency_at_order=price2.frequency
        )

        total = order.calculate_total()
        self.assertEqual(total, 130) # (50*2) + (30*1) = 100 + 30 = 130
        order.refresh_from_db()
        self.assertEqual(order.total_amount, 130)

        # Test item presence in basket (which is part of select-items view context)
        # This part assumes the select-items view will display items from the current order
        url = reverse('select-items')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.title)
        self.assertContains(response, item2.title)
        # Check quantities displayed (this might need specific template tags or context variable structure)
        # For example, if quantities are displayed like "Item1 (2)"
        # self.assertContains(response, f"{self.item.title} ({oi1.quantity})")
        # self.assertContains(response, f"{item2.title} ({oi2.quantity})")


    def test_add_non_existent_item_to_basket(self):
        """Test attempting to add a non-existent item ID to the basket."""
        url = reverse('select-items')
        initial_order_item_count = OrderItem.objects.count()

        # Try to add a non-existent item
        response = self.client.post(url, {
            f'item_{self.NON_EXISTENT_ITEM_ID}': 1
        }, follow=True)

        self.assertEqual(response.status_code, 200) # View should handle gracefully

        # No new OrderItem should be created for the non-existent item
        self.assertEqual(OrderItem.objects.count(), initial_order_item_count)

        # Ensure current order (if any) does not contain this item
        current_order = Order.objects.filter(customer=self.customer, status=Order.StatusChoices.CONFIRMED).first()
        if current_order:
            self.assertFalse(current_order.items.filter(item_id=self.NON_EXISTENT_ITEM_ID).exists())

    def test_calculate_total_for_empty_order(self):
        """Test calculating total for an order with no items."""
        # Ensure no prior confirmed order exists that could interfere
        Order.objects.filter(customer=self.customer, status=Order.StatusChoices.CONFIRMED).delete()

        order = Order.objects.create(customer=self.customer, status=Order.StatusChoices.CONFIRMED)
        self.assertEqual(order.items.count(), 0) # Should be 0 items initially

        total = order.calculate_total()
        self.assertEqual(total, 0)

        order.refresh_from_db()
        self.assertEqual(order.total_amount, 0)