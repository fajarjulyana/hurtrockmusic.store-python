
"""
Chat models for the microservice
"""
from django.db import models
from django.utils import timezone


class ChatRoom(models.Model):
    """Chat room model"""
    name = models.CharField(max_length=100, unique=True, db_index=True)
    buyer_id = models.IntegerField(null=True, blank=True, db_index=True)
    buyer_name = models.CharField(max_length=255, null=True, blank=True)
    buyer_email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'chat_rooms'
    
    def __str__(self):
        if self.buyer_name:
            return f"Room: {self.buyer_name} ({self.buyer_email})"
        return f"Room: {self.name}"


class ChatMessage(models.Model):
    """Chat message model"""
    SENDER_TYPES = [
        ('buyer', 'Buyer'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    
    room = models.ForeignKey(
        ChatRoom, 
        on_delete=models.CASCADE, 
        related_name='messages',
        db_index=True
    )
    user_id = models.IntegerField(db_index=True)
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField()
    message = models.TextField()
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPES, default='buyer')
    product_id = models.IntegerField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'chat_messages'
    
    def __str__(self):
        return f"{self.user_name}: {self.message[:50]}..."


class ChatSession(models.Model):
    """Chat session tracking"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='sessions')
    user_id = models.IntegerField(db_index=True)
    user_name = models.CharField(max_length=255)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-started_at']
        db_table = 'chat_sessions'
    
    def __str__(self):
        return f"Session: {self.user_name} in {self.room.name}"
