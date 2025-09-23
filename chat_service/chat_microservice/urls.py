"""
URL configuration for chat_microservice project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chat.urls')),  # Include chat URLs directly under /api/
    path('health/', include('chat.urls')),  # Health check endpoint
]