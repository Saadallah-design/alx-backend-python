from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import user, Message, Conversation
from .serializers import UserSerializer, MessageSerializer, ConversationSerializer


# class UserViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet for viewing and editing User instances.
#     Provides list, create, retrieve, update, and destroy actions.
#     """
#     queryset = user.objects.all()
#     serializer_class = UserSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Conversation instances.
    Provides list, create, retrieve, update, and destroy actions.
    Also includes custom action to get messages for a conversation.
    """
    # using prefetch_related to optimize queries
    queryset = Conversation.objects.prefetch_related('participants_id', 'messages').all()
    serializer_class = ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with participants.
        Expected payload: {"participants_id": [user_id1, user_id2, ...]}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the conversation
        conversation = serializer.save()
        
        # Add participants
        participants_ids = request.data.get('participants_id', [])
        if participants_ids:
            participants = user.objects.filter(user_id__in=participants_ids)
            conversation.participants_id.set(participants)
        
        # Return the created conversation with full details
        response_serializer = self.get_serializer(conversation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages for a specific conversation.
        URL: /conversations/{id}/messages/
        """
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('sent_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Message instances.
    Provides list, create, retrieve, update, and destroy actions.
    """
    queryset = Message.objects.select_related('sender_id', 'conversation_id').all()
    serializer_class = MessageSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Send a message to an existing conversation.
        Expected payload: {
            "conversation_id": <uuid>,
            "sender_id": <uuid>,
            "message_body": "text"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the message
        message = serializer.save()
        
        # Return the created message with full details
        response_serializer = self.get_serializer(message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        """
        List all messages, optionally filtered by conversation_id.
        Query parameter: ?conversation_id=<uuid>
        """
        queryset = self.get_queryset()
        
        # Filter by conversation if provided
        conversation_id = request.query_params.get('conversation_id', None)
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        
        # Order by sent time
        queryset = queryset.order_by('sent_at')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

