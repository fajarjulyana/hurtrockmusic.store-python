"""
URL configuration for chat_microservice project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', include('chat.urls')),
    path('api/', include('chat.urls')),  # Include direct API access to rooms
    path('health/', include('chat.urls')),  # Health check endpoint
]