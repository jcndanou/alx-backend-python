from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Crée une notification lorsqu'un nouveau message est reçu
    """
    if created:
        Notification.objects.create(
            user=instance.recipient,
            message=instance,
            notification_type='MESSAGE',
            message_preview=f"New message from {instance.sender.username}: {instance.content[:50]}..."
        )