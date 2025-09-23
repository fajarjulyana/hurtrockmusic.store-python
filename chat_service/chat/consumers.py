import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from .models import ChatRoom, ChatMessage, ChatSession
from django.utils import timezone
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract room name from URL
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Get token from query parameters
        token = None
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        if 'token=' in query_string:
            token = query_string.split('token=')[1].split('&')[0]

        if not token:
            logger.error("No token provided for WebSocket connection")
            await self.close()
            return

        # Verify JWT token
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            self.user_data = {
                'id': payload['user_id'],
                'email': payload['email'],
                'name': payload['name'],
                'role': payload['role']
            }
        except jwt.ExpiredSignatureError:
            logger.error("Token expired for WebSocket connection")
            await self.close()
            return
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token for WebSocket connection: {e}")
            await self.close()
            return

        # Get or create chat room
        self.room = await self.get_or_create_room()

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

        # Create or update chat session
        await self.create_or_update_session()

        # Send connection established message that client expects
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Chat connection established successfully'
        }))

        logger.info(f"User {self.user_data['name']} connected to room {self.room_name}")

    async def disconnect(self, close_code):
        # Update session end time
        if hasattr(self, 'session'):
            await self.update_session_end_time()

        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        logger.info(f"User disconnected from room {getattr(self, 'room_name', 'unknown')}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'chat_message')

            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'typing':
                await self.handle_typing(text_data_json)
            elif message_type == 'mark_read':
                await self.handle_mark_read(text_data_json)

        except json.JSONDecodeError:
            logger.error("Invalid JSON received in WebSocket")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    async def handle_chat_message(self, data):
        message_text = data.get('message', '').strip()
        product_id = data.get('product_id')

        if not message_text:
            return

        # Save message to database
        message = await self.save_message(message_text, product_id)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'message': message.message,
                    'sender_type': message.sender_type,
                    'user_id': message.user_id,
                    'user_name': message.user_name,
                    'user_email': message.user_email,
                    'product_id': message.product_id,
                    'created_at': message.created_at.isoformat(),
                    'timestamp': message.created_at.strftime('%H:%M')
                }
            }
        )

    async def handle_typing(self, data):
        # Broadcast typing status to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_status',
                'user_name': self.user_data['name'],
                'is_typing': data.get('is_typing', False)
            }
        )

    async def handle_mark_read(self, data):
        # Mark messages as read for this user
        await self.mark_messages_read()

    # WebSocket message handlers
    async def chat_message(self, event):
        message_data = event['message']
        # Send flattened message format that client expects
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'id': message_data['id'],
            'message': message_data['message'],
            'sender_type': message_data['sender_type'],
            'user_id': message_data['user_id'],
            'user_name': message_data['user_name'],
            'user_email': message_data['user_email'],
            'product_id': message_data['product_id'],
            'created_at': message_data['created_at'],
            'timestamp': message_data['timestamp']
        }))

    async def typing_status(self, event):
        # Don't send typing status back to the sender
        if event.get('user_name') != self.user_data['name']:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_name': event['user_name'],
                'is_typing': event['is_typing']
            }))

    # Database operations using database_sync_to_async
    @database_sync_to_async
    def get_or_create_room(self):
        room, created = ChatRoom.objects.get_or_create(
            name=self.room_name,
            defaults={
                'buyer_id': self.user_data['id'] if self.user_data['role'] == 'buyer' else None,
                'buyer_name': self.user_data['name'] if self.user_data['role'] == 'buyer' else None,
                'buyer_email': self.user_data['email'] if self.user_data['role'] == 'buyer' else None,
            }
        )
        return room

    @database_sync_to_async
    def save_message(self, message_text, product_id=None):
        # Determine sender type based on user role
        sender_type = 'admin' if self.user_data['role'] in ['admin', 'staff'] else 'buyer'

        message = ChatMessage.objects.create(
            room=self.room,
            user_id=self.user_data['id'],
            user_name=self.user_data['name'],
            user_email=self.user_data['email'],
            message=message_text,
            sender_type=sender_type,
            product_id=product_id
        )
        return message

    @database_sync_to_async
    def create_or_update_session(self):
        self.session, created = ChatSession.objects.get_or_create(
            room=self.room,
            user_id=self.user_data['id'],
            ended_at__isnull=True,
            defaults={
                'user_name': self.user_data['name'],
                'started_at': timezone.now()
            }
        )
        if not created:
            # Update existing session
            self.session.started_at = timezone.now()
            self.session.save()

    @database_sync_to_async
    def update_session_end_time(self):
        if hasattr(self, 'session'):
            self.session.ended_at = timezone.now()
            self.session.save()

    @database_sync_to_async
    def mark_messages_read(self):
        # This could be implemented to track read status
        # For now, we'll just log it
        logger.info(f"Messages marked as read by {self.user_data['name']} in room {self.room_name}")