"""
URL configuration for chat_microservice project.
"""
from django.contrib import admin
from django.urls import path, include
from chat.health import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chat.urls')),
    path('health/', health_check, name='health_check'),
]