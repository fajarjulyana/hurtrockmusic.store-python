"""
Serializers for chat microservice REST API
"""
from rest_framework import serializers
from .models import ChatRoom, ChatMessage, ChatSession


class ChatRoomSerializer(serializers.ModelSerializer):
    """
    Serializer for ChatRoom model
    """
    message_count = serializers.ReadOnlyField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'created_at', 'is_active', 
            'message_count', 'last_message'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_last_message(self, obj):
        """Get formatted last message"""
        last_msg = obj.last_message
        if last_msg:
            return {
                'id': last_msg.id,
                'user_name': last_msg.user_name,
                'message': last_msg.message[:100],  # Truncate long messages
                'created_at': last_msg.created_at.isoformat(),
                'sender_type': last_msg.sender_type
            }
        return None


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for ChatMessage model
    """
    room_name = serializers.CharField(source='room.name', read_only=True)
    formatted_created_at = serializers.ReadOnlyField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'room', 'room_name', 'user_id', 'user_name', 'user_email',
            'message', 'sender_type', 'product_id', 'created_at', 
            'formatted_created_at', 'is_read', 'is_deleted'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'formatted_created_at'
        ]
    
    def validate_message(self, value):
        """Validate message content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Pesan tidak boleh kosong")
        
        if len(value.strip()) > 2000:
            raise serializers.ValidationError("Pesan terlalu panjang (maksimal 2000 karakter)")
        
        return value.strip()


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new chat messages
    """
    room_name = serializers.CharField(write_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'room_name', 'message', 'sender_type', 'product_id'
        ]
    
    def create(self, validated_data):
        """Create message with room lookup"""
        room_name = validated_data.pop('room_name')
        room, created = ChatRoom.objects.get_or_create(name=room_name)
        validated_data['room'] = room
        
        # Set user info from request context
        request = self.context.get('request')
        if request and request.user:
            validated_data['user_id'] = request.user.id
            validated_data['user_name'] = request.user.name
            validated_data['user_email'] = request.user.email
        
        return super().create(validated_data)


class ChatSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for ChatSession model
    """
    room_name = serializers.CharField(source='room.name', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'room', 'room_name', 'user_id', 'user_name',
            'started_at', 'ended_at', 'is_active', 'duration_seconds'
        ]
        read_only_fields = ['id', 'started_at', 'ended_at']
    
    def get_duration_seconds(self, obj):
        """Get session duration in seconds"""
        duration = obj.duration
        return int(duration.total_seconds()) if duration else 0


class ProductTagSerializer(serializers.Serializer):
    """
    Serializer for product tagging requests
    """
    product_id = serializers.IntegerField(min_value=1)
    
    def validate_product_id(self, value):
        """Validate product ID (should exist in Flask app)"""
        # Note: We can't validate against Flask DB here, 
        # but we can do basic validation
        if value <= 0:
            raise serializers.ValidationError("Product ID harus positif")
        return value


class RoomJoinSerializer(serializers.Serializer):
    """
    Serializer for joining chat rooms
    """
    room_name = serializers.CharField(max_length=100)
    
    def validate_room_name(self, value):
        """Validate room name format"""
        if not value or not value.strip():
            raise serializers.ValidationError("Nama room tidak boleh kosong")
        
        # Basic validation for room name format
        value = value.strip().lower()
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("Nama room hanya boleh mengandung huruf, angka, underscore, dan dash")
        
        return value


class ChatStatsSerializer(serializers.Serializer):
    """
    Serializer for chat statistics response
    """
    total_rooms = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    messages_by_type = serializers.ListField(child=serializers.DictField())
    recent_activity = serializers.ListField(child=serializers.DictField())
    top_rooms = serializers.ListField(child=serializers.DictField())