from django.db import models
from django.contrib.auth import get_user_model
from .managers import UnreadMessagesManager

User = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # Champ déjà présent
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='edited_messages')

    # Managers
    objects = models.Manager()  # Manager par défaut
    unread = UnreadMessagesManager()  # Manager personnalisé pour les messages non lus

    def __str__(self):
        return f"Message {self.id} from {self.sender} to {self.receiver}"

    class Meta:
        ordering = ['-timestamp']

    def get_thread(self):
        """Récupère toute la conversation threadée"""
        return Message.objects.filter(
            models.Q(id=self.id) |
            models.Q(parent_message=self.id)
        ).select_related('sender', 'receiver').order_by('timestamp')


class MessageHistory(models.Model):
    """Modèle pour stocker l'historique des modifications des messages"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    modified_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                  null=True, blank=True,
                                  related_name='message_modifications')  # Nouveau champ

    class Meta:
        verbose_name_plural = "Message Histories"
        ordering = ['-modified_at']

    def __str__(self):
        return f"History for Message {self.message.id} ({self.modified_at})"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('MESSAGE', 'New Message'),
        ('ALERT', 'System Alert'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='MESSAGE')
    message_preview = models.CharField(max_length=100)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user} - {self.get_notification_type_display()}"