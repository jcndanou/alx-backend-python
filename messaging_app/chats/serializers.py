from rest_framework import serializers
from .models import User, Conversation, Message
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(
        source='get_role_display', 
        read_only=True
    )

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 
                 'phone_number', 'role', 'created_at']
        extra_kwargs = {
            'password_hash': {'write_only': True},
            'created_at': {'read_only': True}
        }
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value
    
    def create(self, validated_data):
        validated_data['password_hash'] = make_password(validated_data.get('password_hash', ''))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password_hash' in validated_data:
            validated_data['password_hash'] = make_password(validated_data['password_hash'])
        return super().update(instance, validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )
    participants_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at']
        extra_kwargs = {
            'created_at': {'read_only': True}
        }
    
    def get_participants_count(self, obj):
        return obj.participants.count()

    def validate_participants(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Une conversation doit avoir au moins 2 participants.")
        return value


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    conversation = serializers.PrimaryKeyRelatedField(
        queryset=Conversation.objects.all()
    )
    preview = serializers.CharField(
        max_length=50,
        read_only=True,
        source='get_preview'
    )

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 
                 'message_body', 'preview', 'sent_at']
        extra_kwargs = {
            'sent_at': {'read_only': True},
            'message_body': {'required': True}
        }
    
    def validate_message_body(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Le message ne peut pas être vide.")
        return value


class MessageDetailSerializer(MessageSerializer):
    sender = UserSerializer(read_only=True)
    is_owner = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.sender


class ConversationDetailSerializer(ConversationSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages', 'last_message']

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        return MessageSerializer(last_msg).data if last_msg else None