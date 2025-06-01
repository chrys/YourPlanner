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
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_professional_account_view_get_non_professional(self):
        """Test GET request to professional account view for authenticated non-professional user."""
        # Create a standard user (not a Professional)
        basic_user = User.objects.create_user(username='basic', password='testpass')
        self.client.login(username='basic', password='testpass')
        url = reverse('professional-account')
        response = self.client.get(url)
        # Depending on implementation, this might be a 403 or redirect.
        # Assuming a redirect to login or a generic page if not authorized.
        # Or if there's a specific "you are not a professional" page.
        # For now, let's check for non-200, and ideally a redirect or 403.
        self.assertIn(response.status_code, [302, 403])
        if response.status_code == 302:
            # Check if it redirects to login or a 'customer_dashboard' if that exists
            # For now, just checking it's not the professional page by accident
            self.assertNotIn("Your Services", response.url) # A bit indirect

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
        self.assertFormError(response, 'form', 'title', 'This field is required.')
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
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_add_item_to_service_post_valid_data(self):
        """Test POST request to add an item to a service with valid data."""
        service = Service.objects.create(professional=self.professional, title="S2_ValidItem", description="D2", is_active=True)
        url = reverse('service-items', args=[service.id])
        initial_item_count = Item.objects.filter(service=service).count()
        response = self.client.post(url, {
            'title': 'Test Item Valid',
            'description': 'Test Item Desc Valid',
            # Assuming price is optional here or handled separately
        }, follow=True) # follow=True to see the result page
        self.assertEqual(response.status_code, 200) # Usually redirects to the same page (service-items)
        self.assertTrue(Item.objects.filter(title='Test Item Valid', service=service).exists())
        self.assertEqual(Item.objects.filter(service=service).count(), initial_item_count + 1)

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
        self.assertFormError(response, 'form', 'title', 'This field is required.')
        self.assertEqual(Item.objects.filter(service=service).count(), initial_item_count)

    def test_edit_item_post_valid_data(self):
        """Test POST request to edit an item and its price with valid data."""
        service = Service.objects.create(professional=self.professional, title="S3_EditValid", description="D3", is_active=True)
        item = Item.objects.create(service=service, title="Item1_Original", description="DescOriginal")
        # Initial price, assuming the form requires all fields for the active price
        price = Price.objects.create(item=item, amount=10, currency="USD", frequency="ONCE", is_active=True)
        url = reverse('edit-item', args=[item.id])

        response = self.client.post(url, {
            'title': 'Item1 Updated',
            'description': 'Desc Updated',
            'active_price_amount': 25, # field name from original test
            'active_price_currency': 'EUR',
            'active_price_frequency': 'MONTHLY',
        }, follow=True)

        self.assertEqual(response.status_code, 200) # Should redirect to service-items or item detail
        item.refresh_from_db()
        # The price object associated with the item might be a new one or updated one
        # depending on form handling logic for prices (e.g. if it deactivates old and creates new)
        # For simplicity, let's assume the existing active price is updated or a new one is clearly active.
        updated_price = item.prices.get(is_active=True)

        self.assertEqual(item.title, 'Item1 Updated')
        self.assertEqual(item.description, 'Desc Updated')
        self.assertEqual(updated_price.amount, 25)
        self.assertEqual(updated_price.currency, 'EUR')
        self.assertEqual(updated_price.frequency, 'MONTHLY')

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
        self.assertFormError(response, 'form', 'active_price_amount', 'Enter a number.') # Example error message

        item.refresh_from_db()
        current_price = item.prices.get(is_active=True)
        self.assertEqual(current_price.amount, original_price.amount) # Price should not have changed
        self.assertEqual(item.title, "Item_EditPriceTest") # Title should not have changed due to form error

