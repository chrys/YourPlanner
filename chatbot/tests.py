from django.test import TestCase
from django.contrib.auth import get_user_model
from chatbot.models import Conversation, Message, FAQ, ChatConfig
from rest_framework.test import APIClient

User = get_user_model()

class ConversationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')

    def test_create_conversation(self):
        conv = Conversation.objects.create(customer=self.user)
        self.assertEqual(conv.status, 'active')
        self.assertIsNotNone(conv.id)


class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
        self.conv = Conversation.objects.create(customer=self.user)

    def test_create_message(self):
        msg = Message.objects.create(
            conversation=self.conv,
            customer=self.user,
            text='Hello',
            sender='customer'
        )
        self.assertEqual(msg.text, 'Hello')
        self.assertEqual(msg.sender, 'customer')

class FAQModelTest(TestCase):
    def test_create_faq(self):
        faq = FAQ.objects.create(
            question="What is your name?",
            answer="I am a chatbot."
        )
        self.assertEqual(faq.question, "What is your name?")
        self.assertTrue(faq.is_active)

class ChatConfigModelTest(TestCase):
    def test_load_chat_config(self):
        config1 = ChatConfig.load()
        config2 = ChatConfig.load()
        self.assertIsNotNone(config1)
        self.assertEqual(config1.pk, config2.pk)

class ChatbotAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='pass')
        self.client.force_authenticate(user=self.user)

        self.faq = FAQ.objects.create(
            question="What's the duration?",
            answer="30-45 minutes.",
            is_active=True
        )

    def test_send_message(self):
        response = self.client.post('/api/chatbot/messages/', {
            'text': "What's the duration?"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['faq_matched'])

    def test_get_faqs(self):
        response = self.client.get('/api/chatbot/faqs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['question'], "What's the duration?")

    def test_get_conversations(self):
        Conversation.objects.create(customer=self.user)
        response = self.client.get('/api/chatbot/conversations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
