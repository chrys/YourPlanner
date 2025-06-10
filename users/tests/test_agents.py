from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Agent
from django.db.utils import IntegrityError # Added for the test_agent_profile_requires_user
from django.db import models # Added for the test_agent_profile_requires_user

User = get_user_model()

class AgentRegistrationTests(TestCase):

    def test_create_agent_profile(self):
        """
        Tests that an Agent profile can be created and is linked to a User account.
        """
        user = User.objects.create_user(
            username='testagent',
            email='testagent@example.com',
            password='password123'
        )
        agent = Agent.objects.create(user=user)

        self.assertIsNotNone(agent.pk)
        self.assertEqual(agent.user, user)
        self.assertEqual(str(agent), f"Agent: {user.username}")

        # Check the reverse relationship
        self.assertIsNotNone(user.agent_profile)
        self.assertEqual(user.agent_profile, agent)

    def test_agent_profile_requires_user(self):
        """
        Tests that an Agent profile cannot be created without a User.
        """
        # The original code had a complex conditional assertRaises.
        # For a OneToOneField(primary_key=True) to User, user_id cannot be null.
        # Django will raise IntegrityError if you try to save it with user=None.
        with self.assertRaises(IntegrityError):
            Agent.objects.create(user=None)
