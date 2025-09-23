"""
JWT Authentication for Django Chat Service
"""
import jwt
import json
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser


class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT Authentication for Flask-Django integration
    """

    def authenticate(self, request):
        """
        Returns a `User` instance if JWT token is valid, otherwise `None`.
        """
        token = self.get_jwt_from_request(request)
        if not token:
            return None

        try:
            payload = self.decode_jwt_token(token)
            user_data = self.get_user_from_payload(payload)
            return (user_data, token)
        except Exception as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')

    def get_jwt_from_request(self, request):
        """
        Extract JWT token from request headers or query parameters
        """
        # Try Authorization header first
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix

        # Try query parameter for WebSocket connections
        return request.GET.get('token')

    def decode_jwt_token(self, token):
        """
        Decode JWT token and return payload
        """
        try:
            # Use the same secret key as Flask app
            secret_key = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])

            # Check if token is expired
            exp_timestamp = payload.get('exp')
            if exp_timestamp and datetime.utcfromtimestamp(exp_timestamp) < datetime.utcnow():
                raise AuthenticationFailed('Token has expired')

            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')

    def get_user_from_payload(self, payload):
        """
        Create user object from JWT payload
        """
        return {
            'id': payload.get('user_id'),
            'email': payload.get('email'),
            'name': payload.get('name'),
            'role': payload.get('role', 'buyer'),
            'is_authenticated': True,
            'is_admin': payload.get('role') == 'admin',
            'is_staff': payload.get('role') in ['admin', 'staff']
        }


def get_user_from_token(token):
    """
    Helper function to get user data from JWT token
    """
    try:
        auth = JWTAuthentication()
        payload = auth.decode_jwt_token(token)
        return auth.get_user_from_payload(payload)
    except Exception as e:
        print(f"Error decoding JWT token: {str(e)}")
        return None


class MockRequest:
    """Mock request for token validation"""
    def __init__(self, token=None):
        self.GET = {'token': token} if token else {}
        self.META = {}


def authenticate_websocket(token):
    """
    Authenticate WebSocket connection using JWT token
    """
    try:
        if not token:
            return None

        auth = JWTAuthentication()
        mock_request = MockRequest(token)
        result = auth.authenticate(mock_request)

        if result:
            user_data, _ = result
            return user_data
        return None
    except Exception as e:
        print(f"WebSocket authentication error: {str(e)}")
        return None