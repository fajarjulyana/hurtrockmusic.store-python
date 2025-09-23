#!/bin/bash

# Start script untuk Hurtrock Music Store
echo "[START] Memulai Hurtrock Music Store..."

# Define the Python command
PYTHON_CMD="python3"

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
        echo "[ERROR] Port 8000 (Django Chat) is already in use"
        echo "Please stop the existing service first"
        exit 1
    fi

    if ! check_port 5000; then
        echo "[ERROR] Port 5000 (Flask Server) is already in use"
        echo "Please stop the existing service first"
        exit 1
    fi

    echo "[SETUP] Preparing Django Chat Service..."
    cd chat_service

    # Set Django environment variables
    export DJANGO_SETTINGS_MODULE=chat_microservice.settings

    # Ensure migrations are up to date
    echo "[DJANGO] Checking migrations..."
    $PYTHON_CMD manage.py migrate --run-syncdb 2>/dev/null || true

    # Start Django Chat Service
    echo "[MOBILE] Starting Django Chat Service on port 8000..."
    $PYTHON_CMD manage.py runserver 0.0.0.0:8000 --noreload &
    DJANGO_PID=$!
    echo "Django Chat Service PID: $DJANGO_PID"
    cd ..

    # Wait for Django to start up
    echo "[WAIT] Waiting for Django to initialize..."
    sleep 5

    # Test Django connection
    for i in {1..10}; do
        if curl -s http://127.0.0.1:8000/health/ > /dev/null 2>&1; then
            echo "[OK] Django Chat Service is responding"
            break
        elif [[ $i -eq 10 ]]; then
            echo "[WARNING] Django Chat Service may not be fully ready"
        else
            echo "[WAIT] Waiting for Django... (attempt $i/10)"
            sleep 2
        fi
    done

    echo "[WEB] Starting Flask Server on port 5000..."
    $PYTHON_CMD main.py &
    FLASK_PID=$!
    echo "Flask Server PID: $FLASK_PID"

    echo ""
    echo "[OK] All services started successfully!"
    echo "[WEB] Main Store: http://localhost:5000"
    echo "[MOBILE] Chat Service: http://localhost:8000"
    echo "[LINK] Admin Panel: http://localhost:5000/admin"
    echo "[CHAT] Chat Interface: http://localhost:5000/admin/chat"
    echo ""
    echo "Default Admin Login:"
    echo "  Email: admin@hurtrock.com"
    echo "  Password: admin123"
    echo ""
    echo "Services PIDs:"
    echo "  Django Chat: $DJANGO_PID"
    echo "  Flask Store: $FLASK_PID"
    echo ""
    echo "Press Ctrl+C to stop all services..."

    # Wait for interrupt signal
    trap 'echo ""; echo "[STOP] Stopping all services..."; kill $DJANGO_PID $FLASK_PID 2>/dev/null; echo "[OK] All services stopped"; exit' INT
    wait
}

start_services