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

    def test_select_items_view_get(self):
        url = reverse('select-items')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select Items")

    def test_select_items_add_to_basket(self):
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

    def test_basket_view(self):
        order = Order.objects.create(customer=self.customer, status=Order.StatusChoices.CONFIRMED)
        # Create a second item and price
        item2 = Item.objects.create(service=self.service, title="Item2", description="Second item")
        price1 = Price.objects.create(item=self.item, amount=50, currency="USD", frequency="once", is_active=True)
        price2 = Price.objects.create(item=item2, amount=30, currency="USD", frequency="once", is_active=True)
        OrderItem.objects.create(
            order=order,
            professional=self.professional,
            service=self.service,
            item=self.item,
            price=price1,
            quantity=2,
        )
        OrderItem.objects.create(
            order=order,
            professional=self.professional,
            service=self.service,
            item=item2,
            price=price2,
            quantity=1,
        )
        total = order.calculate_total()
        for oi in order.items.all():
            print(f"Item: {oi.item.title}, qty: {oi.quantity}, price: {oi.price_amount_at_order}")
        self.assertEqual(total, 130)
        order.refresh_from_db()
        self.assertEqual(order.total_amount, 130)
    def test_order_total_calculation(self):
        order = Order.objects.create(customer=self.customer, status=Order.StatusChoices.CONFIRMED)
        item2 = Item.objects.create(service=self.service, title="Item2", description="Second item")
        price1 = Price.objects.create(item=self.item, amount=50, currency="USD", frequency="once", is_active=True)
        price2 = Price.objects.create(item=item2, amount=30, currency="USD", frequency="once", is_active=True)
        OrderItem.objects.create(
            order=order,
            professional=self.professional,
            service=self.service,
            item=self.item,
            price=price1,
            quantity=2,
        )
        OrderItem.objects.create(
            order=order,
            professional=self.professional,
            service=self.service,
            item=item2,
            price=price2,
            quantity=1,
        )
        total = order.calculate_total()
        self.assertEqual(total, 130)
        order.refresh_from_db()
        self.assertEqual(order.total_amount, 130)