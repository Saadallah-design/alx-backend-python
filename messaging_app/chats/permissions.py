from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view/edit it.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant in the conversation
        if not request.user.is_authenticated:
            return False
        
        # For conversation objects, check participants
        if hasattr(obj, 'participants_id'):
            return obj.participants_id.filter(user_id=request.user.user_id).exists()
        
        # For message objects, check conversation participants
        if hasattr(obj, 'conversation_id'):
            return obj.conversation_id.participants_id.filter(user_id=request.user.user_id).exists()
        
        return False


class IsMessageSenderOrRecipient(permissions.BasePermission):
    """
    Custom permission to only allow sender or recipient of a message to view/edit it.
    Allow write operations (PUT, PATCH, DELETE) only for participants.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Check if the user is the sender or a participant in the conversation
        is_sender = obj.sender_id == request.user.user_id
        is_participant = obj.conversation_id.participants_id.filter(
            user_id=request.user.user_id
        ).exists()
        
        # For write operations (PUT, PATCH, DELETE), check if user is participant
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return is_participant or is_sender
        
        return is_sender or is_participant
