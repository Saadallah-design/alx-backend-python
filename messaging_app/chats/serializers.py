from rest_framework import serializers
from .models import user, Message, Conversation


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    # class Meta is a nested class to define model and fields. 
    # it tells the serializer which model to serialize and which fields to include.
    class Meta:
        model = user
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
        # extra kwargs to make password_hash write-only field
        extra_kwargs = {
            'password_hash': {'write_only': True}
        }


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender = UserSerializer(source='sender_id', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'conversation_id',
            'sender_id',
            'sender',
            'message_body',
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']


#  nested structure: Conversation → Messages → Sender (User)

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested messages and participants.
    ----
    a convo has participants and messages.
    So, we need to get the participants from user serializer
    and messages from message serializer.
    """
    participants = UserSerializer(source='participants_id', many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants_id',
            'participants',
            'messages',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']
