from rest_framework import serializers
from .models import Conversation, Message, FAQ, ChatConfig

class ConversationSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'status', 'started_at', 'ended_at', 'message_count']

    def get_message_count(self, obj):
        return obj.messages.count()


class MessageSerializer(serializers.ModelSerializer):
    faq_matched = serializers.BooleanField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'text', 'timestamp', 'faq_matched']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'order']


class ChatConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatConfig
        fields = ['polling_interval_ms', 'fallback_message']
