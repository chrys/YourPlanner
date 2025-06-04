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
    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.user1 = User.objects.create_user(
            username='professional1_mixin_tests',
            email='pro1_mixin@example.com',
            password='testpassword'
        )
        cls.user2 = User.objects.create_user(
            username='professional2_mixin_tests',
            email='pro2_mixin@example.com',
            password='testpassword'
        )
        cls.regular_user_mixin = User.objects.create_user( # Renamed to avoid conflict if other TestCases use 'regular_user'
            username='regularuser_mixin_tests',
            email='regular_mixin@example.com',
            password='testpassword'
        )
        
        # Create professional profiles
        cls.professional1 = Professional.objects.create(
            user=cls.user1,
            title="Pro1 MixinTester",
            # business_name="Pro1 Business", # Not in model
            # phone_number="1234567890", # Not in model
            # address="123 Pro St" # Not in model
        )
        cls.professional2 = Professional.objects.create(
            user=cls.user2,
            title="Pro2 MixinTester",
            # business_name="Pro2 Business",
            # phone_number="0987654321",
            # address="456 Pro Ave"
        )
        
        # Create service category (though not directly used by all mixin tests, good for completeness)
        cls.category_mixin = ServiceCategory.objects.create(
            name="Test Category Mixins",
            description="Test category for mixin tests"
        )
        
        # Create services
        cls.service1_pro1 = Service.objects.create( # Owned by professional1
            professional=cls.professional1,
            title="Service by Pro1 for Mixin Test",
            description="Test service by professional 1",
            category=cls.category_mixin,
            is_active=True
        )
        
        cls.service2_pro2 = Service.objects.create( # Owned by professional2
            professional=cls.professional2,
            title="Service by Pro2 for Mixin Test",
            description="Test service by professional 2",
            category=cls.category_mixin,
            is_active=True
        )
        
        # Create items (useful for parent/grandparent mixins)
        cls.item1_s1 = Item.objects.create(
            service=cls.service1_pro1,
            title="Item for Service1 Mixin Test"
        )
        
        # Set up clients
        cls.client_pro1 = Client()
        cls.client_pro2 = Client()
        cls.client_regular_mixin = Client()
        
        # Log in users
        cls.client_pro1.login(username='professional1_mixin_tests', password='testpassword')
        cls.client_pro2.login(username='professional2_mixin_tests', password='testpassword')
        cls.client_regular_mixin.login(username='regularuser_mixin_tests', password='testpassword')

    def test_services_TC_V_MIX_001_professional_required_access_granted(self):
        """
        Test Case ID: services_TC_V_MIX_001
        Title: ProfessionalRequiredMixin - Access granted for professional user
        View: ServiceCreateView (uses ProfessionalRequiredMixin)
        """
        response = self.client_pro1.get(reverse('services:service_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_form.html') # Check it reached the view

    def test_services_TC_V_MIX_002_professional_required_access_denied_non_professional(self):
        """
        Test Case ID: services_TC_V_MIX_002
        Title: ProfessionalRequiredMixin - Access denied for non-professional user
        View: ServiceCreateView (uses ProfessionalRequiredMixin)
        """
        response = self.client_regular_mixin.get(reverse('services:service_create'), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:profile_choice'))

        # Check message after redirect
        response_redirected = self.client_regular_mixin.get(reverse('users:profile_choice'))
        messages = list(get_messages(response_redirected.wsgi_request))
        self.assertTrue(any(m.message == "You are not registered as a professional." for m in messages),
                        f"Messages found: {[m.message for m in messages]}")


    def test_services_TC_V_MIX_003_professional_owns_object_access_granted(self):
        """
        Test Case ID: services_TC_V_MIX_003
        Title: ProfessionalOwnsObjectMixin - Access granted for owner
        View: ServiceUpdateView (uses ProfessionalOwnsObjectMixin)
        Object: self.service1_pro1 (owned by self.professional1)
        """
        response = self.client_pro1.get(
            reverse('services:service_update', kwargs={'pk': self.service1_pro1.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_form.html') # Check it reached the view

    def test_services_TC_V_MIX_004_professional_owns_object_access_denied_non_owner(self):
        """
        Test Case ID: services_TC_V_MIX_004
        Title: ProfessionalOwnsObjectMixin - Access denied for non-owner
        View: ServiceUpdateView (uses ProfessionalOwnsObjectMixin)
        Object: self.service1_pro1 (owned by self.professional1, accessed by self.professional2)
        """
        response = self.client_pro2.get(
            reverse('services:service_update', kwargs={'pk': self.service1_pro1.pk}),
            follow=False
        )
        self.assertEqual(response.status_code, 302) # Expecting redirect
        # The mixin redirects to 'services:service_list'
        self.assertRedirects(response, reverse('services:service_list'))

        # Check message after redirect
        response_redirected = self.client_pro2.get(reverse('services:service_list'))
        messages = list(get_messages(response_redirected.wsgi_request))
        # The message in ProfessionalOwnsObjectMixin is "You do not have permission to modify or delete this service."
        # This seems to have a slight mismatch with the test case doc "You do not have permission..."
        # Using the actual message from views.py for now.
        expected_message = "You do not have permission to modify or delete this service."
        self.assertTrue(any(m.message == expected_message for m in messages),
                        f"Expected message '{expected_message}'. Messages found: {[m.message for m in messages]}")

    # Keep existing tests for other mixins, ensure they are well-named
    def test_user_owns_parent_service_mixin_access_granted(self):
        """Test UserOwnsParentServiceMixin grants access to parent service owner for ItemCreateView."""
        response = self.client_pro1.get(
            reverse('services:item_create', kwargs={'service_pk': self.service1_pro1.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/item_form.html')

    def test_user_owns_parent_service_mixin_access_denied_non_owner(self):
        """Test UserOwnsParentServiceMixin denies access to non-owner for ItemCreateView."""
        response = self.client_pro2.get(
            reverse('services:item_create', kwargs={'service_pk': self.service1_pro1.pk}),
            follow=False
        )
        # Expect redirect to service_list or 404 if service not found for user by mixin's dispatch
        # The mixin redirects to services:service_list with a message.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('services:service_list'))

        response_redirected = self.client_pro2.get(reverse('services:service_list'))
        messages = list(get_messages(response_redirected.wsgi_request))
        expected_message = "You do not have permission to access items for this service."
        self.assertTrue(any(m.message == expected_message for m in messages),
                        f"Expected message '{expected_message}'. Messages found: {[m.message for m in messages]}")


    def test_user_owns_grandparent_service_via_item_mixin_access_granted(self):
        """Test UserOwnsGrandparentServiceViaItemMixin grants access for PriceCreateView."""
        response = self.client_pro1.get(
            reverse('services:price_create', kwargs={
                'service_pk': self.service1_pro1.pk,
                'item_pk': self.item1_s1.pk
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/price_form.html')

    def test_user_owns_grandparent_service_via_item_mixin_access_denied_non_owner(self):
        """Test UserOwnsGrandparentServiceViaItemMixin denies access for PriceCreateView to non-owner."""
        response = self.client_pro2.get(
            reverse('services:price_create', kwargs={
                'service_pk': self.service1_pro1.pk, # Pro1's service
                'item_pk': self.item1_s1.pk          # Pro1's item
            }),
            follow=False
        )
        # Expect redirect to service_list or 404 if service/item not found for user by mixin's dispatch
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('services:service_list'))

        response_redirected = self.client_pro2.get(reverse('services:service_list'))
        messages = list(get_messages(response_redirected.wsgi_request))
        expected_message = "You do not have permission to access prices for this item/service."
        self.assertTrue(any(m.message == expected_message for m in messages),
                        f"Expected message '{expected_message}'. Messages found: {[m.message for m in messages]}")


class ServiceViewsTestCase(TestCase):
    """
    Test cases for Service-related views.
    """
    @classmethod
    def setUpTestData(cls):
        # Professional 1 (for general use, owns self.service)
        cls.user = User.objects.create_user(username='pro_user_svtests', email='pro_svtests@example.com', password='testpassword')
        cls.professional = Professional.objects.create(user=cls.user, title="Prof. ServiceView Tester")

        # Professional 2 (for testing ownership boundaries, e.g. in list view)
        cls.user2_svtests = User.objects.create_user(username='pro2_user_svtests', email='pro2_svtests@example.com', password='testpassword')
        cls.professional2 = Professional.objects.create(user=cls.user2_svtests, title="Prof. Two ServiceView Tester")

        cls.category_svtests = ServiceCategory.objects.create(name="Category for SV Tests")

        # Service for Professional 1 (used in SCV_004, detail, update, delete)
        cls.service = Service.objects.create(
            professional=cls.professional, # Owned by self.professional (pro1)
            title="Main Test Service SV",
            category=cls.category_svtests,
            is_active=True
        )
        # Another service for Professional 1 (for list view)
        cls.service_another_by_pro1 = Service.objects.create(
            professional=cls.professional, # Owned by self.professional (pro1)
            title="Another Service by Pro1 SV",
            category=cls.category_svtests,
            is_active=True
        )
        
        # Service for Professional 2 (should not be seen by Professional 1 in their list)
        cls.service_by_pro2 = Service.objects.create(
            professional=cls.professional2,
            title="Service by Pro2 SV",
            category=cls.category_svtests,
            is_active=True
        )

        # Non-professional user (for SCV_002)
        cls.regular_user_svtests = User.objects.create_user(username='reg_user_svtests', email='reg_svtests@example.com', password='testpassword')

    def setUp(self):
        # Client for Professional 1 (self.professional)
        self.client = Client()
        self.client.login(username='pro_user_svtests', password='testpassword')

        # Client for non-logged-in user
        self.guest_client = Client()

        # Client for logged-in, non-professional user (self.regular_user_svtests)
        self.regular_client = Client() # Renamed from self.regular_client_scv for broader use
        self.regular_client.login(username='reg_user_svtests', password='testpassword')

        # Client for Professional 2 (self.professional2) - if needed for specific tests
        self.pro2_client = Client()
        self.pro2_client.login(username='pro2_user_svtests', password='testpassword')


    # TC_V_SLV_001
    def test_services_TC_V_SLV_001_list_access_not_logged_in(self): # Renamed for clarity
        """Test Case ID: services_TC_V_SLV_001 - Access ServiceListView - Not logged in"""
        response = self.guest_client.get(reverse('services:service_list'))
        expected_login_url = reverse('login')
        self.assertRedirects(response, f"{expected_login_url}?next={reverse('services:service_list')}")

    # test_service_list_view (original name) to be RENAMED and REFINED
    def test_services_TC_V_SLV_professional_sees_own_services(self): # Was test_service_list_view
        """ Check professional sees only their services in ServiceListView. """
        response = self.client.get(reverse('services:service_list')) # client is logged in as self.professional
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_list.html')

        context_services = response.context.get('services')
        self.assertIsNotNone(context_services)

        # Check that self.professional's services are present
        self.assertIn(self.service, context_services) # Main Test Service SV
        self.assertIn(self.service_another_by_pro1, context_services) # Another Service by Pro1 SV

        # Check that self.professional2's service is NOT present
        self.assertNotIn(self.service_by_pro2, context_services)

        self.assertEqual(len(context_services), 2)
        self.assertEqual(response.context.get('page_title'), "My Services")

    # PREVIOUSLY IMPLEMENTED SCV tests should be here, using the updated setUpTestData
    # For example:
    def test_services_TC_V_SCV_001_create_access_not_logged_in(self): # Adjusted name
        """Test Case ID: services_TC_V_SCV_001 - Access ServiceCreateView - Not logged in"""
        response = self.guest_client.get(reverse('services:service_create'))
        expected_login_url = reverse('login')
        self.assertRedirects(response, f"{expected_login_url}?next={reverse('services:service_create')}")

    def test_services_TC_V_SCV_002_create_access_logged_in_not_professional(self): # Adjusted name
        """Test Case ID: services_TC_V_SCV_002 - Access ServiceCreateView - Logged in, not professional"""
        response = self.regular_client.get(reverse('services:service_create'), follow=False) # regular_client is non-pro
        self.assertRedirects(response, reverse('users:profile_choice'))
        response_redirected = self.regular_client.get(reverse('users:profile_choice'))
        messages = list(get_messages(response_redirected.wsgi_request))
        self.assertTrue(any(m.message == "You are not registered as a professional." for m in messages))

    def test_services_TC_V_SCV_003_create_get_by_professional(self): # Adjusted name
        """Test Case ID: services_TC_V_SCV_003 - ServiceCreateView GET by professional"""
        response = self.client.get(reverse('services:service_create')) # client is pro1
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_form.html')
        self.assertIsInstance(response.context['form'], ServiceForm)
        self.assertEqual(response.context.get('page_title'), "Create New Service")

    def test_services_TC_V_SCV_004_create_post_valid_data_by_professional(self): # Adjusted name
        """Test Case ID: services_TC_V_SCV_004 - ServiceCreateView POST valid data by professional"""
        service_count = Service.objects.count()
        post_data = {
            'title': 'New Service via POST for SCV004',
            'description': 'Description for SCV004.',
            'category': self.category_svtests.pk, # Use category from common setup
            'is_active': True
        }
        response = self.client.post(reverse('services:service_create'), post_data, follow=False) # client is pro1
        self.assertEqual(Service.objects.count(), service_count + 1)
        new_service = Service.objects.get(title='New Service via POST for SCV004')
        self.assertEqual(new_service.professional, self.professional) # self.professional is pro1
        self.assertRedirects(response, reverse('services:service_list'))
        response_redirected = self.client.get(reverse('services:service_list'))
        messages = list(get_messages(response_redirected.wsgi_request))
        self.assertTrue(any(m.message == "Service created successfully." for m in messages))

    def test_services_TC_V_SCV_005_create_post_invalid_data_by_professional(self): # Adjusted name
        """Test Case ID: services_TC_V_SCV_005 - ServiceCreateView POST invalid data by professional"""
        service_count = Service.objects.count()
        post_data = {'title': '', 'description': 'Invalid SCV005.', 'category': self.category_svtests.pk}
        response = self.client.post(reverse('services:service_create'), post_data) # client is pro1
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_form.html')
        self.assertTrue(response.context['form'].errors)
        self.assertIn('title', response.context['form'].errors)
        self.assertEqual(Service.objects.count(), service_count)

    # Original test_service_detail_view, test_service_update_view, test_service_delete_view
    # should also be here, using the common setUpTestData variables (self.service, self.professional, self.client etc.)
    def test_service_detail_view(self): # Original name, to be handled later
        response = self.client.get(reverse('services:service_detail', kwargs={'pk': self.service.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_detail.html')
        self.assertContains(response, self.service.title)
        self.assertEqual(response.context['service'], self.service)
        self.assertTrue(response.context['user_owns_service'])

    def test_service_update_view(self): # Original name, to be handled later
        response = self.client.post(
            reverse('services:service_update', kwargs={'pk': self.service.pk}),
            {'title': 'Updated Title SV', 'description': 'Updated desc SV', 'category': self.category_svtests.pk, 'is_active': True}
        )
        self.assertRedirects(response, reverse('services:service_detail', kwargs={'pk': self.service.pk}))
        self.service.refresh_from_db()
        self.assertEqual(self.service.title, 'Updated Title SV')

    def test_service_delete_view(self): # Original name, to be handled later
        # Create a new service specifically for this delete test to avoid affecting other tests relying on self.service
        deletable_service = Service.objects.create(professional=self.professional, title="Deletable Service SV", category=self.category_svtests)
        deletable_service_pk = deletable_service.pk

        service_count = Service.objects.filter(professional=self.professional).count()

        response = self.client.post(reverse('services:service_delete', kwargs={'pk': deletable_service_pk}))
        self.assertRedirects(response, reverse('services:service_list'))
        self.assertEqual(Service.objects.filter(professional=self.professional).count(), service_count - 1)
        with self.assertRaises(Service.DoesNotExist):
            Service.objects.get(pk=deletable_service_pk)


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

