from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers  # Renommage pour éviter les conflits
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Routeur principal - format exact demandé
router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'conversations', ConversationViewSet, basename='conversations')

# Routeur imbriqué pour les messages
conversations_router = nested_routers.NestedSimpleRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]