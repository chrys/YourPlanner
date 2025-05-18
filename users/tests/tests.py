from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Customer, Professional, ProfessionalCustomerLink

class UserViewsTest(TestCase):
    # Let's setup some test data
    # Set up test users and profiles for use in all tests
    def setUp(self):
        self.client = Client()
        self.customer_user = User.objects.create_user(username='cust', email='cust@example.com', password='pass')
        self.prof_user = User.objects.create_user(username='prof', email='prof@example.com', password='pass')
        self.customer = Customer.objects.create(user=self.customer_user)
        self.professional = Professional.objects.create(user=self.prof_user, title='Test Pro')

    # Test that the registration page loads successfully
    def test_register_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')

    # Test that posting valid customer registration data creates a User and Customer
    def test_register_post_customer(self):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'testpass',
            'role': 'customer'
        }
        response = self.client.post(reverse('register'), data)
        #response should redirect to login page
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(email='john@example.com').exists())
        self.assertTrue(Customer.objects.filter(user__email='john@example.com').exists())
        
    # Test that a customer with no professional link sees the professional selection form
    def test_user_management_view_customer_no_link(self):
        self.client.login(username='cust', password='pass')
        response = self.client.get(reverse('user_management'))
        self.assertContains(response, 'Choose your Professional')

    # Test that a customer with a professional link sees the customer dashboard
    def test_user_management_view_customer_with_link(self):
        ProfessionalCustomerLink.objects.create(
            professional=self.professional,
            customer=self.customer,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        )
        self.client.login(username='cust', password='pass')
        response = self.client.get(reverse('user_management'))
        self.assertContains(response, 'Your Professional')

    # Test that a customer can change their professional link
    def test_change_professional(self):
        # Create a professional link for the customer
        ProfessionalCustomerLink.objects.create(
            professional=self.professional,
            customer=self.customer,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        )
        self.client.login(username='cust', password='pass')\
        # Create a new user and professional to link to
        new_user = User.objects.create_user(username='prof2', email='prof2@example.com', password='pass')
        new_prof = Professional.objects.create(user=new_user, title='Pro2')
        # Now new_prof.id (or new_prof.pk) should be available
        response = self.client.post(reverse('change_professional'), {'professional': new_prof.pk})
        self.assertRedirects(response, reverse('user_management'))
        # Check that the new link exists
        self.assertTrue(ProfessionalCustomerLink.objects.filter(customer=self.customer, professional=new_prof).exists())