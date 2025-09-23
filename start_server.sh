
#!/bin/bash

# Hurtrock Music Store - Universal Start Server Script
# Compatible with development and production environments
echo "[START] Starting Hurtrock Music Store..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[OK] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Load environment variables if .env exists
if [[ -f ".env" ]]; then
    print_step "Loading environment variables from .env"
    export $(grep -v '^#' .env | grep -v '^$' | xargs) 2>/dev/null || true
fi

# Detect Python command
PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    if command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
    else
        print_error "Python not found. Please install Python 3.x"
        exit 1
    fi
fi

print_step "Using Python command: $PYTHON_CMD"

# Function to check if port is available
check_port() {
    local port=$1
    local service_name=$2
    
    if command -v lsof >/dev/null 2>&1; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Port $port ($service_name) is already in use"
            return 1
        fi
    elif command -v netstat >/dev/null 2>&1; then
        if netstat -tuln | grep ":$port " >/dev/null 2>&1; then
            print_warning "Port $port ($service_name) is already in use"
            return 1
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -tuln | grep ":$port " >/dev/null 2>&1; then
            print_warning "Port $port ($service_name) is already in use"
            return 1
        fi
    else
        print_warning "Cannot check if port $port is available (no lsof/netstat/ss found)"
    fi
    return 0
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_step "Waiting for $service_name to be ready..."
    
    while [[ $attempt -le $max_attempts ]]; do
        if command -v curl >/dev/null 2>&1; then
            if curl -s --max-time 2 "$url" > /dev/null 2>&1; then
                print_success "$service_name is ready"
                return 0
            fi
        elif command -v wget >/dev/null 2>&1; then
            if wget -q --timeout=2 --tries=1 -O /dev/null "$url" 2>/dev/null; then
                print_success "$service_name is ready"
                return 0
            fi
        else
            # Fallback: just wait
            sleep 2
            print_success "$service_name should be ready (no curl/wget available)"
            return 0
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            print_warning "$service_name may not be fully ready after $max_attempts attempts"
            return 1
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
}

# Function to check if Django migrations are needed
check_django_migrations() {
    cd chat_service 2>/dev/null || {
        print_error "chat_service directory not found"
        return 1
    }
    
    export DJANGO_SETTINGS_MODULE=chat_microservice.settings
    
    print_step "Checking Django migrations..."
    
    # Check if migrations need to be created
    if ! $PYTHON_CMD manage.py showmigrations chat 2>/dev/null | grep -q "\[X\]"; then
        print_step "Creating Django migrations..."
        $PYTHON_CMD manage.py makemigrations chat || print_warning "Makemigrations failed"
    fi
    
    # Apply migrations
    print_step "Applying Django migrations..."
    $PYTHON_CMD manage.py migrate --run-syncdb 2>/dev/null || {
        print_warning "Migration failed, trying without --run-syncdb"
        $PYTHON_CMD manage.py migrate || print_warning "Migration still failed"
    }
    
    cd ..
}

# Function to start Django service
start_django_service() {
    print_step "Starting Django Chat Service..."
    
    # Check Django setup first
    check_django_migrations
    
    if ! check_port 8000 "Django Chat Service"; then
        print_error "Port 8000 is already in use. Please stop the existing service first."
        print_step "You can kill it with: sudo pkill -f 'manage.py runserver'"
        return 1
    fi
    
    cd chat_service || {
        print_error "chat_service directory not found"
        return 1
    }
    
    export DJANGO_SETTINGS_MODULE=chat_microservice.settings
    
    # Start Django with better error handling
    print_step "Launching Django on 0.0.0.0:8000..."
    nohup $PYTHON_CMD manage.py runserver 0.0.0.0:8000 --noreload > ../django.log 2>&1 &
    DJANGO_PID=$!
    
    echo $DJANGO_PID > ../django.pid
    print_success "Django Chat Service started (PID: $DJANGO_PID)"
    
    cd ..
    
    # Wait for Django to be ready
    wait_for_service "http://127.0.0.1:8000/health/" "Django Chat Service"
    
    return 0
}

# Function to start Flask service
start_flask_service() {
    print_step "Starting Flask Main Server..."
    
    if ! check_port 5000 "Flask Server"; then
        print_error "Port 5000 is already in use. Please stop the existing service first."
        print_step "You can kill it with: sudo pkill -f 'python.*main.py'"
        return 1
    fi
    
    # Test Flask configuration first
    if ! $PYTHON_CMD -c "from main import app; print('Flask app loaded successfully')" 2>/dev/null; then
        print_error "Flask application failed to load. Check your configuration."
        return 1
    fi
    
    print_step "Launching Flask on 0.0.0.0:5000..."
    nohup $PYTHON_CMD main.py > flask.log 2>&1 &
    FLASK_PID=$!
    
    echo $FLASK_PID > flask.pid
    print_success "Flask Server started (PID: $FLASK_PID)"
    
    # Wait for Flask to be ready
    wait_for_service "http://127.0.0.1:5000/" "Flask Server"
    
    return 0
}

# Function to stop services
stop_services() {
    print_step "Stopping all services..."
    
    # Stop Flask
    if [[ -f "flask.pid" ]]; then
        FLASK_PID=$(cat flask.pid)
        if kill -0 $FLASK_PID 2>/dev/null; then
            kill $FLASK_PID
            rm -f flask.pid
            print_success "Flask server stopped"
        fi
    fi
    
    # Stop Django
    if [[ -f "django.pid" ]]; then
        DJANGO_PID=$(cat django.pid)
        if kill -0 $DJANGO_PID 2>/dev/null; then
            kill $DJANGO_PID
            rm -f django.pid
            print_success "Django server stopped"
        fi
    fi
    
    # Fallback: kill by process name
    pkill -f "manage.py runserver" 2>/dev/null || true
    pkill -f "python.*main.py" 2>/dev/null || true
}

# Function to show status
show_status() {
    echo ""
    print_step "Service Status:"
    
    # Check Flask
    if [[ -f "flask.pid" ]]; then
        FLASK_PID=$(cat flask.pid)
        if kill -0 $FLASK_PID 2>/dev/null; then
            print_success "Flask Server: Running (PID: $FLASK_PID)"
        else
            print_warning "Flask Server: PID file exists but process not running"
            rm -f flask.pid
        fi
    else
        print_warning "Flask Server: Not running"
    fi
    
    # Check Django
    if [[ -f "django.pid" ]]; then
        DJANGO_PID=$(cat django.pid)
        if kill -0 $DJANGO_PID 2>/dev/null; then
            print_success "Django Chat Service: Running (PID: $DJANGO_PID)"
        else
            print_warning "Django Chat Service: PID file exists but process not running"
            rm -f django.pid
        fi
    else
        print_warning "Django Chat Service: Not running"
    fi
    
    echo ""
    print_step "Access URLs:"
    echo "  Main Store: http://localhost:5000"
    echo "  Admin Panel: http://localhost:5000/admin"
    echo "  Chat API: http://localhost:8000"
    echo "  Chat Interface: http://localhost:5000/admin/chat"
    echo ""
    print_step "Default Admin Login:"
    echo "  Email: admin@hurtrock.com"
    echo "  Password: admin123"
    echo ""
}

# Main execution
case "${1:-start}" in
    "start")
        print_step "Starting Hurtrock Music Store services..."
        
        # Start Django first
        if start_django_service; then
            sleep 3
            # Then start Flask
            if start_flask_service; then
                echo ""
                print_success "All services started successfully!"
                show_status
                
                print_step "Log files:"
                echo "  Django: django.log"
                echo "  Flask: flask.log"
                echo ""
                print_step "To stop services: $0 stop"
                print_step "To check status: $0 status"
                print_step "To view logs: $0 logs"
            else
                print_error "Failed to start Flask service"
                stop_services
                exit 1
            fi
        else
            print_error "Failed to start Django service"
            exit 1
        fi
        ;;
    
    "stop")
        stop_services
        print_success "All services stopped"
        ;;
    
    "restart")
        print_step "Restarting services..."
        stop_services
        sleep 2
        $0 start
        ;;
    
    "status")
        show_status
        ;;
    
    "logs")
        print_step "Showing service logs (press Ctrl+C to exit)..."
        if [[ -f "django.log" ]] && [[ -f "flask.log" ]]; then
            tail -f django.log flask.log
        elif [[ -f "django.log" ]]; then
            tail -f django.log
        elif [[ -f "flask.log" ]]; then
            tail -f flask.log
        else
            print_warning "No log files found"
        fi
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all services (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  status  - Show service status"
        echo "  logs    - Show live logs"
        exit 1
        ;;
esac

# Setup signal handlers for graceful shutdown
trap 'echo ""; print_step "Received interrupt signal, stopping services..."; stop_services; exit 0' INT TERM

# If starting services and script is run interactively, wait for interrupt
if [[ "${1:-start}" == "start" ]] && [[ -t 0 ]]; then
    echo ""
    print_step "Services are running. Press Ctrl+C to stop all services..."
    
    # Keep script running to handle signals
    while true; do
        sleep 10
        
        # Check if services are still running
        if [[ -f "flask.pid" ]]; then
            FLASK_PID=$(cat flask.pid)
            if ! kill -0 $FLASK_PID 2>/dev/null; then
                print_warning "Flask service stopped unexpectedly"
                rm -f flask.pid
            fi
        fi
        
        if [[ -f "django.pid" ]]; then
            DJANGO_PID=$(cat django.pid)
            if ! kill -0 $DJANGO_PID 2>/dev/null; then
                print_warning "Django service stopped unexpectedly"
                rm -f django.pid
            fi
        fi
    done
fi
