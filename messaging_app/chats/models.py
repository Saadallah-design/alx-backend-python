from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin  

# Create your models here.
# create user model an extension of the AbstractBaseUser
# we can extend the default user model or even substitute it completely

class user(AbstractBaseUser):

    # Define user roles as choices using TextChoices and Enum
    class RoleChoices(models.TextChoices):
        GUEST = 'guest', 'Guest'
        HOST = 'host', 'Host'
        ADMIN = 'admin', 'Admin'
    
    user_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30, null=False)
    email = models.EmailField(unique=True, null=False)
    password_hash = models.CharField(max_length=128, null=False)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.GUEST,
        null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

# conversation model
class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    participants_id = models.ManyToManyField(user, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

# constraint to ensure that a user can only have one conversation with another user
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['participants_id'],
                name='unique_conversation_per_user_pair'
            )
        ]

# message model
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=False)
    sender_id = models.ForeignKey(user, on_delete=models.CASCADE, related_name='sent_messages')
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(auto_now_add=True)