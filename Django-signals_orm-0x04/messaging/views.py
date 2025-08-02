from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

User = get_user_model()

@require_POST
@login_required
def delete_user(request):
    """Vue pour supprimer le compte utilisateur"""
    user = request.user
    user.delete()
    messages.success(request, "Votre compte a été supprimé avec succès.")
    return redirect('home')  # Redirigez vers la page d'accueil ou une autre vue appropriée