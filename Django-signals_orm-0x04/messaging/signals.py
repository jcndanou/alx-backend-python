from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory

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

@receiver(pre_save, sender=Message)
def track_message_edit(sender, instance, **kwargs):
    """
    Signal pour enregistrer les modifications de message avant sauvegarde
    """
    if instance.pk:  # Vérifie si le message existe déjà (c'est une mise à jour)
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:  # Si le contenu a changé
                # Crée un historique de la modification
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content
                )
                # Marque le message comme modifié
                instance.edited = True
        except Message.DoesNotExist:
            pass  # Le message n'existe pas encore (première création)