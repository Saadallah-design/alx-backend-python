from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view/edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant in the conversation
        return obj.participants.filter(user_id=request.user.user_id).exists()


class IsMessageSenderOrRecipient(permissions.BasePermission):
    """
    Custom permission to only allow sender or recipient of a message to view/edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is the sender or a participant in the conversation
        is_sender = obj.sender_id == request.user.user_id
        is_participant = obj.conversation.participants.filter(
            user_id=request.user.user_id
        ).exists()
        
        return is_sender or is_participant
