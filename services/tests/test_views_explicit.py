from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from users.models import Professional
from services.models import Service, ServiceCategory, Item, Price
from services.forms import ServiceForm, ItemForm, PriceForm
from decimal import Decimal

User = get_user_model()

class MixinTestCase(TestCase):
    """
    Test cases for the authorization mixins in the services app.
    Each test method corresponds to a specific test case ID from the documentation.
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

    def test_professional_required_mixin_access_granted(self):
        """
        Test Case ID: services_TC_V_MIX_001
        Title: ProfessionalRequiredMixin - Access granted for professional user
        Description: Verify users with a professional profile can access views using this mixin.
        """
        # Professional should be able to access service creation
        response = self.client1.get(reverse('services:service_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_form.html')
        self.assertIsInstance(response.context['form'], ServiceForm)

    def test_professional_required_mixin_access_denied(self):
        """
        Test Case ID: services_TC_V_MIX_002
        Title: ProfessionalRequiredMixin - Access denied for non-professional user
        Description: Verify users without a professional profile are redirected.
        """
        # Regular user should be redirected
        response = self.regular_client.get(reverse('services:service_create'))
        self.assertNotEqual(response.status_code, 200)
        # Check for redirect (302) or permission denied (403)
        self.assertIn(response.status_code, [302, 403])
        
        # If redirected, check for appropriate message
        if response.status_code == 302:
            # Follow the redirect to check for messages
            response = self.regular_client.get(reverse('services:service_create'), follow=True)
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any("not registered as a professional" in str(message) for message in messages))

    def test_professional_owns_object_mixin_access_granted(self):
        """
        Test Case ID: services_TC_V_MIX_003
        Title: ProfessionalOwnsObjectMixin - Access granted for owner
        Description: Verify professional who owns the object can access views using this mixin.
        """
        # Professional1 should be able to update their own service
        response = self.client1.get(
            reverse('services:service_update', kwargs={'pk': self.service1.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_form.html')
        self.assertEqual(response.context['service'], self.service1)

    def test_professional_owns_object_mixin_access_denied(self):
        """
        Test Case ID: services_TC_V_MIX_004
        Title: ProfessionalOwnsObjectMixin - Access denied for non-owner
        Description: Verify professional who does NOT own the object is denied access.
        """
        # Professional2 should not be able to update Professional1's service
        response = self.client2.get(
            reverse('services:service_update', kwargs={'pk': self.service1.pk})
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 403, 404])
        
        # If redirected, check for appropriate message
        if response.status_code == 302:
            # Follow the redirect to check for messages
            response = self.client2.get(
                reverse('services:service_update', kwargs={'pk': self.service1.pk}),
                follow=True
            )
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any("permission" in str(message).lower() for message in messages))

    def test_user_owns_parent_service_mixin_access_granted(self):
        """
        Test Case ID: services_TC_V_MIX_005
        Title: UserOwnsParentServiceMixin - Access granted for owner of parent Service
        Description: Verify professional who owns the parent Service can access Item views.
        """
        # Professional1 should be able to create an item for their service
        response = self.client1.get(
            reverse('services:item_create', kwargs={'service_pk': self.service1.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/item_form.html')
        self.assertEqual(response.context['service'], self.service1)

    def test_user_owns_parent_service_mixin_access_denied(self):
        """
        Test Case ID: services_TC_V_MIX_006
        Title: UserOwnsParentServiceMixin - Access denied for non-owner of parent Service
        Description: Verify professional who does not own the parent Service is denied access to Item views.
        """
        # Professional2 should not be able to create an item for Professional1's service
        response = self.client2.get(
            reverse('services:item_create', kwargs={'service_pk': self.service1.pk})
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 403, 404])
        
        # If redirected, check for appropriate message
        if response.status_code == 302:
            # Follow the redirect to check for messages
            response = self.client2.get(
                reverse('services:item_create', kwargs={'service_pk': self.service1.pk}),
                follow=True
            )
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any("permission" in str(message).lower() for message in messages))

    def test_user_owns_grandparent_service_via_item_mixin_access_granted(self):
        """
        Test Case ID: services_TC_V_MIX_007
        Title: UserOwnsGrandparentServiceViaItemMixin - Access granted
        Description: Verify professional owning grandparent Service (via Item) can access Price views.
        """
        # Professional1 should be able to create a price for their item
        response = self.client1.get(
            reverse('services:price_create', kwargs={
                'service_pk': self.service1.pk,
                'item_pk': self.item1.pk
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/price_form.html')
        self.assertEqual(response.context['service'], self.service1)
        self.assertEqual(response.context['item'], self.item1)

    def test_user_owns_grandparent_service_via_item_mixin_access_denied(self):
        """
        Test Case ID: services_TC_V_MIX_008
        Title: UserOwnsGrandparentServiceViaItemMixin - Access denied for non-owner
        Description: Verify access denied if professional does not own the grandparent Service.
        """
        # Professional2 should not be able to create a price for Professional1's item
        response = self.client2.get(
            reverse('services:price_create', kwargs={
                'service_pk': self.service1.pk,
                'item_pk': self.item1.pk
            })
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 403, 404])
        
        # If redirected, check for appropriate message
        if response.status_code == 302:
            # Follow the redirect to check for messages
            response = self.client2.get(
                reverse('services:price_create', kwargs={
                    'service_pk': self.service1.pk,
                    'item_pk': self.item1.pk
                }),
                follow=True
            )
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any("permission" in str(message).lower() for message in messages))


class ServiceCreateViewTestCase(TestCase):
    """
    Test cases for ServiceCreateView.
    Each test method corresponds to a specific test case ID from the documentation.
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
        
        # Create regular user (non-professional)
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpassword'
        )
        
        # Create category
        self.category = ServiceCategory.objects.create(
            name="Test Category",
            description="Test category description"
        )
        
        # Set up clients
        self.client = Client()
        self.regular_client = Client()

    def test_service_create_view_not_logged_in(self):
        """
        Test Case ID: services_TC_V_SCV_001
        Title: Access ServiceCreateView - Not logged in
        Description: Verify unauthenticated users are redirected to login.
        """
        # Attempt to access service create view without logging in
        response = self.client.get(reverse('services:service_create'))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)  # Redirect status code
        
        # Check that the redirect is to the login page
        self.assertIn('login', response.url)

    def test_service_create_view_logged_in_not_professional(self):
        """
        Test Case ID: services_TC_V_SCV_002
        Title: Access ServiceCreateView - Logged in, not professional
        Description: Verify logged-in non-professional users are redirected.
        """
        # Log in as regular user
        self.regular_client.login(username='regularuser', password='testpassword')
        
        # Attempt to access service create view
        response = self.regular_client.get(reverse('services:service_create'))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)  # Redirect status code
        
        # Follow the redirect to check for messages
        response = self.regular_client.get(reverse('services:service_create'), follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("not registered as a professional" in str(message) for message in messages))

    def test_service_create_view_get_professional(self):
        """
        Test Case ID: services_TC_V_SCV_003
        Title: ServiceCreateView GET request - Logged in, professional
        Description: Verify a logged-in professional user can access the form page.
        """
        # Log in as professional
        self.client.login(username='testprofessional', password='testpassword')
        
        # Access service create view
        response = self.client.get(reverse('services:service_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_form.html')
        self.assertIsInstance(response.context['form'], ServiceForm)
        self.assertEqual(response.context['page_title'], "Create New Service")

    def test_service_create_view_post_valid_data(self):
        """
        Test Case ID: services_TC_V_SCV_004
        Title: ServiceCreateView POST request - Valid data
        Description: Verify creating a new service with valid data.
        """
        # Log in as professional
        self.client.login(username='testprofessional', password='testpassword')
        
        # Count services before creation
        service_count = Service.objects.count()
        
        # Post valid data to create a new service
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
        self.assertEqual(new_service.category, self.category)
        self.assertTrue(new_service.is_active)
        
        # Check success message
        response = self.client.post(
            reverse('services:service_create'),
            {
                'title': 'Another Test Service',
                'description': 'Another test service description',
                'category': self.category.pk,
                'is_active': True
            },
            follow=True
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("created successfully" in str(message) for message in messages))

    def test_service_create_view_post_invalid_data(self):
        """
        Test Case ID: services_TC_V_SCV_005
        Title: ServiceCreateView POST request - Invalid data
        Description: Verify form re-renders with errors for invalid data.
        """
        # Log in as professional
        self.client.login(username='testprofessional', password='testpassword')
        
        # Count services before attempt
        service_count = Service.objects.count()
        
        # Post invalid data (missing required title)
        response = self.client.post(
            reverse('services:service_create'),
            {
                'title': '',  # Empty title (required field)
                'description': 'Test service description',
                'category': self.category.pk,
                'is_active': True
            }
        )
        
        # Check form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_form.html')
        self.assertTrue(response.context['form'].errors)
        self.assertIn('title', response.context['form'].errors)
        
        # Check no service was created
        self.assertEqual(Service.objects.count(), service_count)


class ServiceListViewTestCase(TestCase):
    """
    Test cases for ServiceListView.
    Each test method corresponds to a specific test case ID from the documentation.
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
        
        # Create services for professional1
        self.service1 = Service.objects.create(
            professional=self.professional1,
            title="Service 1 by Pro1",
            description="Test service 1 by professional 1",
            is_active=True
        )
        self.service2 = Service.objects.create(
            professional=self.professional1,
            title="Service 2 by Pro1",
            description="Test service 2 by professional 1",
            is_active=True
        )
        
        # Create service for professional2
        self.service3 = Service.objects.create(
            professional=self.professional2,
            title="Service by Pro2",
            description="Test service by professional 2",
            is_active=True
        )
        
        # Set up clients
        self.client1 = Client()
        self.client2 = Client()
        self.regular_client = Client()

    def test_service_list_view_not_logged_in(self):
        """
        Test Case ID: services_TC_V_SLV_001
        Title: Access ServiceListView - Not logged in
        Description: Verify unauthenticated users are redirected to login.
        """
        # Attempt to access service list view without logging in
        response = self.client1.get(reverse('services:service_list'))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)  # Redirect status code
        
        # Check that the redirect is to the login page
        self.assertIn('login', response.url)

    def test_service_list_view_logged_in_professional(self):
        """
        Test Case ID: services_TC_V_SLV_002
        Title: ServiceListView GET request - Logged in, professional
        Description: Verify professional sees only their services.
        """
        # Log in as professional1
        self.client1.login(username='professional1', password='testpassword')
        
        # Access service list view
        response = self.client1.get(reverse('services:service_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_list.html')
        
        # Check that only professional1's services are in the context
        services = response.context['services']
        self.assertEqual(len(services), 2)
        self.assertIn(self.service1, services)
        self.assertIn(self.service2, services)
        self.assertNotIn(self.service3, services)
        
        # Check other context variables
        self.assertEqual(response.context['professional'], self.professional1)
        self.assertEqual(response.context['page_title'], "My Services")

    def test_service_list_view_logged_in_no_professional_profile(self):
        """
        Test Case ID: services_TC_V_SLV_003
        Title: ServiceListView GET request - Logged in, no professional profile
        Description: Verify user with no professional profile sees an empty list.
        """
        # Log in as regular user
        self.regular_client.login(username='regularuser', password='testpassword')
        
        # Access service list view
        response = self.regular_client.get(reverse('services:service_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_list.html')
        
        # Check that no services are in the context
        services = response.context['services']
        self.assertEqual(len(services), 0)
        
        # Check professional is None in context
        self.assertIsNone(response.context['professional'])


class ServiceDetailViewTestCase(TestCase):
    """
    Test cases for ServiceDetailView.
    Each test method corresponds to a specific test case ID from the documentation.
    """
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(
            username='testprofessional',
            email='test@example.com',
            password='testpassword'
        )
        self.other_user = User.objects.create_user(
            username='otherprofessional',
            email='other@example.com',
            password='testpassword'
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpassword'
        )
        
        # Create professional profiles
        self.professional = Professional.objects.create(
            user=self.user,
            business_name="Test Business",
            phone_number="1234567890",
            address="123 Test St"
        )
        self.other_professional = Professional.objects.create(
            user=self.other_user,
            business_name="Other Business",
            phone_number="0987654321",
            address="456 Other St"
        )
        
        # Create service
        self.service = Service.objects.create(
            professional=self.professional,
            title="Test Service",
            description="Test service description",
            is_active=True
        )
        
        # Set up clients
        self.client = Client()
        self.other_client = Client()
        self.regular_client = Client()

    def test_service_detail_view_not_logged_in(self):
        """
        Test Case ID: services_TC_V_SDV_001
        Title: Access ServiceDetailView - Not logged in
        Description: Verify unauthenticated users are redirected to login.
        """
        # Attempt to access service detail view without logging in
        response = self.client.get(
            reverse('services:service_detail', kwargs={'pk': self.service.pk})
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)  # Redirect status code
        
        # Check that the redirect is to the login page
        self.assertIn('login', response.url)

    def test_service_detail_view_logged_in_owner(self):
        """
        Test Case ID: services_TC_V_SDV_002
        Title: ServiceDetailView GET request - Logged in, owner
        Description: Verify owner can view their service details.
        """
        # Log in as service owner
        self.client.login(username='testprofessional', password='testpassword')
        
        # Access service detail view
        response = self.client.get(
            reverse('services:service_detail', kwargs={'pk': self.service.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service_detail.html')
        
        # Check context variables
        self.assertEqual(response.context['service'], self.service)
        self.assertEqual(response.context['page_title'], self.service.title)
        self.assertTrue(response.context['user_owns_service'])

    def test_service_detail_view_logged_in_other_professional(self):
        """
        Test Case ID: services_TC_V_SDV_003
        Title: ServiceDetailView GET request - Logged in, other professional
        Description: Verify other professionals cannot view the service details.
        """
        # Log in as other professional
        self.other_client.login(username='otherprofessional', password='testpassword')
        
        # Attempt to access service detail view
        response = self.other_client.get(
            reverse('services:service_detail', kwargs={'pk': self.service.pk})
        )
        
        # Check access is denied (either 404 or redirect)
        self.assertNotEqual(response.status_code, 200)

    def test_service_detail_view_logged_in_regular_user(self):
        """
        Test Case ID: services_TC_V_SDV_004
        Title: ServiceDetailView GET request - Logged in, regular user
        Description: Verify regular users cannot view the service details.
        """
        # Log in as regular user
        self.regular_client.login(username='regularuser', password='testpassword')
        
        # Attempt to access service detail view
        response = self.regular_client.get(
            reverse('services:service_detail', kwargs={'pk': self.service.pk})
        )
        
        # Check access is denied (either 404 or redirect)
        self.assertNotEqual(response.status_code, 200)


# Additional test cases would follow the same pattern for:
# - ServiceUpdateView
# - ServiceDeleteView
# - ItemCreateView
# - ItemListView
# - ItemDetailView
# - ItemUpdateView
# - ItemDeleteView
# - PriceCreateView
# - PriceListView
# - PriceDetailView
# - PriceUpdateView
# - PriceDeleteView

# Each test case would be implemented as a separate method with a clear docstring
# indicating the corresponding test case ID from the documentation.

