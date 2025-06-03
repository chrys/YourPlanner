from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from users.models import Customer, Professional, ProfessionalCustomerLink
from users.forms import ProfessionalChoiceForm

class UserViewsTests(TestCase):
    """
    Test cases for user views functionality.
    These tests correspond to the test cases in the documentation:
    - users_VIEW_001: User Management View - Anonymous User
    - users_VIEW_002: User Management View - Professional User
    - users_VIEW_003: User Management View - Customer Not Linked to Professional
    - users_VIEW_004: User Management View - Customer Not Linked to Professional (GET)
    - users_VIEW_005: User Management View - Customer Linked to Professional
    - users_VIEW_006: User Management View - Professional User
    - users_VIEW_007: User Management View - Customer Chooses Professional (POST)
    - users_VIEW_008: User Profile View - Customer
    - users_VIEW_009: User Profile View - Professional
    - users_VIEW_010: Change Professional View - Access (GET)
    - users_VIEW_011: Change Professional View - Successful Change (POST)
    - users_VIEW_012: Login Functionality
    - users_VIEW_013: Logout Functionality
    - users_VIEW_014: Attempt to Access Profile Page When Not Logged In
    - users_VIEW_015: Attempt to Access Change Professional Page When Not Logged In
    - users_VIEW_016: Attempt to Access Change Professional Page as Customer Not Linked to any Professional
    """
    
    def setUp(self):
        """Set up test data for all test methods."""
        self.client = Client()
        
        # Create a customer user
        self.customer_user = User.objects.create_user(
            username='customer@example.com',
            email='customer@example.com',
            password='password123',
            first_name='Customer',
            last_name='User'
        )
        self.customer = Customer.objects.create(user=self.customer_user)
        
        # Create a professional user
        self.professional_user = User.objects.create_user(
            username='professional@example.com',
            email='professional@example.com',
            password='password123',
            first_name='Professional',
            last_name='User'
        )
        self.professional = Professional.objects.create(
            user=self.professional_user,
            title='Software Engineer'
        )
        
        # Create another professional for testing changes
        self.professional_user2 = User.objects.create_user(
            username='professional2@example.com',
            email='professional2@example.com',
            password='password123',
            first_name='Professional',
            last_name='Two'
        )
        self.professional2 = Professional.objects.create(
            user=self.professional_user2,
            title='Data Scientist'
        )
    
    def test_user_management_view_anonymous_user(self):
        """
        Test Case ID: users_VIEW_001
        Verify that an anonymous user is redirected to login when attempting to access the user management page.
        """
        # Ensure user is not logged in
        self.client.logout()
        
        # Attempt to access user management page
        response = self.client.get(reverse('users:user_management'))
        
        # Verify redirect to login page
        login_url = f"{settings.LOGIN_URL}?next={reverse('users:user_management')}"
        self.assertRedirects(response, login_url)
    
    def test_user_management_view_professional_user(self):
        """
        Test Case ID: users_VIEW_002 and users_VIEW_006
        Verify that a professional user sees the generic management page.
        """
        # Login as professional
        self.client.login(username='professional@example.com', password='password123')
        
        # Access user management page
        response = self.client.get(reverse('users:user_management'))
        
        # Verify response is successful
        self.assertEqual(response.status_code, 200)
        
        # Verify correct template is used
        self.assertTemplateUsed(response, 'users/management.html')
        
        # Verify page title
        self.assertEqual(response.context['page_title'], 'User Management')
    
    def test_user_management_view_customer_not_linked(self):
        """
        Test Case ID: users_VIEW_003 and users_VIEW_004
        Verify that a customer not linked to a professional sees the professional choice form.
        """
        # Login as customer
        self.client.login(username='customer@example.com', password='password123')
        
        # Access user management page
        response = self.client.get(reverse('users:user_management'))
        
        # Verify response is successful
        self.assertEqual(response.status_code, 200)
        
        # Verify correct template is used
        self.assertTemplateUsed(response, 'users/customer_choose_professional.html')
        
        # Verify professional choice form is in context
        self.assertIsInstance(response.context['form'], ProfessionalChoiceForm)
        
        # Verify page title
        self.assertEqual(response.context['page_title'], 'Choose Your Professional')
    
    def test_user_management_view_customer_linked(self):
        """
        Test Case ID: users_VIEW_005
        Verify that a customer linked to a professional sees the customer dashboard.
        """
        # Create link between customer and professional
        ProfessionalCustomerLink.objects.create(
            customer=self.customer,
            professional=self.professional,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        )
        
        # Login as customer
        self.client.login(username='customer@example.com', password='password123')
        
        # Access user management page
        response = self.client.get(reverse('users:user_management'))
        
        # Verify response is successful
        self.assertEqual(response.status_code, 200)
        
        # Verify correct template is used
        self.assertTemplateUsed(response, 'users/customer_dashboard.html')
        
        # Verify professional is in context
        self.assertEqual(response.context['professional'], self.professional)
        
        # Verify page title
        self.assertEqual(response.context['page_title'], 'My Dashboard')
    
    def test_user_management_view_customer_chooses_professional(self):
        """
        Test Case ID: users_VIEW_007
        Verify that a customer can successfully choose a professional via POST.
        """
        # Login as customer
        self.client.login(username='customer@example.com', password='password123')
        
        # Submit form to choose professional
        data = {'professional': self.professional.pk}
        response = self.client.post(reverse('users:user_management'), data)
        
        # Verify redirect to user management page
        self.assertRedirects(response, reverse('users:user_management'))
        
        # Verify link was created
        self.assertTrue(
            ProfessionalCustomerLink.objects.filter(
                customer=self.customer,
                professional=self.professional,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            ).exists()
        )
    
    def test_user_profile_view_customer(self):
        """
        Test Case ID: users_VIEW_008
        Verify that a customer can view their profile.
        """
        # Login as customer
        self.client.login(username='customer@example.com', password='password123')
        
        # Access profile page
        response = self.client.get(reverse('users:profile'))
        
        # Verify response is successful
        self.assertEqual(response.status_code, 200)
        
        # Verify correct template is used
        self.assertTemplateUsed(response, 'users/profile.html')
        
        # Verify customer profile is in context
        self.assertEqual(response.context['customer_profile'], self.customer)
        
        # Verify page title
        self.assertEqual(response.context['page_title'], 'My Profile')
    
    def test_user_profile_view_professional(self):
        """
        Test Case ID: users_VIEW_009
        Verify that a professional can view their profile.
        """
        # Login as professional
        self.client.login(username='professional@example.com', password='password123')
        
        # Access profile page
        response = self.client.get(reverse('users:profile'))
        
        # Verify response is successful
        self.assertEqual(response.status_code, 200)
        
        # Verify correct template is used
        self.assertTemplateUsed(response, 'users/profile.html')
        
        # Verify professional profile is in context
        self.assertEqual(response.context['professional_profile'], self.professional)
        
        # Verify page title
        self.assertEqual(response.context['page_title'], 'My Profile')
    
    def test_change_professional_view_access(self):
        """
        Test Case ID: users_VIEW_010
        Verify that a customer linked to a professional can access the change professional page.
        """
        # Create link between customer and professional
        ProfessionalCustomerLink.objects.create(
            customer=self.customer,
            professional=self.professional,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        )
        
        # Login as customer
        self.client.login(username='customer@example.com', password='password123')
        
        # Access change professional page
        response = self.client.get(reverse('users:change_professional'))
        
        # Verify response is successful
        self.assertEqual(response.status_code, 200)
        
        # Verify correct template is used
        self.assertTemplateUsed(response, 'users/customer_choose_professional.html')
        
        # Verify professional choice form is in context
        self.assertIsInstance(response.context['form'], ProfessionalChoiceForm)
        
        # Verify page title
        self.assertEqual(response.context['page_title'], 'Change Your Professional')
    
    def test_change_professional_view_successful_change(self):
        """
        Test Case ID: users_VIEW_011
        Verify that a customer can successfully change their professional.
        """
        # Create initial link between customer and professional
        ProfessionalCustomerLink.objects.create(
            customer=self.customer,
            professional=self.professional,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        )
        
        # Login as customer
        self.client.login(username='customer@example.com', password='password123')
        
        # Submit form to change professional
        data = {'professional': self.professional2.pk}
        response = self.client.post(reverse('users:change_professional'), data)
        
        # Verify redirect to user management page
        self.assertRedirects(response, reverse('users:user_management'))
        
        # Verify old link is no longer active
        self.assertFalse(
            ProfessionalCustomerLink.objects.filter(
                customer=self.customer,
                professional=self.professional,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            ).exists()
        )
        
        # Verify new link is active
        self.assertTrue(
            ProfessionalCustomerLink.objects.filter(
                customer=self.customer,
                professional=self.professional2,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            ).exists()
        )
    
    def test_login_functionality(self):
        """
        Test Case ID: users_VIEW_012
        Verify that a user can successfully log in.
        """
        # Attempt to login
        response = self.client.post(
            reverse('login'),
            {'username': 'customer@example.com', 'password': 'password123'},
            follow=True
        )
        
        # Verify login was successful
        self.assertTrue(response.context['user'].is_authenticated)
        
        # Verify user is redirected appropriately
        # Note: The exact redirect depends on the LOGIN_REDIRECT_URL setting
        self.assertEqual(response.status_code, 200)
    
    def test_logout_functionality(self):
        """
        Test Case ID: users_VIEW_013
        Verify that a user can successfully log out.
        """
        # Login first
        self.client.login(username='customer@example.com', password='password123')
        
        # Verify login was successful
        response = self.client.get(reverse('users:profile'))
        self.assertTrue(response.context['user'].is_authenticated)
        
        # Logout
        response = self.client.get(reverse('logout'), follow=True)
        
        # Verify logout was successful
        self.assertFalse(response.context['user'].is_authenticated)
    
    def test_access_profile_page_when_not_logged_in(self):
        """
        Test Case ID: users_VIEW_014
        Verify that an anonymous user is redirected to login when attempting to access the profile page.
        """
        # Ensure user is not logged in
        self.client.logout()
        
        # Attempt to access profile page
        response = self.client.get(reverse('users:profile'))
        
        # Verify redirect to login page
        login_url = f"{settings.LOGIN_URL}?next={reverse('users:profile')}"
        self.assertRedirects(response, login_url)
    
    def test_access_change_professional_page_when_not_logged_in(self):
        """
        Test Case ID: users_VIEW_015
        Verify that an anonymous user is redirected to login when attempting to access the change professional page.
        """
        # Ensure user is not logged in
        self.client.logout()
        
        # Attempt to access change professional page
        response = self.client.get(reverse('users:change_professional'))
        
        # Verify redirect to login page
        login_url = f"{settings.LOGIN_URL}?next={reverse('users:change_professional')}"
        self.assertRedirects(response, login_url)
    
    def test_access_change_professional_page_as_customer_not_linked(self):
        """
        Test Case ID: users_VIEW_016
        Verify behavior when a customer not linked to any professional attempts to access the change professional page.
        """
        # Login as customer (not linked to any professional)
        self.client.login(username='customer@example.com', password='password123')
        
        # Attempt to access change professional page
        response = self.client.get(reverse('users:change_professional'))
        
        # Verify response is successful (the view should handle this case)
        self.assertEqual(response.status_code, 200)
        
        # Verify correct template is used
        self.assertTemplateUsed(response, 'users/customer_choose_professional.html')
        
        # Verify professional choice form is in context
        self.assertIsInstance(response.context['form'], ProfessionalChoiceForm)
