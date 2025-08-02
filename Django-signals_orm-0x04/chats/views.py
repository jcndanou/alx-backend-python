from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from django.http import Http404

from .filters import MessageFilter, ConversationFilter
from .pagination import MessagePagination
from .permissions import IsParticipantOfConversation
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    MessageDetailSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Endpoint pour récupérer l'utilisateur connecté"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConversationFilter

    def get_queryset(self):
        """Ne retourne que les conversations de l'utilisateur connecté"""
        if self.request.user.is_authenticated:
            # Filtrer les conversations où l'utilisateur est un participant
            return Conversation.objects.filter(participants=self.request.user).order_by('-created_at')
        return Conversation.objects.none() # Aucun résultat si non authentifié

    def get_serializer_class(self):
        """Utilise le serializer détaillé pour la récupération"""
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Ajoute automatiquement l'utilisateur comme participant"""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Ajoute un participant à une conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(pk=user_id)
            conversation.participants.add(user)
            return Response({'status': 'participant added'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    def get_object(self):
        """Surcharge pour vérifier explicitement les permissions avec conversation_id"""
        try:
            obj = super().get_object()
            # Vérification explicite de la participation
            if not obj.participants.filter(id=self.request.user.id).exists():
                raise PermissionDenied("You are not a participant of this conversation")
            return obj
        except Http404:
            # Si la conversation n'existe pas, retourner 403 au lieu de 404 pour la sécurité
            raise PermissionDenied("Conversation not found or access denied")
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsParticipantOfConversation])
    def send_message(self, request, pk=None):
        conversation = self.get_object()  # Utilise get_object qui vérifie déjà les permissions
        
        # Vérification redondante pour être explicite (optionnel mais recommandé)
        if not conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {"detail": "You are not a participant of this conversation"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                message_body=serializer.validated_data['message_body']
            )
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-sent_at')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        """Filtre les messages visibles par l'utilisateur où l'utilisateur est participant"""
        if self.request.user.is_authenticated:
            return Message.objects.filter(
                conversation__participants=self.request.user
            ).order_by('sent_at') # Les messages d'une conversation doivent être triés par date
        return Message.objects.none()

    def get_serializer_class(self):
        """Utilise le serializer détaillé pour la récupération"""
        if self.action in ['retrieve', 'list']:
            return MessageDetailSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Définit automatiquement l'expéditeur"""
        serializer.save(sender=self.request.user)

    def get_object(self):
        """Surcharge pour vérifier explicitement les permissions avec conversation_id"""
        try:
            obj = super().get_object()
            # Vérification explicite que l'utilisateur est participant de la conversation
            if not obj.conversation.participants.filter(id=self.request.user.id).exists():
                raise PermissionDenied("You are not a participant of this conversation")
            return obj
        except Http404:
            # Si le message n'existe pas, retourner 403 au lieu de 404 pour la sécurité
            raise PermissionDenied("Message not found or access denied")

    @action(detail=True, methods=['get'])
    def conversation_messages(self, request, pk=None):
        """Récupère tous les messages d'une conversation spécifique"""
        try:
            # Récupération explicite avec vérification de permission
            conversation = Conversation.objects.get(pk=pk)
            if not conversation.participants.filter(id=request.user.id).exists():
                return Response(
                    {"detail": "You are not a participant of this conversation"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            messages = Message.objects.filter(
                conversation=conversation
            ).order_by('sent_at')
            serializer = self.get_serializer(messages, many=True)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response(
                {"detail": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND
            )