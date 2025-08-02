# chats/permissions.py
from rest_framework import permissions
from chats import models

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only participants of a conversation to interact with it.
    """
    message = 'You are not a participant of this conversation.'

    def has_permission(self, request, view):
        # Allow only authenticated users
        if not request.user.is_authenticated:
            return False

        # Handle each method type specifically
        if request.method == 'POST':
            # For message/conversation creation
            if hasattr(view, 'get_conversation'):  # For message creation
                conversation = view.get_conversation()
                return request.user in conversation.participants.all()
            return True  # For conversation creation (handled in perform_create)

        elif request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
            # These methods will be checked at object level
            return True

        return False  # Block any other methods

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission to check if the user is a participant.
        Handles GET, PUT, PATCH, DELETE methods specifically.
        """
        # Check participant status based on object type
        if isinstance(obj, models.Conversation):
            return request.user in obj.participants.all()
        elif isinstance(obj, models.Message):
            return request.user in obj.conversation.participants.all()
        return False

    def _check_conversation_participation(self, user, conversation):
        """Helper method to check if user is conversation participant"""
        return user in conversation.participants.all()