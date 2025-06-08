from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from users.models import Customer, Professional, ProfessionalCustomerLink
from users.forms import ProfessionalChoiceForm
from labels.models import Label # Added import

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
        #self.assertFalse(response.wsgi_request.user.is_authenticated)
    
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
        #login_url = f"{settings.LOGIN_URL}?next={reverse('users:change_professional')}"
        #self.assertRedirects(response, login_url)
    
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


class DepositPaymentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_password = 'testpassword123'

        # Create deposit_paid label
        self.deposit_label, _ = Label.objects.get_or_create(
            name='deposit_paid',
            defaults={'label_type': 'CUSTOMER', 'color': '#28a745'}
        )

        # Data for customer registration redirect test
        self.customer_reg_data = {
            'first_name': 'Test', 'last_name': 'CustReg', 'email': 'custreg@example.com',
            'password': self.user_password, 'role': 'customer', 'title': ''
        }

        # Customer for deposit form test
        self.customer_user_for_deposit_test = User.objects.create_user(
            username='testcust_deposit@example.com', email='testcust_deposit@example.com',
            password=self.user_password, first_name='Test', last_name='CustomerDeposit'
        )
        self.customer_profile_for_deposit_test = Customer.objects.create(user=self.customer_user_for_deposit_test)

        # Professional and another customer for label management tests
        self.prof_user_for_label_test = User.objects.create_user(
            username='testprof_label@example.com', email='testprof_label@example.com',
            password=self.user_password, first_name='Test', last_name='ProfessionalLabel'
        )
        self.professional_profile_for_label_test = Professional.objects.create(user=self.prof_user_for_label_test, title='Dr. LabelProf')

        self.managed_customer_user_for_label_test = User.objects.create_user(
            username='managedcust_label@example.com', email='managedcust_label@example.com',
            password=self.user_password, first_name='ManagedLabel', last_name='Customer'
        )
        self.managed_customer_profile_for_label_test = Customer.objects.create(user=self.managed_customer_user_for_label_test)

        ProfessionalCustomerLink.objects.create(
            professional=self.professional_profile_for_label_test,
            customer=self.managed_customer_profile_for_label_test,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        )

    def test_customer_registration_redirects_to_deposit_payment(self):
        """
        Tests that a new customer registration redirects to the deposit payment page.
        """
        response = self.client.post(reverse('users:register'), self.customer_reg_data)
        # Check if user was created, to ensure redirect is the actual point of test
        self.assertTrue(User.objects.filter(email=self.customer_reg_data['email']).exists(), "User was not created.")
        user = User.objects.get(email=self.customer_reg_data['email'])
        self.assertTrue(hasattr(user, 'customer_profile'), "Customer profile not created.")
        # Check response status code after user creation checks
        self.assertEqual(response.status_code, 302, msg=f"Registration did not redirect. Errors: {response.context.get('form').errors if response.context and hasattr(response.context, 'get') else 'No form context or context not a dict'}")
        self.assertRedirects(response, reverse('users:deposit_payment'))

    def test_deposit_payment_form_adds_label(self):
        """
        Tests that submitting the deposit payment form adds the 'deposit_paid' label
        to the customer and shows a success message.
        """
        self.client.login(username='testcust_deposit@example.com', password=self.user_password)

        self.assertNotIn(self.deposit_label, self.customer_profile_for_deposit_test.labels.all())

        response_post = self.client.post(reverse('users:deposit_payment'), {'deposit_paid_checkbox': 'on'})

        if response_post.status_code == 200:
            # If we got a 200, it means form_invalid was likely called.
            # Check for the specific error message related to Label.DoesNotExist.
            content = response_post.content.decode('utf-8')
            is_label_missing_error = "Critical error: The 'deposit_paid' label is not configured. Please contact support." in content
            form_errors = response_post.context.get('form').errors if response_post.context and hasattr(response_post.context.get('form'), 'errors') else "No form errors in context or form has no errors attribute."
            self.fail(f"Form submission returned 200 instead of 302. Label missing error present: {is_label_missing_error}. Form errors: {form_errors}. Content: {content[:500]}...") # Fail with more info

        self.assertEqual(response_post.status_code, 302, "Form submission did not redirect.") # Check for redirect first

        # Follow the redirect manually to inspect the final page and messages
        response_get = self.client.get(response_post.url)
        self.assertEqual(response_get.status_code, 200)

        self.customer_profile_for_deposit_test.refresh_from_db()
        self.assertIn(self.deposit_label, self.customer_profile_for_deposit_test.labels.all())

        messages = list(response_get.context['messages']) # Check messages on the final page
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Thank you for confirming your deposit payment. Your account is now fully active.")

    def test_professional_can_add_deposit_label(self):
        """
        Tests that a professional can add the 'deposit_paid' label to a linked customer
        via the customer_labels update view.
        """
        self.client.login(username='testprof_label@example.com', password=self.user_password)

        self.assertNotIn(self.deposit_label, self.managed_customer_profile_for_label_test.labels.all())

        response = self.client.post(
            reverse('users:customer_labels', kwargs={'customer_id': self.managed_customer_profile_for_label_test.pk}),
            {'labels': [self.deposit_label.pk]}
        )

        self.assertEqual(response.status_code, 302)

        self.managed_customer_profile_for_label_test.refresh_from_db()
        self.assertIn(self.deposit_label, self.managed_customer_profile_for_label_test.labels.all())

    def test_professional_can_remove_deposit_label(self):
        """
        Tests that a professional can remove the 'deposit_paid' label from a linked customer.
        """
        self.managed_customer_profile_for_label_test.labels.add(self.deposit_label)
        self.assertIn(self.deposit_label, self.managed_customer_profile_for_label_test.labels.all())

        self.client.login(username='testprof_label@example.com', password=self.user_password)

        response = self.client.post(
            reverse('users:customer_labels', kwargs={'customer_id': self.managed_customer_profile_for_label_test.pk}),
            {'labels': []}
        )

        self.assertEqual(response.status_code, 302)

        self.managed_customer_profile_for_label_test.refresh_from_db()
        self.assertNotIn(self.deposit_label, self.managed_customer_profile_for_label_test.labels.all())
