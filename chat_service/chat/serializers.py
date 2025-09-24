"""
Serializers for chat models
"""
from rest_framework import serializers
from .models import ChatRoom, ChatMessage, ChatSession


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for ChatRoom model"""
    message_count = serializers.ReadOnlyField()
    unread_messages_count = serializers.ReadOnlyField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'buyer_id', 'buyer_name', 'buyer_email',
            'created_at', 'is_active', 'message_count', 'unread_messages_count'
        ]
        read_only_fields = ['id', 'created_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage model"""
    formatted_created_at = serializers.ReadOnlyField()

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'room', 'user_id', 'user_name', 'user_email', 'message',
            'sender_type', 'product_id', 'is_read', 'is_deleted',
            'created_at', 'updated_at', 'formatted_created_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for ChatSession model"""
    duration = serializers.ReadOnlyField()

    class Meta:
        model = ChatSession
        fields = [
            'id', 'room', 'user_id', 'user_name', 'user_email', 'user_role',
            'started_at', 'ended_at', 'is_active', 'duration'
        ]
        read_only_fields = ['id', 'started_at']