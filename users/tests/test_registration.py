from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Customer, Professional
from django.utils.html import escape  # Add this import

class UserRegistrationTests(TestCase):
    """
    Test cases for user registration functionality.
    These tests correspond to the test cases in the documentation:
    - users_REG_001: Successful Customer Registration
    - users_REG_002: Successful Professional Registration
    - users_REG_003: Attempt Registration with Existing Email
    - users_REG_004: Attempt Professional Registration without Title
    - users_REG_005: Attempt Registration with Missing Required Fields (e.g., Email)
    """
    
    def setUp(self):
        """Set up test data for all test methods."""
        self.client = Client()
        # Create a user for testing duplicate email
        self.existing_user = User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='password123',
            first_name='Existing',
            last_name='User'
        )
        
    def test_successful_customer_registration(self):
        """
        Test Case ID: users_REG_001
        Verify that a new user can successfully register as a 'Customer'.
        """
        # Initial counts for verification
        initial_user_count = User.objects.count()
        initial_customer_count = Customer.objects.count()
        
        # Registration data
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'securepassword',
            'role': 'customer'
        }
        
        # Submit registration form
        response = self.client.post(reverse('users:register'), data)
        
        # Verify redirect to user management page
        self.assertRedirects(response, reverse('users:user_management'))
        
        # Verify user and customer profile creation
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        self.assertEqual(Customer.objects.count(), initial_customer_count + 1)
        
        # Verify user details
        new_user = User.objects.get(email='john.doe@example.com')
        self.assertEqual(new_user.first_name, 'John')
        self.assertEqual(new_user.last_name, 'Doe')
        
        # Verify customer profile was created and linked to user
        self.assertTrue(hasattr(new_user, 'customer_profile'))
        self.assertIsNotNone(new_user.customer_profile)
    
    def test_successful_professional_registration(self):
        """
        Test Case ID: users_REG_002
        Verify that a new user can successfully register as a 'Professional'.
        """
        # Initial counts for verification
        initial_user_count = User.objects.count()
        initial_professional_count = Professional.objects.count()
        
        # Registration data
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'password': 'securepassword',
            'role': 'professional',
            'title': 'Software Engineer'
        }
        
        # Submit registration form
        response = self.client.post(reverse('users:register'), data)
        
        # Verify redirect to user management page
        self.assertRedirects(response, reverse('users:user_management'))
        
        # Verify user and professional profile creation
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        self.assertEqual(Professional.objects.count(), initial_professional_count + 1)
        
        # Verify user details
        new_user = User.objects.get(email='jane.smith@example.com')
        self.assertEqual(new_user.first_name, 'Jane')
        self.assertEqual(new_user.last_name, 'Smith')
        
        # Verify professional profile was created with correct title
        self.assertTrue(hasattr(new_user, 'professional_profile'))
        self.assertIsNotNone(new_user.professional_profile)
        self.assertEqual(new_user.professional_profile.title, 'Software Engineer')
    
    def test_registration_with_existing_email(self):
        """
        Test Case ID: users_REG_003
        Verify that registration fails if the email address is already in use.
        """
        # Initial counts for verification
        initial_user_count = User.objects.count()
        
        # Registration data with existing email
        data = {
            'first_name': 'Another',
            'last_name': 'User',
            'email': 'existing@example.com',  # Email already in use
            'password': 'securepassword',
            'role': 'customer'
        }
        
        # Submit registration form
        response = self.client.post(reverse('users:register'), data)
        
        # Verify form is re-rendered (not redirected)
        self.assertEqual(response.status_code, 200)
        
        # Verify error message is displayed
        # Note: The error is displayed via messages framework, not form errors
        self.assertContains(response, "This email is already registered")
        
        # Verify no new user was created
        self.assertEqual(User.objects.count(), initial_user_count)
    
    def test_professional_registration_without_title(self):
        """
        Test Case ID: users_REG_004
        Verify that registration for a 'Professional' fails if the 'Title' field is not provided.
        """
        # Initial counts for verification
        initial_user_count = User.objects.count()
        initial_professional_count = Professional.objects.count()
        
        # Registration data without title
        data = {
            'first_name': 'Missing',
            'last_name': 'Title',
            'email': 'missing.title@example.com',
            'password': 'securepassword',
            'role': 'professional',
            # 'title' field is intentionally omitted
        }
        
        # Submit registration form
        response = self.client.post(reverse('users:register'), data)
        
        # Verify form is re-rendered (not redirected)
        self.assertEqual(response.status_code, 200)
        
        # Verify error message for title field
        self.assertFormError(response, 'form', 'title', 'Title is required for professionals.')
        
        # Verify no new user or professional was created
        self.assertEqual(User.objects.count(), initial_user_count)
        self.assertEqual(Professional.objects.count(), initial_professional_count)
    
    def test_registration_with_missing_email(self):
        """
        Test Case ID: users_REG_005
        Verify that registration fails if a required field (email) is not provided.
        """
        # Initial counts for verification
        initial_user_count = User.objects.count()
        
        # Registration data without email
        data = {
            'first_name': 'Missing',
            'last_name': 'Email',
            'email': '',  # Empty email
            'password': 'securepassword',
            'role': 'customer'
        }
        
        # Submit registration form
        response = self.client.post(reverse('users:register'), data)
        
        # Verify form is re-rendered (not redirected)
        self.assertEqual(response.status_code, 200)
        
        # Verify error message for email field
        self.assertFormError(response, 'form', 'email', 'This field is required.')
        
        # Verify no new user was created
        self.assertEqual(User.objects.count(), initial_user_count)
