#!/bin/bash

# Start script untuk Hurtrock Music Store
echo "🚀 Memulai Hurtrock Music Store..."

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "Port $port is already in use"
        return 1
    fi
    return 0
}

# Function to start services
start_services() {
    # Check if ports are available
    if ! check_port 8000; then
        echo "❌ Port 8000 (Django Chat) is already in use"
        echo "Please stop the existing service first"
        exit 1
    fi
    
    if ! check_port 5000; then
        echo "❌ Port 5000 (Flask Server) is already in use"
        echo "Please stop the existing service first"
        exit 1
    fi
    
    echo "📱 Starting Django Chat Service on port 8000..."
    cd chat_service
    python3 manage.py runserver 0.0.0.0:8000 --noreload &
    DJANGO_PID=$!
    echo "Django Chat Service PID: $DJANGO_PID"
    cd ..
    
    # Wait a moment for Django to start
    sleep 3
    
    echo "🌐 Starting Flask Server on port 5000..."
    python3 main.py &
    FLASK_PID=$!
    echo "Flask Server PID: $FLASK_PID"
    
    echo ""
    echo "✅ All services started successfully!"
    echo "🌐 Main Store: http://localhost:5000"
    echo "📱 Chat Service: http://localhost:8000"
    echo "🔗 Admin Panel: http://localhost:5000/admin"
    echo "💬 Chat Interface: http://localhost:5000/admin/chat"
    echo ""
    echo "Services PIDs:"
    echo "  Django Chat: $DJANGO_PID"
    echo "  Flask Store: $FLASK_PID"
    echo ""
    echo "Press Ctrl+C to stop all services..."
    
    # Wait for interrupt signal
    trap 'echo ""; echo "🛑 Stopping all services..."; kill $DJANGO_PID $FLASK_PID 2>/dev/null; echo "✅ All services stopped"; exit' INT
    wait
}

start_services
