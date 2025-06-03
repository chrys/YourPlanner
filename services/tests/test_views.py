from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from users.models import Professional
from services.models import Service, ServiceCategory, Item, Price
from services.forms import ServiceForm, ItemForm, PriceForm
import tempfile
from PIL import Image
from decimal import Decimal

User = get_user_model()

class MixinTestCase(TestCase):
    """
    Test cases for the authorization mixins in the services app.
    """
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            username='professional1',
            email='pro1@example.com',
            password='testpassword'
        )
        self.user2 = User.objects.create_user(
            username='professional2',
            email='pro2@example.com',
            password='testpassword'
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpassword'
        )
        
        # Create professional profiles
        self.professional1 = Professional.objects.create(
            user=self.user1,
            business_name="Pro1 Business",
            phone_number="1234567890",
            address="123 Pro St"
        )
        self.professional2 = Professional.objects.create(
            user=self.user2,
            business_name="Pro2 Business",
            phone_number="0987654321",
            address="456 Pro Ave"
        )
        
        # Create service category
        self.category = ServiceCategory.objects.create(
            name="Test Category",
            description="Test category description"
        )
        
        # Create services
        self.service1 = Service.objects.create(
            professional=self.professional1,
            title="Service by Pro1",
            description="Test service by professional 1",
            category=self.category,
            is_active=True
        )
        
        self.service2 = Service.objects.create(
            professional=self.professional2,
            title="Service by Pro2",
            description="Test service by professional 2",
            category=self.category,
            is_active=True
        )
        
        # Create items
        self.item1 = Item.objects.create(
            service=self.service1,
            title="Item for Service1",
            description="Test item for service 1"
        )
        
        self.item2 = Item.objects.create(
            service=self.service2,
            title="Item for Service2",
            description="Test item for service 2"
        )
        
        # Create prices
        self.price1 = Price.objects.create(
            item=self.item1,
            amount=Decimal('100.00'),
            currency='USD',
            frequency='monthly',
            description="Test price for item 1"
        )
        
        self.price2 = Price.objects.create(
            item=self.item2,
            amount=Decimal('200.00'),
            currency='USD',
            frequency='monthly',
            description="Test price for item 2"
        )
        
        # Set up clients
        self.client1 = Client()
        self.client2 = Client()
        self.regular_client = Client()
        
        # Log in users
        self.client1.login(username='professional1', password='testpassword')
        self.client2.login(username='professional2', password='testpassword')
        self.regular_client.login(username='regularuser', password='testpassword')

    def test_professional_required_mixin(self):
        """Test that ProfessionalRequiredMixin restricts access to non-professionals."""
        # Professional should be able to access service creation
        response = self.client1.get(reverse('services:service_create'))
        self.assertEqual(response.status_code, 200)
        
        # Regular user should be redirected
        response = self.regular_client.get(reverse('services:service_create'))
        self.assertNotEqual(response.status_code, 200)
        # Check for redirect (302) or permission denied (403)
        self.assertIn(response.status_code, [302, 403])

    def test_professional_owns_object_mixin(self):
        """Test that ProfessionalOwnsObjectMixin restricts access to non-owners."""
        # Professional1 should be able to update their own service
        response = self.client1.get(
            reverse('services:service_update', kwargs={'pk': self.service1.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Professional2 should not be able to update Professional1's service
        response = self.client2.get(
            reverse('services:service_update', kwargs={'pk': self.service1.pk})
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 403, 404])

    def test_user_owns_parent_service_mixin(self):
        """Test that UserOwnsParentServiceMixin restricts access to non-owners of parent service."""
        # Professional1 should be able to create an item for their service
        response = self.client1.get(
            reverse('services:item_create', kwargs={'service_pk': self.service1.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Professional2 should not be able to create an item for Professional1's service
        response = self.client2.get(
            reverse('services:item_create', kwargs={'service_pk': self.service1.pk})
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 403, 404])

    def test_user_owns_grandparent_service_via_item_mixin(self):
        """Test that UserOwnsGrandparentServiceViaItemMixin restricts access appropriately."""
        # Professional1 should be able to create a price for their item
        response = self.client1.get(
            reverse('services:price_create', kwargs={
                'service_pk': self.service1.pk,
                'item_pk': self.item1.pk
            })
        )
        self.assertEqual(response.status_code, 200)
        
        # Professional2 should not be able to create a price for Professional1's item
        response = self.client2.get(
            reverse('services:price_create', kwargs={
                'service_pk': self.service1.pk,
                'item_pk': self.item1.pk
            })
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 403, 404])


class ServiceViewsTestCase(TestCase):
    """
    Test cases for Service-related views.
    """
    def setUp(self):
        # Create user and professional
        self.user = User.objects.create_user(
            username='testprofessional',
            email='test@example.com',
            password='testpassword'
        )
        self.professional = Professional.objects.create(
            user=self.user,
            business_name="Test Business",
            phone_number="1234567890",
            address="123 Test St"
        )
        
        # Create category
        self.category = ServiceCategory.objects.create(
            name="Test Category",
            description="Test category description"
        )
        
        # Create service
        self.service = Service.objects.create(
            professional=self.professional,
            title="Test Service",
            description="Test service description",
            category=self.category,
            is_active=True
        )
        
        # Set up client
        self.client = Client()
        self.client.login(username='testprofessional', password='testpassword')

    def test_service_list_view(self):
        """Test the service list view displays services correctly."""
        response = self.client.get(reverse('services:service_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_list.html')
        self.assertContains(response, "Test Service")
        self.assertEqual(len(response.context['services']), 1)

    def test_service_detail_view(self):
        """Test the service detail view displays service details correctly."""
        response = self.client.get(
            reverse('services:service_detail', kwargs={'pk': self.service.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_detail.html')
        self.assertContains(response, "Test Service")
        self.assertEqual(response.context['service'], self.service)
        self.assertTrue(response.context['user_owns_service'])

    def test_service_create_view_get(self):
        """Test the service create view form is displayed correctly."""
        response = self.client.get(reverse('services:service_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_form.html')
        self.assertIsInstance(response.context['form'], ServiceForm)

    def test_service_create_view_post(self):
        """Test creating a new service works correctly."""
        service_count = Service.objects.count()
        response = self.client.post(
            reverse('services:service_create'),
            {
                'title': 'New Test Service',
                'description': 'New test service description',
                'category': self.category.pk,
                'is_active': True
            }
        )
        # Check redirect after successful creation
        self.assertRedirects(response, reverse('services:service_list'))
        # Check service was created
        self.assertEqual(Service.objects.count(), service_count + 1)
        # Check the new service has correct data
        new_service = Service.objects.get(title='New Test Service')
        self.assertEqual(new_service.professional, self.professional)
        self.assertEqual(new_service.description, 'New test service description')

    def test_service_update_view(self):
        """Test updating a service works correctly."""
        response = self.client.post(
            reverse('services:service_update', kwargs={'pk': self.service.pk}),
            {
                'title': 'Updated Service Title',
                'description': 'Updated service description',
                'category': self.category.pk,
                'is_active': True
            }
        )
        # Check redirect after successful update
        self.assertRedirects(
            response, 
            reverse('services:service_detail', kwargs={'pk': self.service.pk})
        )
        # Refresh from database
        self.service.refresh_from_db()
        # Check service was updated
        self.assertEqual(self.service.title, 'Updated Service Title')
        self.assertEqual(self.service.description, 'Updated service description')

    def test_service_delete_view(self):
        """Test deleting a service works correctly."""
        service_count = Service.objects.count()
        response = self.client.post(
            reverse('services:service_delete', kwargs={'pk': self.service.pk})
        )
        # Check redirect after successful deletion
        self.assertRedirects(response, reverse('services:service_list'))
        # Check service was deleted
        self.assertEqual(Service.objects.count(), service_count - 1)
        with self.assertRaises(Service.DoesNotExist):
            Service.objects.get(pk=self.service.pk)


class ItemViewsTestCase(TestCase):
    """
    Test cases for Item-related views.
    """
    def setUp(self):
        # Create user and professional
        self.user = User.objects.create_user(
            username='testprofessional',
            email='test@example.com',
            password='testpassword'
        )
        self.professional = Professional.objects.create(
            user=self.user,
            business_name="Test Business",
            phone_number="1234567890",
            address="123 Test St"
        )
        
        # Create service
        self.service = Service.objects.create(
            professional=self.professional,
            title="Test Service",
            description="Test service description",
            is_active=True
        )
        
        # Create item
        self.item = Item.objects.create(
            service=self.service,
            title="Test Item",
            description="Test item description"
        )
        
        # Set up client
        self.client = Client()
        self.client.login(username='testprofessional', password='testpassword')
        
        # Create a temporary image for testing
        self.image = self._create_test_image()

    def _create_test_image(self):
        """Helper method to create a test image file."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            image = Image.new('RGB', (100, 100), 'white')
            image.save(f, 'JPEG')
            return f.name

    def test_item_list_view(self):
        """Test the item list view displays items correctly."""
        response = self.client.get(
            reverse('services:item_list', kwargs={'service_pk': self.service.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/item_list.html')
        self.assertContains(response, "Test Item")
        self.assertEqual(len(response.context['items']), 1)
        self.assertEqual(response.context['service'], self.service)

    def test_item_detail_view(self):
        """Test the item detail view displays item details correctly."""
        response = self.client.get(
            reverse('services:item_detail', kwargs={
                'service_pk': self.service.pk,
                'pk': self.item.pk
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/item_detail.html')
        self.assertContains(response, "Test Item")
        self.assertEqual(response.context['item'], self.item)
        self.assertEqual(response.context['service'], self.service)
        self.assertTrue(response.context['user_owns_service'])

    def test_item_create_view_get(self):
        """Test the item create view form is displayed correctly."""
        response = self.client.get(
            reverse('services:item_create', kwargs={'service_pk': self.service.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/item_form.html')
        self.assertIsInstance(response.context['form'], ItemForm)
        self.assertEqual(response.context['service'], self.service)

    def test_item_create_view_post(self):
        """Test creating a new item works correctly."""
        item_count = Item.objects.count()
        with open(self.image, 'rb') as img:
            response = self.client.post(
                reverse('services:item_create', kwargs={'service_pk': self.service.pk}),
                {
                    'title': 'New Test Item',
                    'description': 'New test item description',
                    'image': img
                }
            )
        # Check redirect after successful creation
        self.assertRedirects(
            response, 
            reverse('services:service_detail', kwargs={'pk': self.service.pk})
        )
        # Check item was created
        self.assertEqual(Item.objects.count(), item_count + 1)
        # Check the new item has correct data
        new_item = Item.objects.get(title='New Test Item')
        self.assertEqual(new_item.service, self.service)
        self.assertEqual(new_item.description, 'New test item description')
        self.assertTrue(new_item.image)  # Check image was uploaded

    def test_item_update_view(self):
        """Test updating an item works correctly."""
        response = self.client.post(
            reverse('services:item_update', kwargs={
                'service_pk': self.service.pk,
                'pk': self.item.pk
            }),
            {
                'title': 'Updated Item Title',
                'description': 'Updated item description'
            }
        )
        # Check redirect after successful update
        self.assertRedirects(
            response, 
            reverse('services:item_detail', kwargs={
                'service_pk': self.service.pk,
                'pk': self.item.pk
            })
        )
        # Refresh from database
        self.item.refresh_from_db()
        # Check item was updated
        self.assertEqual(self.item.title, 'Updated Item Title')
        self.assertEqual(self.item.description, 'Updated item description')

    def test_item_delete_view(self):
        """Test deleting an item works correctly."""
        item_count = Item.objects.count()
        response = self.client.post(
            reverse('services:item_delete', kwargs={
                'service_pk': self.service.pk,
                'pk': self.item.pk
            })
        )
        # Check redirect after successful deletion
        self.assertRedirects(
            response, 
            reverse('services:service_detail', kwargs={'pk': self.service.pk})
        )
        # Check item was deleted
        self.assertEqual(Item.objects.count(), item_count - 1)
        with self.assertRaises(Item.DoesNotExist):
            Item.objects.get(pk=self.item.pk)


class PriceViewsTestCase(TestCase):
    """
    Test cases for Price-related views.
    """
    def setUp(self):
        # Create user and professional
        self.user = User.objects.create_user(
            username='testprofessional',
            email='test@example.com',
            password='testpassword'
        )
        self.professional = Professional.objects.create(
            user=self.user,
            business_name="Test Business",
            phone_number="1234567890",
            address="123 Test St"
        )
        
        # Create service
        self.service = Service.objects.create(
            professional=self.professional,
            title="Test Service",
            description="Test service description",
            is_active=True
        )
        
        # Create item
        self.item = Item.objects.create(
            service=self.service,
            title="Test Item",
            description="Test item description"
        )
        
        # Create price
        self.price = Price.objects.create(
            item=self.item,
            amount=Decimal('100.00'),
            currency='USD',
            frequency='monthly',
            description="Test price description"
        )
        
        # Set up client
        self.client = Client()
        self.client.login(username='testprofessional', password='testpassword')

    def test_price_list_view(self):
        """Test the price list view displays prices correctly."""
        response = self.client.get(
            reverse('services:price_list', kwargs={
                'service_pk': self.service.pk,
                'item_pk': self.item.pk
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/price_list.html')
        self.assertContains(response, "100.00")
        self.assertEqual(len(response.context['prices']), 1)
        self.assertEqual(response.context['service'], self.service)
        self.assertEqual(response.context['item'], self.item)

    def test_price_detail_view(self):
        """Test the price detail view displays price details correctly."""
        response = self.client.get(
            reverse('services:price_detail', kwargs={
                'service_pk': self.service.pk,
                'item_pk': self.item.pk,
                'pk': self.price.pk
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/price_detail.html')
        self.assertContains(response, "100.00")
        self.assertEqual(response.context['price'], self.price)
        self.assertEqual(response.context['service'], self.service)
        self.assertEqual(response.context['item'], self.item)
        self.assertTrue(response.context['user_owns_service'])

    def test_price_create_view_get(self):
        """Test the price create view form is displayed correctly."""
        response = self.client.get(
            reverse('services:price_create', kwargs={
                'service_pk': self.service.pk,
                'item_pk': self.item.pk
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/price_form.html')
        self.assertIsInstance(response.context['form'], PriceForm)
        self.assertEqual(response.context['service'], self.service)
        self.assertEqual(response.context['item'], self.item)

    def test_price_create_view_post(self):
        """Test creating a new price works correctly."""
        price_count = Price.objects.count()
        response = self.client.post(
            reverse('services:price_create', kwargs={
                'service_pk': self.service.pk,
                'item_pk': self.item.pk
            }),
            {
                'amount': '200.00',
                'currency': 'EUR',
                'frequency': 'yearly',
                'description': 'New test price description',
                'is_active': True
            }
        )
        # Check redirect after successful creation
        self.assertRedirects(
            response, 
            reverse('services:item_detail', kwargs={
                'service_pk': self.service.pk,
                'pk': self.item.pk
            })
        )
        # Check price was created
        self.assertEqual(Price.objects.count(), price_count + 1)
        # Check the new price has correct data
        new_price = Price.objects.get(amount=Decimal('200.00'))
        self.assertEqual(new_price.item, self.item)
        self.assertEqual(new_price.currency, 'EUR')
        self.assertEqual(new_price.frequency, 'yearly')
        self.assertEqual(new_price.description, 'New test price description')

    def test_price_update_view(self):
        """Test updating a price works correctly."""
        response = self.client.post(
            reverse('services:price_update', kwargs={
                'service_pk': self.service.pk,
                'item_pk': self.item.pk,
                'pk': self.price.pk
            }),
            {
                'amount': '150.00',
                'currency': 'GBP',
                'frequency': 'weekly',
                'description': 'Updated price description',
                'is_active': True
            }
        )
        # Check redirect after successful update
        self.assertRedirects(
            response, 
            reverse('services:price_detail', kwargs={
                'service_pk': self.service.pk,
                'item_pk': self.item.pk,
                'pk': self.price.pk
            })
        )
        # Refresh from database
        self.price.refresh_from_db()
        # Check price was updated
        self.assertEqual(self.price.amount, Decimal('150.00'))
        self.assertEqual(self.price.currency, 'GBP')
        self.assertEqual(self.price.frequency, 'weekly')
        self.assertEqual(self.price.description, 'Updated price description')

    def test_price_delete_view(self):
        """Test deleting a price works correctly."""
        price_count = Price.objects.count()
        response = self.client.post(
            reverse('services:price_delete', kwargs={
                'service_pk': self.service.pk,
                'item_pk': self.item.pk,
                'pk': self.price.pk
            })
        )
        # Check redirect after successful deletion
        self.assertRedirects(
            response, 
            reverse('services:item_detail', kwargs={
                'service_pk': self.service.pk,
                'pk': self.item.pk
            })
        )
        # Check price was deleted
        self.assertEqual(Price.objects.count(), price_count - 1)
        with self.assertRaises(Price.DoesNotExist):
            Price.objects.get(pk=self.price.pk)


class AuthorizationTestCase(TestCase):
    """
    Test cases for authorization and permissions in views.
    """
    def setUp(self):
        # Create users
        self.professional_user = User.objects.create_user(
            username='testprofessional',
            email='pro@example.com',
            password='testpassword'
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpassword'
        )
        
        # Create professional profile
        self.professional = Professional.objects.create(
            user=self.professional_user,
            business_name="Test Business",
            phone_number="1234567890",
            address="123 Test St"
        )
        
        # Create service
        self.service = Service.objects.create(
            professional=self.professional,
            title="Test Service",
            description="Test service description",
            is_active=True
        )
        
        # Create item
        self.item = Item.objects.create(
            service=self.service,
            title="Test Item",
            description="Test item description"
        )
        
        # Create price
        self.price = Price.objects.create(
            item=self.item,
            amount=Decimal('100.00'),
            currency='USD',
            frequency='monthly',
            description="Test price description"
        )
        
        # Set up clients
        self.professional_client = Client()
        self.regular_client = Client()
        
        # Log in users
        self.professional_client.login(username='testprofessional', password='testpassword')
        self.regular_client.login(username='regularuser', password='testpassword')

    def test_service_list_access(self):
        """Test access to service list view."""
        # Professional should be able to access their service list
        response = self.professional_client.get(reverse('services:service_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['services']), 1)
        
        # Regular user should get an empty list or be redirected
        response = self.regular_client.get(reverse('services:service_list'))
        self.assertEqual(response.status_code, 200)  # Assuming view doesn't restrict access
        self.assertEqual(len(response.context['services']), 0)  # But shows no services

    def test_service_detail_access(self):
        """Test access to service detail view."""
        # Professional should be able to view their service
        response = self.professional_client.get(
            reverse('services:service_detail', kwargs={'pk': self.service.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Regular user should not be able to view the service detail
        response = self.regular_client.get(
            reverse('services:service_detail', kwargs={'pk': self.service.pk})
        )
        self.assertNotEqual(response.status_code, 200)

    def test_item_detail_access(self):
        """Test access to item detail view."""
        # Professional should be able to view their item
        response = self.professional_client.get(
            reverse('services:item_detail', kwargs={
                'service_pk': self.service.pk,
                'pk': self.item.pk
            })
        )
        self.assertEqual(response.status_code, 200)
        
        # Regular user should not be able to view the item detail
        response = self.regular_client.get(
            reverse('services:item_detail', kwargs={
                'service_pk': self.service.pk,
                'pk': self.item.pk
            })
        )
        self.assertNotEqual(response.status_code, 200)

    def test_price_detail_access(self):
        """Test access to price detail view."""
        # Professional should be able to view their price
        response = self.professional_client.get(
            reverse('services:price_detail', kwargs={
                'service_pk': self.service.pk,
                'item_pk': self.item.pk,
                'pk': self.price.pk
            })
        )
        self.assertEqual(response.status_code, 200)
        
        # Regular user should not be able to view the price detail
        response = self.regular_client.get(
            reverse('services:price_detail', kwargs={
                'service_pk': self.service.pk,
                'item_pk': self.item.pk,
                'pk': self.price.pk
            })
        )
        self.assertNotEqual(response.status_code, 200)


class MessageTestCase(TestCase):
    """
    Test cases for Django messages in views.
    """
    def setUp(self):
        # Create user and professional
        self.user = User.objects.create_user(
            username='testprofessional',
            email='test@example.com',
            password='testpassword'
        )
        self.professional = Professional.objects.create(
            user=self.user,
            business_name="Test Business",
            phone_number="1234567890",
            address="123 Test St"
        )
        
        # Create service
        self.service = Service.objects.create(
            professional=self.professional,
            title="Test Service",
            description="Test service description",
            is_active=True
        )
        
        # Set up client
        self.client = Client()
        self.client.login(username='testprofessional', password='testpassword')

    def test_service_create_success_message(self):
        """Test success message is displayed after creating a service."""
        response = self.client.post(
            reverse('services:service_create'),
            {
                'title': 'New Test Service',
                'description': 'New test service description',
                'is_active': True
            },
            follow=True  # Follow redirects to check messages
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(message.message == "Service created successfully." for message in messages))

    def test_service_update_success_message(self):
        """Test success message is displayed after updating a service."""
        response = self.client.post(
            reverse('services:service_update', kwargs={'pk': self.service.pk}),
            {
                'title': 'Updated Service Title',
                'description': 'Updated service description',
                'is_active': True
            },
            follow=True
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(message.message == "Service updated successfully." for message in messages))

    def test_service_delete_success_message(self):
        """Test success message is displayed after deleting a service."""
        response = self.client.post(
            reverse('services:service_delete', kwargs={'pk': self.service.pk}),
            follow=True
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("deleted successfully" in message.message for message in messages))

