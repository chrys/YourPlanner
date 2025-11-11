import requests
import difflib
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from .models import Conversation, Message, FAQ, ChatConfig
from .serializers import (
    ConversationSerializer, MessageSerializer,
    FAQSerializer, ChatConfigSerializer
)


@api_view(['GET'])
def faq_list_view(request):
    """Fetch active FAQs."""
    faqs = FAQ.objects.filter(is_active=True).order_by('order')
    serializer = FAQSerializer(faqs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def chat_config_view(request):
    """Fetch client configuration."""
    config = ChatConfig.load()
    serializer = ChatConfigSerializer(config)
    return Response(serializer.data)


@api_view(['GET'])
def conversation_list_view(request):
    """Fetch customer's conversations."""
    status_filter = request.query_params.get('status', 'active')
    limit = int(request.query_params.get('limit', 10))

    conversations = Conversation.objects.filter(
        customer=request.user,
        status=status_filter
    ).order_by('-started_at')[:limit]

    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data)


@api_view(['POST', 'GET'])
def message_view(request):
    """Send message or fetch message history."""
    if request.method == 'POST':
        conversation_id = request.data.get('conversation_id')
        text = request.data.get('text', '').strip()

        if not text:
            return Response(
                {'error': 'Text must not be empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create conversation
        if conversation_id:
            conversation = get_object_or_404(
                Conversation,
                id=conversation_id,
                customer=request.user
            )
        else:
            conversation = Conversation.objects.create(customer=request.user)

        # Store customer message
        customer_message = Message.objects.create(
            conversation=conversation,
            customer=request.user,
            text=text,
            sender='customer'
        )

        # Check FAQ match (fuzzy matching)
        faqs = FAQ.objects.filter(is_active=True)
        best_match = None
        highest_ratio = 0.8  # Threshold for a good match

        for faq in faqs:
            ratio = difflib.SequenceMatcher(None, text.lower(), faq.question.lower()).ratio()
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = faq

        faq_match = best_match

        bot_text = faq_match.answer if faq_match else ChatConfig.load().fallback_message

        # If no FAQ match, call RAG API (Phase 1 MVP: skip for now)
        if not faq_match:
            # TODO: Integrate RAG API in Phase 1.5
            pass

        # Store bot message
        bot_message = Message.objects.create(
            conversation=conversation,
            customer=request.user,
            text=bot_text,
            sender='bot'
        )

        # Annotate faq_matched for response
        bot_message.faq_matched = bool(faq_match)

        serializer = MessageSerializer(bot_message)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def conversation_messages_view(request, conversation_id):
    """Fetch messages in a conversation."""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        customer=request.user
    )

    limit = int(request.query_params.get('limit', 50))
    offset = int(request.query_params.get('offset', 0))

    messages = conversation.messages.all()[offset:offset+limit]

    serializer = MessageSerializer(messages, many=True)
    return Response({
        'count': conversation.messages.count(),
        'results': serializer.data
    })


@api_view(['POST'])
def feedback_view(request):
    """Submit feedback on a message. Forward to RAG API."""
    message_id = request.data.get('message_id')
    value = request.data.get('value')

    if value not in ['up', 'down']:
        return Response(
            {'error': "Value must be 'up' or 'down'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    message = get_object_or_404(
        Message,
        id=message_id,
        conversation__customer=request.user
    )

    # Prepare feedback payload for RAG API
    config = ChatConfig.load()
    feedback_payload = {
        'message_id': str(message.id),
        'conversation_id': str(message.conversation.id),
        'customer_id': str(request.user.id),
        'value': value,
        'timestamp': message.timestamp.isoformat()
    }

    try:
        # Forward to RAG API
        rag_response = requests.post(
            f"{config.rag_api_url}/feedback",
            json=feedback_payload,
            headers={'Authorization': f'Bearer {config.rag_api_key}'},
            timeout=config.rag_api_timeout_seconds
        )

        if rag_response.status_code >= 200 and rag_response.status_code < 300:
            return Response({'success': True, 'message': 'Feedback submitted to RAG API'})
        else:
            return Response(
                {'error': 'Failed to submit feedback to RAG API'},
                status=status.HTTP_502_BAD_GATEWAY
            )
    except requests.RequestException as e:
        return Response(
            {'error': f'RAG API error: {str(e)}'},
            status=status.HTTP_502_BAD_GATEWAY
        )
