from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.db.models import Count, Q
from .models import Message, Notification

User = get_user_model()

@cache_page(60) # Cache la vue pour 60 secondes
def conversation_detail_view(request, conversation_id):
    # ... Votre logique de vue pour récupérer les messages de la conversation ...
    messages = Message.objects.filter(conversation_id=conversation_id).select_related('sender')
    context = {'messages': messages}
    return render(request, 'chats/conversation_detail.html', context)

@require_POST
@login_required
def delete_user(request):
    """Vue pour supprimer le compte utilisateur"""
    user = request.user
    user.delete()
    messages.success(request, "Votre compte a été supprimé avec succès.")
    return redirect('home')  # Redirigez vers la page d'accueil ou une autre vue appropriée


@login_required
def message_thread(request, message_id):
    """Affiche une conversation threadée avec optimisation"""
    cache_key = f'message_thread_{message_id}_{request.user.id}'
    thread = cache.get(cache_key)

    if not thread:
        main_message = get_object_or_404(
            Message.objects.select_related('sender', 'receiver'),
            Q(id=message_id),
            Q(sender=request.user) | Q(receiver=request.user)
            # Sécurité: vérifie que l'utilisateur fait partie de la conversation
        )
        thread = main_message.get_thread()
        cache.set(cache_key, thread, timeout=300)  # Cache pour 5 minutes

    return render(request, 'messaging/thread.html', {'thread': thread})


@login_required
def inbox(request):
    """Boîte de réception avec optimisations"""
    # Récupère les conversations avec le dernier message et le nombre de non-lus
    conversations = Message.objects.filter(
        receiver=request.user,
        parent_message__isnull=True  # Seulement les messages initiaux
    ).annotate(
        reply_count=Count('replies'),
        unread_count=Count('replies', filter=Q(replies__read=False))
    ).select_related('sender').order_by('-timestamp')

    return render(request, 'messaging/inbox.html', {'conversations': conversations})


@login_required
def conversation(request, user_id):
    """Affiche une conversation avec un utilisateur spécifique"""
    other_user = get_object_or_404(User, id=user_id)

    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).select_related('sender', 'receiver').order_by('timestamp')

    return render(request, 'messaging/conversation.html', {
        'messages': messages,
        'other_user': other_user
    })


@login_required
def inbox_view(request):
    """
    Vue pour afficher les messages non lus avec optimisation des requêtes
    Utilise le manager personnalisé comme spécifié
    """
    # Utilisation du manager personnalisé avec la méthode exacte demandée
    unread_messages = Message.unread.unread_for_user(request.user).select_related(
        'sender'
    ).only(
        'sender__username',
        'content',
        'timestamp',
        'read'
    ).order_by('-timestamp')

    return render(request, 'messaging/inbox.html', {
        'unread_messages': unread_messages
    })