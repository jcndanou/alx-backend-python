from django.db import models

class UnreadMessagesManager(models.Manager):
    """
    Manager personnalisé pour les messages non lus
    """
    def for_user(self, user):
        """
        Retourne les messages non lus pour un utilisateur spécifique
        """
        return self.filter(receiver=user, read=False)