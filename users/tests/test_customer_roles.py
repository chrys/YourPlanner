from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Customer

class CustomerRoleTests(TestCase):
    def setUp(self):
        # Create test users with different roles
        self.standard_user = User.objects.create_user(
            username='standard_user',
            email='standard@example.com',
            password='password123'
        )
        self.premium_user = User.objects.create_user(
            username='premium_user',
            email='premium@example.com',
            password='password123'
        )
        self.vip_user = User.objects.create_user(
            username='vip_user',
            email='vip@example.com',
            password='password123'
        )
        self.enterprise_user = User.objects.create_user(
            username='enterprise_user',
            email='enterprise@example.com',
            password='password123'
        )
        
        # Create customer profiles with different roles
        self.standard_customer = Customer.objects.create(
            user=self.standard_user,
            role=Customer.RoleChoices.STANDARD
        )
        self.premium_customer = Customer.objects.create(
            user=self.premium_user,
            role=Customer.RoleChoices.PREMIUM
        )
        self.vip_customer = Customer.objects.create(
            user=self.vip_user,
            role=Customer.RoleChoices.VIP
        )
        self.enterprise_customer = Customer.objects.create(
            user=self.enterprise_user,
            role=Customer.RoleChoices.ENTERPRISE
        )
    
    def test_customer_role_default(self):
        """Test that the default role is STANDARD"""
        new_user = User.objects.create_user(
            username='new_user',
            email='new@example.com',
            password='password123'
        )
        new_customer = Customer.objects.create(user=new_user)
        self.assertEqual(new_customer.role, Customer.RoleChoices.STANDARD)
    
    def test_has_role_method(self):
        """Test the has_role method"""
        self.assertTrue(self.standard_customer.has_role(Customer.RoleChoices.STANDARD))
        self.assertFalse(self.standard_customer.has_role(Customer.RoleChoices.PREMIUM))
        
        self.assertTrue(self.premium_customer.has_role(Customer.RoleChoices.PREMIUM))
        self.assertFalse(self.premium_customer.has_role(Customer.RoleChoices.VIP))
        
        self.assertTrue(self.vip_customer.has_role(Customer.RoleChoices.VIP))
        self.assertFalse(self.vip_customer.has_role(Customer.RoleChoices.ENTERPRISE))
        
        self.assertTrue(self.enterprise_customer.has_role(Customer.RoleChoices.ENTERPRISE))
        self.assertFalse(self.enterprise_customer.has_role(Customer.RoleChoices.STANDARD))
    
    def test_has_minimum_role_method(self):
        """Test the has_minimum_role method"""
        # Standard customer
        self.assertTrue(self.standard_customer.has_minimum_role(Customer.RoleChoices.STANDARD))
        self.assertFalse(self.standard_customer.has_minimum_role(Customer.RoleChoices.PREMIUM))
        self.assertFalse(self.standard_customer.has_minimum_role(Customer.RoleChoices.VIP))
        self.assertFalse(self.standard_customer.has_minimum_role(Customer.RoleChoices.ENTERPRISE))
        
        # Premium customer
        self.assertTrue(self.premium_customer.has_minimum_role(Customer.RoleChoices.STANDARD))
        self.assertTrue(self.premium_customer.has_minimum_role(Customer.RoleChoices.PREMIUM))
        self.assertFalse(self.premium_customer.has_minimum_role(Customer.RoleChoices.VIP))
        self.assertFalse(self.premium_customer.has_minimum_role(Customer.RoleChoices.ENTERPRISE))
        
        # VIP customer
        self.assertTrue(self.vip_customer.has_minimum_role(Customer.RoleChoices.STANDARD))
        self.assertTrue(self.vip_customer.has_minimum_role(Customer.RoleChoices.PREMIUM))
        self.assertTrue(self.vip_customer.has_minimum_role(Customer.RoleChoices.VIP))
        self.assertFalse(self.vip_customer.has_minimum_role(Customer.RoleChoices.ENTERPRISE))
        
        # Enterprise customer
        self.assertTrue(self.enterprise_customer.has_minimum_role(Customer.RoleChoices.STANDARD))
        self.assertTrue(self.enterprise_customer.has_minimum_role(Customer.RoleChoices.PREMIUM))
        self.assertTrue(self.enterprise_customer.has_minimum_role(Customer.RoleChoices.VIP))
        self.assertTrue(self.enterprise_customer.has_minimum_role(Customer.RoleChoices.ENTERPRISE))

