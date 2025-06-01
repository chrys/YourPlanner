from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Professional, Customer # Ensure Customer is imported
from services.models import Service, Item, Price
from django.urls import reverse
from django.conf import settings
from decimal import Decimal

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

    def test_professional_account_view_get_authenticated_pro(self):
        """Test GET request to professional account view for an authenticated professional."""
        url = reverse('professional-account')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Services")

    def test_professional_account_view_get_unauthenticated(self):
        """Test GET request to professional account view for unauthenticated user."""
        self.client.logout()
        url = reverse('professional-account')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # Redirect to login
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={url}")

    def test_professional_account_view_get_non_professional(self):
        """Test GET request to professional account view for authenticated non-professional user."""
        # Create a standard user and explicitly a Customer profile for them
        basic_user = User.objects.create_user(username='basic_customer', email='basic_customer@example.com', password='testpass')
        Customer.objects.create(user=basic_user) # Make them a customer
        self.client.login(username='basic_customer', password='testpass')

        url = reverse('professional-account')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Access Denied")
        self.assertContains(response, "You are not registered as a professional")

    def test_create_service_post_valid_data(self):
        """Test POST request to create a service with valid data."""
        url = reverse('professional-account') # Assumes creation is on the account page
        initial_service_count = Service.objects.count()
        response = self.client.post(url, {
            'title': 'Test Service Valid',
            'description': 'Test Description Valid',
            'is_active': True,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Service.objects.filter(title='Test Service Valid', professional=self.professional).exists())
        self.assertEqual(Service.objects.count(), initial_service_count + 1)

    def test_create_service_post_invalid_data_empty_title(self):
        """Test POST to create a service with an empty title."""
        url = reverse('professional-account')
        initial_service_count = Service.objects.count()
        response = self.client.post(url, {
            'title': '', # Invalid: empty title
            'description': 'Test Desc Invalid',
            'is_active': True,
        }) # No follow=True, we want to check the form errors
        self.assertEqual(response.status_code, 200) # Should re-render the form
        self.assertFormError(response.context['form'], 'title', 'This field is required.')
        self.assertEqual(Service.objects.count(), initial_service_count) # No new service created

    def test_service_items_view_get_for_own_service(self):
        """Test GET request to service items view for a professional's own service."""
        service = Service.objects.create(professional=self.professional, title="S1_Own", description="D1", is_active=True)
        url = reverse('service-items', args=[service.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Items for")
        self.assertContains(response, service.title)

    def test_service_items_view_get_unauthenticated(self):
        """Test GET to service items view for unauthenticated user."""
        service = Service.objects.create(professional=self.professional, title="S_UnauthTest", is_active=True)
        url = reverse('service-items', args=[service.id])
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={url}")

    def test_add_item_to_service_post_valid_data(self):
        """Test POST request to add an item to a service with valid data."""
        service = Service.objects.create(professional=self.professional, title="S2_ValidItem", description="D2", is_active=True)
        url = reverse('service-items', args=[service.id])
        initial_item_count = Item.objects.filter(service=service).count()
        initial_price_count = Price.objects.count()

        post_data = {
            'title': 'Test Item Valid',       # For ItemForm
            'description': 'Test Item Desc Valid',  # For ItemForm
            'amount': '10.99',                # For PriceForm
            'currency': 'USD',                # For PriceForm
            'frequency': Price.FrequencyChoices.ONCE  # For PriceForm (Corrected from ONE_TIME)
        }
        response = self.client.post(url, post_data, follow=True)

        self.assertEqual(response.status_code, 200) # Usually redirects to the same page (service-items)

        # Check if item was created
        self.assertTrue(Item.objects.filter(title='Test Item Valid', service=service).exists())
        self.assertEqual(Item.objects.filter(service=service).count(), initial_item_count + 1)

        # Check if price was created and linked
        new_item = Item.objects.get(title='Test Item Valid', service=service)
        self.assertTrue(Price.objects.filter(item=new_item, amount=10.99, currency='USD', frequency=Price.FrequencyChoices.ONCE).exists())
        self.assertEqual(Price.objects.count(), initial_price_count + 1)

    def test_add_item_to_service_post_invalid_data_empty_title(self):
        """Test POST to add item with an empty title to a service."""
        service = Service.objects.create(professional=self.professional, title="S_InvalidItemAdd", description="D", is_active=True)
        url = reverse('service-items', args=[service.id])
        initial_item_count = Item.objects.filter(service=service).count()
        response = self.client.post(url, {
            'title': '', # Invalid: empty title
            'description': 'Test Item Desc Invalid',
        }) # No follow=True
        self.assertEqual(response.status_code, 200) # Re-renders form
        self.assertFormError(response.context['form'], 'title', 'This field is required.')
        self.assertEqual(Item.objects.filter(service=service).count(), initial_item_count)

    def test_edit_item_post_valid_data(self):
        """Test POST request to edit an item and its price with valid data."""
        service = Service.objects.create(professional=self.professional, title="S3_EditValid", description="D3", is_active=True)
        item = Item.objects.create(service=service, title="Item1_Original", description="DescOriginal")
        # Initial price
        price = Price.objects.create(item=item, amount=Decimal('10.00'), currency="USD", frequency=Price.FrequencyChoices.ONCE, is_active=True)
        url = reverse('edit-item', args=[item.id])

        post_data = {
            'title': 'Item1 Updated',
            'description': 'Desc Updated',
            'amount': '25.00',
            'currency': 'EUR',
            'frequency': Price.FrequencyChoices.MONTHLY
        }
        response = self.client.post(url, post_data) # Removed follow=True

        self.assertEqual(response.status_code, 200)
        # Check context for 'saved' flag which view sets on successful POST
        self.assertTrue(response.context.get('saved'), "View context 'saved' flag not True, forms likely invalid.")

        item.refresh_from_db()
        price.refresh_from_db() # The 'price' instance from setup should be updated

        self.assertEqual(item.title, 'Item1 Updated')
        self.assertEqual(item.description, 'Desc Updated')
        self.assertEqual(price.amount, Decimal('25.00'))
        self.assertEqual(price.currency, 'EUR')
        self.assertEqual(price.frequency, Price.FrequencyChoices.MONTHLY)

    def test_edit_item_post_invalid_data_non_numeric_price(self):
        """Test POST to edit item with a non-numeric price."""
        service = Service.objects.create(professional=self.professional, title="S_EditItemInvalidPrice", is_active=True)
        item = Item.objects.create(service=service, title="Item_EditPriceTest", description="Desc")
        original_price = Price.objects.create(item=item, amount=10, currency="USD", frequency="ONCE", is_active=True)
        url = reverse('edit-item', args=[item.id])

        response = self.client.post(url, {
            'title': 'Item Updated Title',
            'description': 'Desc Updated',
            'active_price_amount': 'not_a_number', # Invalid
            'active_price_currency': 'USD',
            'active_price_frequency': 'ONCE',
        }) # No follow=True

        self.assertEqual(response.status_code, 200) # Re-renders form
        # Assuming the form in context for price errors is 'form'.
        # If edit_item view uses multiple forms in context (e.g., 'item_form', 'price_form'), this might need adjustment.
        # Based on original test, 'form' is the likely key.
        self.assertFormError(response.context['form'], 'active_price_amount', 'Enter a number.')

        item.refresh_from_db()
        current_price = item.prices.get(is_active=True)
        self.assertEqual(current_price.amount, original_price.amount) # Price should not have changed
        self.assertEqual(item.title, "Item_EditPriceTest") # Title should not have changed due to form error

