from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Customer, Professional

class UserProfileManagementTests(TestCase):
    """
    Test cases for user profile management functionality.
    These tests correspond to the test cases in the documentation:
    - users_PRF_001: Verify Professional Profile Attributes
    - users_PRF_002: Verify Customer Profile Attributes
    - users_PRF_003: Placeholder - Customer Profile Update Functionality (not implemented yet)
    - users_PRF_004: Placeholder - Professional Profile Update Functionality (not implemented yet)
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
        self.customer = Customer.objects.create(
            user=self.customer_user,
            company_name='Test Company',
            shipping_address='123 Shipping St',
            billing_address='456 Billing Ave',
            preferred_currency='USD',
            marketing_preferences={'email': True, 'sms': False}
        )
        
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
            title='Software Architect',
            specialization='Web Development',
            bio='Experienced software architect with 10+ years of experience',
            contact_hours='9 AM - 5 PM EST',
            rating=4.75
        )
    
    def test_professional_profile_attributes(self):
        """
        Test Case ID: users_PRF_001
        Ensure a Professional's profile can store and retrieve its attributes.
        """
        # Retrieve the professional from the database
        professional = Professional.objects.get(user=self.professional_user)
        
        # Verify all attributes are stored correctly
        self.assertEqual(professional.title, 'Software Architect')
        self.assertEqual(professional.specialization, 'Web Development')
        self.assertEqual(professional.bio, 'Experienced software architect with 10+ years of experience')
        self.assertEqual(professional.contact_hours, '9 AM - 5 PM EST')
        self.assertEqual(professional.rating, 4.75)
        
        # Login as the professional user
        self.client.login(username='professional@example.com', password='password123')
        
        # Access the profile view
        response = self.client.get(reverse('users:profile'))
        
        # Verify the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Verify the professional profile is in the context
        self.assertIn('professional_profile', response.context)
        
        # Verify the profile data in the context matches what we expect
        profile = response.context['professional_profile']
        self.assertEqual(profile.title, 'Software Architect')
        self.assertEqual(profile.specialization, 'Web Development')
        self.assertEqual(profile.bio, 'Experienced software architect with 10+ years of experience')
        self.assertEqual(profile.contact_hours, '9 AM - 5 PM EST')
        self.assertEqual(profile.rating, 4.75)
    
    def test_customer_profile_attributes(self):
        """
        Test Case ID: users_PRF_002
        Ensure a Customer's profile can store and retrieve its attributes.
        """
        # Retrieve the customer from the database
        customer = Customer.objects.get(user=self.customer_user)
        
        # Verify all attributes are stored correctly
        self.assertEqual(customer.company_name, 'Test Company')
        self.assertEqual(customer.shipping_address, '123 Shipping St')
        self.assertEqual(customer.billing_address, '456 Billing Ave')
        self.assertEqual(customer.preferred_currency, 'USD')
        self.assertEqual(customer.marketing_preferences, {'email': True, 'sms': False})
        
        # Login as the customer user
        self.client.login(username='customer@example.com', password='password123')
        
        # Access the profile view
        response = self.client.get(reverse('users:profile'))
        
        # Verify the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Verify the customer profile is in the context
        self.assertIn('customer_profile', response.context)
        
        # Verify the profile data in the context matches what we expect
        profile = response.context['customer_profile']
        self.assertEqual(profile.company_name, 'Test Company')
        self.assertEqual(profile.shipping_address, '123 Shipping St')
        self.assertEqual(profile.billing_address, '456 Billing Ave')
        self.assertEqual(profile.preferred_currency, 'USD')
        self.assertEqual(profile.marketing_preferences, {'email': True, 'sms': False})
    
    # Note: The following tests are placeholders for functionality that is not yet implemented
    # They are included to match the test cases in the documentation
    
    def test_customer_profile_update_placeholder(self):
        """
        Test Case ID: users_PRF_003
        Placeholder for testing customer profile update functionality (not implemented yet).
        This test will fail until the functionality is implemented.
        """
        # This is a placeholder test for future implementation
        # When implemented, it should test the ability to update customer profile information
        pass
    
    def test_professional_profile_update_placeholder(self):
        """
        Test Case ID: users_PRF_004
        Placeholder for testing professional profile update functionality (not implemented yet).
        This test will fail until the functionality is implemented.
        """
        # This is a placeholder test for future implementation
        # When implemented, it should test the ability to update professional profile information
        pass

