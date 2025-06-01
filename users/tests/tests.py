from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Customer, Professional, ProfessionalCustomerLink
from django.conf import settings

class UserViewsTest(TestCase):
    NON_EXISTENT_PROFESSIONAL_ID = 99999
    # Let's setup some test data
    # Set up test users and profiles for use in all tests
    def setUp(self):
        self.client = Client()
        self.customer_user = User.objects.create_user(username='cust', email='cust@example.com', password='pass')
        self.prof_user = User.objects.create_user(username='prof', email='prof@example.com', password='pass')
        self.customer = Customer.objects.create(user=self.customer_user)
        self.professional = Professional.objects.create(user=self.prof_user, title='Test Pro')

    def test_register_view_get(self):
        """Test GET request to the registration page."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')

    def test_register_post_valid_customer_data(self):
        """Test POST to register a new customer with valid data."""
        initial_user_count = User.objects.count()
        initial_customer_count = Customer.objects.count()
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'testpass',
            'role': 'customer'
        }
        response = self.client.post(reverse('register'), data)
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        self.assertEqual(Customer.objects.count(), initial_customer_count + 1)
        self.assertTrue(User.objects.filter(email='john@example.com').exists())
        self.assertTrue(Customer.objects.filter(user__email='john@example.com').exists())

    def test_register_post_duplicate_email(self):
        """Test POST to register with an existing email address."""
        initial_user_count = User.objects.count()
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': self.customer_user.email, # Existing email
            'password': 'password123',
            'role': 'customer'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200) # Re-renders form
        self.assertFormError(response.context['form'], 'email', 'This email is already registered. Please log in instead.') # Adjust error message if needed
        self.assertEqual(User.objects.count(), initial_user_count)

    def test_register_post_missing_email(self):
        """Test POST to register with a missing email address."""
        initial_user_count = User.objects.count()
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': '', # Missing email
            'password': 'password123',
            'role': 'customer'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'This field is required.')
        self.assertEqual(User.objects.count(), initial_user_count)

    def test_login_view_get(self):
        """Test GET request to the login page."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login') # Or other text like "Sign in"

    def test_login_post_incorrect_credentials(self):
        """Test POST to login with incorrect credentials."""
        data = {'username': 'cust', 'password': 'wrongpassword'}
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200) # Re-renders form
        self.assertContains(response, "Please enter a correct username and password.") # Django's default message
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_post_correct_credentials(self):
        """Test POST to login with correct credentials and successful redirect."""
        data = {'username': 'cust', 'password': 'pass'} # From setUp
        response = self.client.post(reverse('login'), data, follow=True)
        self.assertTrue(response.redirect_chain) # Check if any redirect happened
        # Check final landing page after redirect (e.g., user_management)
        self.assertEqual(response.request['PATH_INFO'], reverse('user_management'))
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.customer_user.pk)

    def test_user_management_view_customer_no_link_shows_choice(self):
        """Test user_management view for customer without a professional link shows professional choice form."""
        self.client.login(username='cust', password='pass')
        response = self.client.get(reverse('user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Choose your Professional')

    def test_user_management_view_customer_with_link_shows_dashboard(self):
        """Test user_management view for customer with a professional link shows dashboard."""
        ProfessionalCustomerLink.objects.create(
            professional=self.professional,
            customer=self.customer,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        )
        self.client.login(username='cust', password='pass')
        response = self.client.get(reverse('user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your Professional')

    def test_change_professional_post_valid_id(self):
        """Test POST to change professional with a valid new professional ID."""
        self.client.login(username='cust', password='pass')
        # Ensure a link might or might not exist initially, the view should handle it.
        # Optional: Create an initial link to see it change
        ProfessionalCustomerLink.objects.create(
            professional=self.professional, # Initial professional
            customer=self.customer,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        )

        new_prof_user = User.objects.create_user(username='prof2', email='prof2@example.com', password='pass')
        new_prof = Professional.objects.create(user=new_prof_user, title='Pro2')

        response = self.client.post(reverse('change_professional'), {'professional': new_prof.pk})
        self.assertRedirects(response, reverse('user_management'))
        link_exists = ProfessionalCustomerLink.objects.filter(customer=self.customer, professional=new_prof, status=ProfessionalCustomerLink.StatusChoices.ACTIVE).exists()
        self.assertTrue(link_exists)
        # Ensure old link (if any specific one was targeted) is no longer active or is deleted,
        # depending on the view's logic (e.g., it might set old ones to INACTIVE)
        old_link_active = ProfessionalCustomerLink.objects.filter(customer=self.customer, professional=self.professional, status=ProfessionalCustomerLink.StatusChoices.ACTIVE).exists()
        self.assertFalse(old_link_active)


    def test_change_professional_post_non_existent_id(self):
        """Test POST to change professional with a non-existent professional ID."""
        self.client.login(username='cust', password='pass')
        initial_link = ProfessionalCustomerLink.objects.filter(customer=self.customer).first()

        response = self.client.post(reverse('change_professional'), {'professional': self.NON_EXISTENT_PROFESSIONAL_ID}) # Non-existent ID

        self.assertEqual(response.status_code, 200) # View should re-render with form errors
        self.assertFormError(response.context['form'], 'professional', 'Select a valid choice. That choice is not one of the available choices.')

        current_link = ProfessionalCustomerLink.objects.filter(customer=self.customer).first()
        self.assertEqual(initial_link, current_link) # Link should not have changed

    def test_change_professional_get_unauthenticated(self):
        """Test GET request to change_professional view when unauthenticated."""
        self.client.logout()
        url = reverse('change_professional')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={url}")

    def test_change_professional_post_unauthenticated(self):
        """Test POST request to change_professional view when unauthenticated."""
        self.client.logout()
        url = reverse('change_professional')
        response = self.client.post(url, {'professional': self.professional.pk})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={url}")