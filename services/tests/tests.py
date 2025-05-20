from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Professional
from services.models import Service, Item, Price
from django.urls import reverse

User = get_user_model()
'''
These tests cover:
Professional account page loads
Service creation
Service items page loads
Adding an item to a service
Editing an item and its active price
'''
class ServicesAppTests(TestCase):
    def setUp(self):
        # Create a professional user and login
        self.user = User.objects.create_user(username='pro', password='testpass')
        self.professional = Professional.objects.create(user=self.user, title="Pro", specialization="Test", bio="Bio")
        self.client.login(username='pro', password='testpass')

    def test_professional_account_page(self):
        url = reverse('professional-account')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Services")

    def test_create_service(self):
        url = reverse('professional-account')
        response = self.client.post(url, {
            'title': 'Test Service',
            'description': 'Test Description',
            'is_active': True,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Service.objects.filter(title='Test Service', professional=self.professional).exists())

    def test_service_items_page(self):
        service = Service.objects.create(professional=self.professional, title="S1", description="D1", is_active=True)
        url = reverse('service-items', args=[service.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Items for")

    def test_add_item_to_service(self):
        service = Service.objects.create(professional=self.professional, title="S2", description="D2", is_active=True)
        url = reverse('service-items', args=[service.id])
        response = self.client.post(url, {
            'title': 'Test Item',
            'description': 'Test Item Desc',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Item.objects.filter(title='Test Item', service=service).exists())

    def test_edit_item_and_active_price(self):
        service = Service.objects.create(professional=self.professional, title="S3", description="D3", is_active=True)
        item = Item.objects.create(service=service, title="Item1", description="Desc")
        price = Price.objects.create(item=item, amount=10, currency="USD", frequency="ONCE", is_active=True)
        url = reverse('edit-item', args=[item.id])
        # Edit item and price
        response = self.client.post(url, {
            'title': 'Item1 Updated',
            'description': 'Desc Updated',
            'active_price_amount': 25,
            'active_price_currency': 'EUR',
            'active_price_frequency': 'MONTHLY',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        price.refresh_from_db()
        self.assertEqual(item.title, 'Item1 Updated')
        self.assertEqual(price.amount, 25)
        self.assertEqual(price.currency, 'EUR')
        self.assertEqual(price.frequency, 'MONTHLY')

