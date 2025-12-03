from rest_framework import serializers
from .models import user, Message, Conversation


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    # CharField for computed full name
    full_name = serializers.CharField(read_only=True)
    
    # SerializerMethodField for conversation count
    active_conversations_count = serializers.SerializerMethodField()
    
    # Password field for registration (write-only)
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    
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
            'created_at',
            'full_name',
            'active_conversations_count',
            'password',
            'password_confirm'
        ]
        read_only_fields = ['user_id', 'created_at']
        # extra kwargs to make password_hash write-only field
        extra_kwargs = {
            'password_hash': {'write_only': True}
        }
    
    def get_active_conversations_count(self, obj):
        """Count user's active conversations"""
        return obj.conversations.count()
    
    def validate_email(self, value):
        """Validate email format using ValidationError"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email format")
        return value.lower()
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value:
            cleaned = value.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            if not cleaned.isdigit() or len(cleaned) < 10:
                raise serializers.ValidationError("Phone number must contain at least 10 digits")
        return value


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender = UserSerializer(source='sender_id', read_only=True)
    
    # CharField for sender name
    sender_name = serializers.CharField(read_only=True)
    
    # SerializerMethodField for time since sent
    time_since_sent = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'conversation_id',
            'sender_id',
            'sender',
            'sender_name',
            'message_body',
            'sent_at',
            'time_since_sent'
        ]
        read_only_fields = ['message_id', 'sent_at']
    
    def get_time_since_sent(self, obj):
        """Calculate time since message was sent"""
        from django.utils import timezone
        delta = timezone.now() - obj.sent_at
        
        if delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600}h ago"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60}m ago"
        else:
            return "just now"
    
    def validate_message_body(self, value):
        """Validate message content with ValidationError"""
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Message cannot be empty")
        if len(cleaned) > 10000:
            raise serializers.ValidationError("Message exceeds maximum length of 10,000 characters")
        return cleaned
    
    def validate(self, data):
        """Validate sender is participant"""
        sender = data.get('sender_id')
        conversation = data.get('conversation_id')
        
        if sender and conversation:
            if not conversation.participants_id.filter(user_id=sender.user_id).exists():
                raise serializers.ValidationError({
                    "sender_id": "Sender must be a participant in this conversation"
                })
        
        return data


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
    
    # SerializerMethodFields for computed data
    message_count = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()
    last_message_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants_id',
            'participants',
            'messages',
            'message_count',
            'last_message_preview',
            'last_message_at',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_message_count(self, obj):
        """Count total messages in conversation"""
        return obj.messages.count()
    
    def get_last_message_preview(self, obj):
        """Get preview of last message"""
        last_msg = obj.messages.order_by('-sent_at').first()
        if last_msg:
            preview = last_msg.message_body[:50]
            return preview + "..." if len(last_msg.message_body) > 50 else preview
        return None
    
    def get_last_message_at(self, obj):
        """Get timestamp of last message"""
        last_msg = obj.messages.order_by('-sent_at').first()
        return last_msg.sent_at if last_msg else None
    
    def validate(self, data):
        """Validate conversation data with ValidationError"""
        participants = data.get('participants_id', [])
        
        # Minimum participants
        if len(participants) < 2:
            raise serializers.ValidationError({
                "participants_id": "A conversation must have at least 2 participants"
            })
        
        # Maximum participants
        if len(participants) > 10:
            raise serializers.ValidationError({
                "participants_id": "A conversation cannot have more than 10 participants"
            })
        
        return data
