from django.urls import path, include
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Routeur principal
router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'conversations', ConversationViewSet, basename='conversations')

# Routeur imbriqué pour les messages - Utilisation de NestedDefaultRouter
conversations_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]