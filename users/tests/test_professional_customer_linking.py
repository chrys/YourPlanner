from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Customer, Professional, ProfessionalCustomerLink

class ProfessionalCustomerLinkingTests(TestCase):
    """
    Test cases for professional-customer linking functionality.
    These tests correspond to the test cases in the documentation:
    - users_LINK_001: Successful Linking of Customer to Professional
    - users_LINK_002: Attempt to Link Customer to Non-existent Professional
    - users_LINK_003: Successful Change of Professional for Customer
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
        
        # Create professional users
        self.professional_user1 = User.objects.create_user(
            username='professional1@example.com',
            email='professional1@example.com',
            password='password123',
            first_name='Professional',
            last_name='One'
        )
        self.professional1 = Professional.objects.create(
            user=self.professional_user1,
            title='Software Engineer'
        )
        
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
        
        # Non-existent professional ID for testing
        self.non_existent_professional_id = 9999
    
    def test_successful_linking_of_customer_to_professional(self):
        """
        Test Case ID: users_LINK_001
        Verify that a Customer can successfully link to an available Professional.
        """
        # Login as customer
        self.client.login(username='customer@example.com', password='password123')
        
        # Initial count of links
        initial_link_count = ProfessionalCustomerLink.objects.count()
        
        # Submit form to link with professional
        data = {'professional': self.professional1.pk}
        response = self.client.post(reverse('users:user_management'), data)
        
        # Verify redirect to user management page
        self.assertRedirects(response, reverse('users:user_management'))
        
        # Verify a new link was created
        self.assertEqual(ProfessionalCustomerLink.objects.count(), initial_link_count + 1)
        
        # Verify the link has the correct attributes
        link = ProfessionalCustomerLink.objects.get(
            customer=self.customer,
            professional=self.professional1
        )
        self.assertEqual(link.status, ProfessionalCustomerLink.StatusChoices.ACTIVE)
        
        # Verify the customer is now linked to the professional
        self.assertTrue(
            ProfessionalCustomerLink.objects.filter(
                customer=self.customer,
                professional=self.professional1,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            ).exists()
        )
    
    def test_attempt_to_link_customer_to_non_existent_professional(self):
        """
        Test Case ID: users_LINK_002
        Verify that an attempt to link a Customer to a non-existent Professional fails.
        """
        # Login as customer
        self.client.login(username='customer@example.com', password='password123')
        
        # Initial count of links
        initial_link_count = ProfessionalCustomerLink.objects.count()
        
        # Submit form with non-existent professional ID
        data = {'professional': self.non_existent_professional_id}
        response = self.client.post(reverse('users:user_management'), data)
        
        # Verify form is re-rendered (not redirected)
        self.assertEqual(response.status_code, 200)
        
        # Verify error message
        self.assertFormError(
            response.context['form'], 'professional', 
            'Select a valid choice. That choice is not one of the available choices.'
)
        
        # Verify no new link was created
        self.assertEqual(ProfessionalCustomerLink.objects.count(), initial_link_count)
    
    def test_successful_change_of_professional_for_customer(self):
        """
        Test Case ID: users_LINK_003
        Verify that a Customer can successfully change their linked Professional.
        """
        # Create initial link between customer and professional1
        initial_link = ProfessionalCustomerLink.objects.create(
            customer=self.customer,
            professional=self.professional1,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        )
        
        # Login as customer
        self.client.login(username='customer@example.com', password='password123')
        
        # Initial count of active links
        initial_active_link_count = ProfessionalCustomerLink.objects.filter(
            customer=self.customer,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        ).count()
        self.assertEqual(initial_active_link_count, 1)
        
        # Submit form to change professional
        data = {'professional': self.professional2.pk}
        response = self.client.post(reverse('users:change_professional'), data)
        
        # Verify redirect to user management page
        self.assertRedirects(response, reverse('users:user_management'))
        
        # Verify the old link is no longer active
        self.assertFalse(
            ProfessionalCustomerLink.objects.filter(
                id=initial_link.id,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            ).exists()
        )
        
        # Verify a new active link exists with the new professional
        self.assertTrue(
            ProfessionalCustomerLink.objects.filter(
                customer=self.customer,
                professional=self.professional2,
                status=ProfessionalCustomerLink.StatusChoices.ACTIVE
            ).exists()
        )
        
        # Verify there is still only one active link
        current_active_link_count = ProfessionalCustomerLink.objects.filter(
            customer=self.customer,
            status=ProfessionalCustomerLink.StatusChoices.ACTIVE
        ).count()
        self.assertEqual(current_active_link_count, 1)

