"""
URL patterns for chat REST API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import health

router = DefaultRouter()
router.register(r'rooms', views.ChatRoomViewSet)
router.register(r'messages', views.ChatMessageViewSet)

urlpatterns = [
    # REST API endpoints
    path('api/', include(router.urls)),

    # Health check endpoints
    path('health/', health.health_check_simple, name='health_check'),
    path('health/detailed/', health.health_check_detailed, name='health_check_detailed'),

    # Chat room specific endpoints
    path('api/rooms/<str:room_name>/messages/', views.ChatRoomMessagesView.as_view(), name='room_messages'),
    path('api/rooms/<str:room_name>/join/', views.JoinChatRoomView.as_view(), name='join_room'),
    path('api/rooms/<str:room_name>/mark-read/', views.MarkMessagesAsReadView.as_view(), name='mark-messages-read'),

    # Product tagging endpoints
    path('api/messages/<int:message_id>/tag-product/', views.TagProductView.as_view(), name='tag_product'),

    # Admin endpoints
    path('api/admin/pending-chats/', views.PendingChatsView.as_view(), name='pending_chats'),
    path('api/admin/chat-stats/', views.ChatStatsView.as_view(), name='chat_stats'),
    path('api/admin/buyer-rooms/', views.BuyerChatRoomsView.as_view(), name='buyer-chat-rooms'),
]