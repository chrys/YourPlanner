from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Agent, Professional
from orders.models import Order, OrderItem
from services.models import Service, Item, Price
from django.utils import timezone

class AgentModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='agent@example.com',
            email='agent@example.com',
            password='password123',
            first_name='Agent',
            last_name='Test'
        )
        self.agent = Agent.objects.create(
            user=self.user,
            agency_name='Test Agency'
        )
        
    def test_agent_creation(self):
        """Test that an agent can be created correctly."""
        self.assertEqual(self.agent.user.username, 'agent@example.com')
        self.assertEqual(self.agent.agency_name, 'Test Agency')
        self.assertEqual(str(self.agent), f"Agent: {self.user}")
        
    def test_agent_profile_access(self):
        """Test that the agent profile can be accessed through the user."""
        self.assertEqual(self.user.agent_profile, self.agent)

class AgentViewsTestCase(TestCase):
    def setUp(self):
        # Create agent user
        self.agent_user = User.objects.create_user(
            username='agent@example.com',
            email='agent@example.com',
            password='password123',
            first_name='Agent',
            last_name='Test'
        )
        self.agent = Agent.objects.create(
            user=self.agent_user,
            agency_name='Test Agency'
        )
        
        # Create professional user
        self.professional_user = User.objects.create_user(
            username='professional@example.com',
            email='professional@example.com',
            password='password123',
            first_name='Professional',
            last_name='Test'
        )
        self.professional = Professional.objects.create(
            user=self.professional_user,
            title='Test Professional'
        )
        
        # Create service and items
        self.service = Service.objects.create(
            professional=self.professional,
            title='Test Service',
            description='Test service description',
            is_active=True
        )
        
        self.item = Item.objects.create(
            service=self.service,
            title='Test Item',
            description='Test item description',
            quantity=10
        )
        
        self.price = Price.objects.create(
            item=self.item,
            amount=100.00,
            currency='EUR',
            frequency=Price.FrequencyChoices.ONE_TIME,
            is_active=True
        )
        
        # Create client
        self.client = Client()
        
    def test_agent_dashboard(self):
        """Test that an agent can access their dashboard."""
        self.client.login(username='agent@example.com', password='password123')
        response = self.client.get(reverse('users:user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/agent_dashboard.html')
        
    def test_agent_create_order_view(self):
        """Test that an agent can access the create order view."""
        self.client.login(username='agent@example.com', password='password123')
        response = self.client.get(reverse('users:agent_create_order'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/agent_select_professional.html')
        
    def test_agent_order_creation_flow(self):
        """Test the complete order creation flow for an agent."""
        self.client.login(username='agent@example.com', password='password123')
        
        # Step 1: Select professional
        response = self.client.post(reverse('users:agent_create_order'), {
            'professional': self.professional.pk
        })
        self.assertEqual(response.status_code, 302)  # Redirect to next step
        
        # Step 2: Select services and items
        response = self.client.get(reverse('users:agent_select_services'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/agent_select_services.html')
        
        response = self.client.post(reverse('users:agent_select_services'), {
            f'item_{self.item.pk}': 2  # Order 2 of the test item
        })
        self.assertEqual(response.status_code, 302)  # Redirect to next step
        
        # Step 3: Finalize order
        response = self.client.get(reverse('users:agent_finalize_order'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/agent_finalize_order.html')
        
        # Count orders before
        orders_before = Order.objects.count()
        
        response = self.client.post(reverse('users:agent_finalize_order'), {
            'notes': 'Test order notes',
            'currency': 'EUR'
        })
        
        # Verify order was created
        self.assertEqual(Order.objects.count(), orders_before + 1)
        
        # Get the created order
        order = Order.objects.latest('created_at')
        self.assertEqual(order.agent, self.agent)
        self.assertEqual(order.notes, 'Test order notes')
        self.assertEqual(order.currency, 'EUR')
        
        # Verify order items
        self.assertEqual(order.items.count(), 1)
        order_item = order.items.first()
        self.assertEqual(order_item.item, self.item)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price_amount_at_order, 100.00)
        
        # Verify total amount
        self.assertEqual(order.total_amount, 200.00)  # 2 items at 100.00 each

class AgentRegistrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_agent_registration(self):
        """Test that a user can register as an agent."""
        response = self.client.post(reverse('users:register'), {
            'first_name': 'New',
            'last_name': 'Agent',
            'email': 'newagent@example.com',
            'password': 'password123',
            'role': 'agent',
            'agency_name': 'New Agency'
        })
        
        # Check if user was created
        self.assertTrue(User.objects.filter(email='newagent@example.com').exists())
        user = User.objects.get(email='newagent@example.com')
        
        # Check if agent profile was created
        self.assertTrue(hasattr(user, 'agent_profile'))
        self.assertEqual(user.agent_profile.agency_name, 'New Agency')

