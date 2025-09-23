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
        try:
            # Extract room name from URL
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'
            self.reconnect_attempts = 0
            self.max_reconnect_attempts = 5
            self.heartbeat_interval = 30  # seconds
            self.last_heartbeat = None

            # Get token from query parameters
            token = None
            query_string = self.scope.get('query_string', b'').decode('utf-8')
            if 'token=' in query_string:
                token = query_string.split('token=')[1].split('&')[0]

            if not token:
                logger.error("No token provided for WebSocket connection")
                await self.send_error_and_close("Authentication required")
                return

            # Verify JWT token with retry mechanism
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
                await self.send_error_and_close("Token expired")
                return
            except jwt.InvalidTokenError as e:
                logger.error(f"Invalid token for WebSocket connection: {e}")
                await self.send_error_and_close("Invalid token")
                return

            # Get or create chat room with retry
            try:
                self.room = await self.get_or_create_room()
            except Exception as e:
                logger.error(f"Failed to get/create room: {e}")
                await self.send_error_and_close("Database error")
                return

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Accept the WebSocket connection
            await self.accept()

            # Send connection established message
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': f'Connected to room {self.room_name}',
                'user_id': self.user_data['id'],
                'user_name': self.user_data['name']
            }))

            # Create or update chat session
            await self.create_or_update_session()

            # Start heartbeat
            await self.start_heartbeat()

            logger.info(f"User {self.user_data['name']} ({self.user_data['role']}) connected to room {self.room_name}")

        except Exception as e:
            logger.error(f"Error during WebSocket connection: {str(e)}", exc_info=True)
            await self.send_error_and_close("Connection failed")

    async def send_error_and_close(self, error_message):
        """Send error message and close connection"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': error_message
            }))
        except:
            pass
        finally:
            await self.close()

    async def start_heartbeat(self):
        """Start heartbeat to keep connection alive"""
        import asyncio
        self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())

    async def heartbeat_loop(self):
        """Send periodic heartbeat to maintain connection"""
        import asyncio
        from django.utils import timezone
        
        try:
            while True:
                await asyncio.sleep(self.heartbeat_interval)
                self.last_heartbeat = timezone.now()
                await self.send(text_data=json.dumps({
                    'type': 'heartbeat',
                    'timestamp': self.last_heartbeat.isoformat()
                }))
        except asyncio.CancelledError:
            logger.info("Heartbeat cancelled")
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            # Cancel heartbeat task
            if hasattr(self, 'heartbeat_task') and not self.heartbeat_task.done():
                self.heartbeat_task.cancel()

            # Update session end time
            if hasattr(self, 'session') and self.session:
                await self.update_session_end_time()

            # Leave room group
            if hasattr(self, 'room_group_name') and hasattr(self, 'channel_name'):
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )

            # Send disconnect notification to other users in room
            if hasattr(self, 'room_group_name') and hasattr(self, 'user_data'):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_disconnect',
                        'user_id': self.user_data['id'],
                        'user_name': self.user_data['name'],
                        'disconnect_time': timezone.now().isoformat()
                    }
                )

            logger.info(f"User {getattr(self, 'user_data', {}).get('name', 'unknown')} disconnected from room {getattr(self, 'room_name', 'unknown')} (code: {close_code})")

        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}", exc_info=True)

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'chat_message')

            logger.info(f"Received message type: {message_type} for room: {self.room_name}")
            logger.debug(f"Message data: {text_data_json}")

            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'join_room':
                await self.handle_join_room(text_data_json)
            elif message_type == 'mark_read':
                await self.handle_mark_read(text_data_json)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send(text_data=json.dumps({
                    'error': f'Unknown message type: {message_type}'
                }))

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({
                'error': 'Internal server error'
            }))

    async def handle_chat_message(self, data):
        message_text = data.get('message', '').strip()
        product_id = data.get('product_id')

        if not message_text:
            logger.warning("Received empty message text.")
            return

        try:
            # Save message to database
            message = await self.save_message(self.room, self.user_data, message_text, product_id)

            logger.info(f"Message saved to database: ID {message.id}")

            # Get product info if product_id is provided
            product_info = None
            if product_id:
                product_info = await self.get_product_info(product_id)
                logger.info(f"Product info retrieved for product ID {product_id}: {product_info}")

            # Prepare message data
            message_data = {
                'id': message.id,
                'message': message.message,
                'sender_type': message.sender_type,
                'user_name': message.user_name,
                'user_email': message.user_email,
                'user_id': message.user_id,
                'product_id': message.product_id,
                'created_at': message.created_at.isoformat(),
                'timestamp': message.created_at.isoformat(),
                'room_name': self.room_name
            }

            if product_info:
                message_data['product_info'] = product_info

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )

            logger.info(f"Message sent to room {self.room_name} by {self.user_data['name']} (Message ID: {message.id})")

        except Exception as e:
            logger.error(f"Error handling chat message: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Gagal mengirim pesan. Silakan coba lagi.'
            }))

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

    async def handle_join_room(self, data):
        # This is a placeholder for future functionality if needed
        logger.info(f"User {self.user_data['name']} joined room {self.room_name}")
        pass

    # WebSocket message handlers
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))

    async def typing_status(self, event):
        # Don't send typing status back to the sender
        if event.get('user_name') != self.user_data['name']:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_name': event['user_name'],
                'is_typing': event['is_typing']
            }))

    async def user_disconnect(self, event):
        # Don't send disconnect notification to the user who disconnected
        if event.get('user_id') != self.user_data['id']:
            await self.send(text_data=json.dumps({
                'type': 'user_offline',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'disconnect_time': event['disconnect_time']
            }))

    async def notification_message(self, event):
        # Send notification to user
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
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
                'is_active': True
            }
        )

        # Update buyer info if room exists but buyer info is missing or outdated
        if not created and self.user_data['role'] == 'buyer':
            if not room.buyer_id or room.buyer_id != self.user_data['id']:
                room.buyer_id = self.user_data['id']
                room.buyer_name = self.user_data['name']
                room.buyer_email = self.user_data['email']
                room.save()
                logger.info(f"Updated buyer info for room {self.room_name}")

        logger.info(f"Room '{self.room_name}' accessed. Created: {created}")
        return room

    @database_sync_to_async
    def save_message(self, room, user_data, message_text, product_id=None):
        """Save message to database with proper validation"""
        try:
            # Validate required fields
            user_id = user_data.get('id', 0)
            user_name = user_data.get('name', 'Anonymous')
            user_email = user_data.get('email', '')
            sender_type = user_data.get('role', 'buyer')

            # Ensure sender_type is valid
            valid_sender_types = ['buyer', 'admin', 'staff']
            if sender_type not in valid_sender_types:
                logger.warning(f"Invalid sender type '{sender_type}' for user {user_id}. Defaulting to 'buyer'.")
                sender_type = 'buyer'

            logger.info(f"Saving message to room {room.name}: user_id={user_id}, name={user_name}, type={sender_type}")

            from django.db import transaction
            with transaction.atomic():
                message = ChatMessage.objects.create(
                    room=room,
                    user_id=user_id,
                    user_name=user_name,
                    user_email=user_email,
                    message=message_text,
                    sender_type=sender_type,
                    product_id=product_id,
                    created_at=timezone.now()
                )

                # Verify the message was saved
                saved_message = ChatMessage.objects.get(id=message.id)
                logger.info(f"Message successfully saved with ID: {saved_message.id}")

            return message
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}", exc_info=True)
            raise

    @database_sync_to_async
    def get_product_info(self, product_id):
        """Fetch product information from Flask API"""
        try:
            import requests
            # Use internal communication - try different endpoints
            endpoints = [
                f'http://127.0.0.1:5000/api/products/{product_id}',
                f'http://localhost:5000/api/products/{product_id}',
                f'http://0.0.0.0:5000/api/products/{product_id}'
            ]

            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=3)
                    if response.status_code == 200:
                        product_data = response.json()
                        logger.info(f"Product info fetched successfully from {endpoint}")
                        return product_data
                except requests.exceptions.RequestException:
                    continue

            logger.warning(f"Failed to fetch product info for ID {product_id} from any endpoint.")
            return None

        except Exception as e:
            logger.error(f"Error fetching product info: {e}", exc_info=True)
            return None

    @database_sync_to_async
    def create_or_update_session(self):
        try:
            self.session, created = ChatSession.objects.get_or_create(
                room=self.room,
                user_id=self.user_data['id'],
                ended_at__isnull=True,
                defaults={
                    'user_name': self.user_data['name'],
                    'user_email': self.user_data['email'],
                    'user_role': self.user_data['role'],
                    'started_at': timezone.now()
                }
            )
            if not created:
                # Update existing session if it's still active
                self.session.started_at = timezone.now()
                self.session.save()
                logger.info(f"Updated active chat session for user {self.user_data['id']} in room {self.room.name}")
            else:
                logger.info(f"Created new chat session for user {self.user_data['id']} in room {self.room.name}")
        except Exception as e:
            logger.error(f"Error creating or updating chat session: {str(e)}", exc_info=True)


    @database_sync_to_async
    def update_session_end_time(self):
        if hasattr(self, 'session') and self.session and self.session.ended_at is None:
            try:
                self.session.ended_at = timezone.now()
                self.session.save()
                logger.info(f"Updated end time for chat session ID {self.session.id}")
            except Exception as e:
                logger.error(f"Error updating session end time: {str(e)}", exc_info=True)


    @database_sync_to_async
    def mark_messages_read(self):
        # This could be implemented to track read status
        # For now, we'll just log it
        logger.info(f"Messages marked as read by {self.user_data['name']} in room {self.room_name}")