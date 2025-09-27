from decimal import Decimal
from datetime import timedelta  # Change: allow computing future wedding day for test data

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone  # Change: used to generate future wedding day

from users.models import Customer, Professional
from services.models import Service, Item, Price
from orders.models import Order, OrderItem


class OrderModelTestCase(TestCase):
    """Covers orders_#001 – orders_#005."""

    def setUp(self):
        user_model = get_user_model()
        self.customer_user = user_model.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="testpass123",
        )
        self.professional_user = user_model.objects.create_user(
            username="professional",
            email="professional@example.com",
            password="testpass123",
        )

        future_wedding_day = timezone.now().date() + timedelta(days=30)  # Change: ensure wedding_day satisfies model constraint
        self.customer = Customer.objects.create(user=self.customer_user, wedding_day=future_wedding_day)  # Change: provide required wedding_day field
        self.professional = Professional.objects.create(
            user=self.professional_user,
            title="Test Professional",
            specialization="Testing",
            bio="Test bio",
        )

        self.service = Service.objects.create(
            professional=self.professional,
            title="Test Service",
            description="Test service description",
            is_active=True,
        )
        self.item = Item.objects.create(
            service=self.service,
            title="Test Item",
            description="Test item description",
            is_active=True,
        )
        self.price = Price.objects.create(
            item=self.item,
            amount=Decimal("100.00"),
            currency="EUR",
            frequency="once",
            is_active=True,
        )

        self.order = Order.objects.create(
            customer=self.customer,
            status=Order.StatusChoices.PENDING,
            total_amount=Decimal("0.00"),
        )
        OrderItem.objects.create(
            order=self.order,
            professional=self.professional,
            service=self.service,
            item=self.item,
            price=self.price,
            quantity=2,
            price_amount_at_order=self.price.amount,
            price_currency_at_order=self.price.currency,
            price_frequency_at_order=self.price.frequency,
        )

    def test_create_new_order(self):
        self.order.status = Order.StatusChoices.CONFIRMED  # Change: avoid violating unique pending order constraint
        self.order.save()  # Change: persist status update before creating additional order
        new_order = Order.objects.create(
            customer=self.customer,
            status=Order.StatusChoices.PENDING,
            total_amount=Decimal("0.00"),
        )
        OrderItem.objects.create(
            order=new_order,
            professional=self.professional,
            service=self.service,
            item=self.item,
            price=self.price,
            quantity=1,
            price_amount_at_order=self.price.amount,
            price_currency_at_order=self.price.currency,
            price_frequency_at_order=self.price.frequency,
        )
        new_order.calculate_total()
        new_order.save(update_fields=["total_amount"])  # Change: persist calculated total for assertions
        new_order.refresh_from_db()

        self.assertEqual(
            OrderItem.objects.filter(order=new_order).count(),
            1,
        )
        self.assertEqual(new_order.total_amount, Decimal("100.00"))

    def test_calculate_total_amount(self):
        another_item = Item.objects.create(
            service=self.service,
            title="Test Item 2",
            description="Test item 2 description",
            is_active=True,
        )
        another_price = Price.objects.create(
            item=another_item,
            amount=Decimal("50.00"),
            currency="EUR",
            frequency="once",
            is_active=True,
        )
        OrderItem.objects.create(
            order=self.order,
            professional=self.professional,
            service=self.service,
            item=another_item,
            price=another_price,
            quantity=3,
            price_amount_at_order=another_price.amount,
            price_currency_at_order=another_price.currency,
            price_frequency_at_order=another_price.frequency,
        )

        total = self.order.calculate_total()
        self.order.save(update_fields=["total_amount"])  # Change: persist calculated total amount
        self.order.refresh_from_db()

        expected_total = Decimal("350.00")
        self.assertEqual(total, expected_total)
        self.assertEqual(self.order.total_amount, expected_total)

    def test_can_be_cancelled(self):
        self.order.status = Order.StatusChoices.PENDING
        self.order.save()
        self.assertTrue(self.order.can_be_cancelled())

        self.order.status = Order.StatusChoices.CONFIRMED
        self.order.save()
        self.assertTrue(self.order.can_be_cancelled())

        self.order.status = Order.StatusChoices.IN_PROGRESS
        self.order.save()
        self.assertFalse(self.order.can_be_cancelled())

    def test_change_order_status(self):
        self.assertEqual(self.order.status, Order.StatusChoices.PENDING)

        self.order.status = Order.StatusChoices.CONFIRMED
        self.order.save()
        self.order.refresh_from_db()

        self.assertEqual(self.order.status, Order.StatusChoices.CONFIRMED)

    def test_change_payment_status(self):
        self.assertEqual(
            self.order.payment_status,
            Order.PaymentStatusChoices.UNPAID,
        )

        self.order.payment_status = Order.PaymentStatusChoices.PAID
        self.order.save()
        self.order.refresh_from_db()

        self.assertEqual(
            self.order.payment_status,
            Order.PaymentStatusChoices.PAID,
        )