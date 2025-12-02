"""
Filters for the messaging API.

This module provides FilterSet classes for filtering conversations and messages
based on various criteria like participants, time ranges, and message content.
"""

import django_filters
from .models import Message, Conversation, user as User


class MessageFilter(django_filters.FilterSet):
    """
    FilterSet for filtering messages by various criteria.
    
    Filters:
    - conversation: Filter by conversation ID
    - sender: Filter by sender user ID
    - message_body: Search in message content (case-insensitive)
    - sent_at_after: Messages sent after a specific datetime
    - sent_at_before: Messages sent before a specific datetime
    - date_range: Messages within a date range (after and before combined)
    """
    
    # Filter by conversation ID
    conversation = django_filters.UUIDFilter(
        field_name='conversation_id__conversation_id',
        lookup_expr='exact'
    )
    
    # Filter by sender user ID
    sender = django_filters.UUIDFilter(
        field_name='sender_id__user_id',
        lookup_expr='exact'
    )
    
    # Search in message body (case-insensitive partial match)
    message_body = django_filters.CharFilter(
        field_name='message_body',
        lookup_expr='icontains'
    )
    
    # Filter messages sent after a specific datetime
    sent_at_after = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte'
    )
    
    # Filter messages sent before a specific datetime
    sent_at_before = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte'
    )
    
    class Meta:
        model = Message
        fields = ['conversation', 'sender', 'message_body', 'sent_at_after', 'sent_at_before']


class ConversationFilter(django_filters.FilterSet):
    """
    FilterSet for filtering conversations by participants and creation time.
    
    Filters:
    - participant: Filter by participant user ID
    - participant_email: Filter by participant email
    - created_after: Conversations created after a specific datetime
    - created_before: Conversations created before a specific datetime
    """
    
    # Filter by participant user ID
    participant = django_filters.UUIDFilter(
        field_name='participants_id__user_id',
        lookup_expr='exact'
    )
    
    # Filter by participant email
    participant_email = django_filters.CharFilter(
        field_name='participants_id__email',
        lookup_expr='iexact'
    )
    
    # Filter conversations created after a specific datetime
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    
    # Filter conversations created before a specific datetime
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    
    class Meta:
        model = Conversation
        fields = ['participant', 'participant_email', 'created_after', 'created_before']
