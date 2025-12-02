from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import user, Message, Conversation
from .serializers import UserSerializer, MessageSerializer, ConversationSerializer
from .permissions import IsParticipantOfConversation, IsMessageSenderOrRecipient
from .filters import MessageFilter, ConversationFilter
from .pagination import MessagePagination


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
    
    Only allows users to access conversations they are participants in.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['participants_id__email', 'participants_id__first_name']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        """
        Filter conversations to only show those the user is a participant in.
        """
        return Conversation.objects.prefetch_related('participants_id', 'messages').filter(
            participants_id__user_id=self.request.user.user_id
        ).distinct()
    
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
    Includes pagination (20 messages per page) and filtering.
    
    Only allows users to access messages in conversations they are participants in.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsMessageSenderOrRecipient]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body', 'sender_id__email']
    ordering_fields = ['sent_at']
    pagination_class = MessagePagination
    
    def get_queryset(self):
        """
        Filter messages to only show those in conversations the user is a participant in.
        """
        # Check if this is a nested route from conversations
        conversation_pk = self.kwargs.get('conversation_pk')
        
        if conversation_pk:
            # Nested route: filter by conversation and ensure user is a participant
            return Message.objects.filter(
                conversation_id=conversation_pk,
                conversation_id__participants_id__user_id=self.request.user.user_id
            ).select_related('sender_id', 'conversation_id').distinct()
        else:
            # Regular route: show all messages in conversations the user participates in
            return Message.objects.filter(
                conversation_id__participants_id__user_id=self.request.user.user_id
            ).select_related('sender_id', 'conversation_id').distinct()
    
    def create(self, request, *args, **kwargs):
        """
        Send a message to an existing conversation.
        The sender is automatically set to the authenticated user.
        Expected payload: {
            "conversation_id": <uuid>,
            "message_body": "text"
        }
        """
        # Check if this is a nested route
        conversation_pk = self.kwargs.get('conversation_pk')
        
        data = request.data.copy()
        # Automatically set sender to the authenticated user
        data['sender_id'] = request.user.user_id
        
        # If nested route, set conversation from URL
        if conversation_pk:
            data['conversation_id'] = conversation_pk
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # Verify user is a participant in the conversation
        conversation = serializer.validated_data['conversation_id']
        if not conversation.participants_id.filter(user_id=request.user.user_id).exists():
            return Response(
                {"detail": "You are not a participant in this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )
        
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

