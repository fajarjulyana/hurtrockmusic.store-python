
#!/bin/bash

# Hurtrock Music Store - Arch Linux Server Startup Script
# Script dengan penanganan error yang komprehensif untuk Arch Linux

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
APP_DIR="$(pwd)"
VENV_DIR="$APP_DIR/.venv"
ENV_FILE="$APP_DIR/.env"
LOG_FILE="$APP_DIR/hurtrock.log"
PID_FILE="$APP_DIR/app.pid"
DJANGO_PID_FILE="$APP_DIR/django.pid"
FLASK_PID_FILE="$APP_DIR/flask.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1${NC}"
}

# Error handler
error_exit() {
    log_error "$1"
    exit 1
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if port is available
check_port() {
    local port=$1
    if command_exists ss; then
        ! ss -tuln | grep ":$port " >/dev/null 2>&1
    elif command_exists netstat; then
        ! netstat -tuln | grep ":$port " >/dev/null 2>&1
    elif command_exists lsof; then
        ! lsof -Pi :$port -sTCP:LISTEN >/dev/null 2>&1
    else
        log_warning "Cannot check port $port availability (no ss/netstat/lsof)"
        return 0
    fi
}

# Kill process by PID file
kill_by_pid_file() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -TERM "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null || true
            sleep 2
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null || true
            fi
            log_success "$service_name stopped (PID: $pid)"
        else
            log_warning "$service_name PID file exists but process not running"
        fi
        rm -f "$pid_file"
    else
        log_info "No PID file found for $service_name"
    fi
}

# Setup Python virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    # Check if Python is available
    if ! command_exists python; then
        error_exit "Python not found. Please install Python 3.x"
    fi
    
    # Create venv if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        log_info "Creating virtual environment at $VENV_DIR"
        python -m venv "$VENV_DIR" || error_exit "Failed to create virtual environment"
        log_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate" || error_exit "Failed to activate virtual environment"
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel || log_warning "Failed to upgrade pip"
    
    # Install requirements
    if [ -f "$APP_DIR/requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        pip install -r "$APP_DIR/requirements.txt" || error_exit "Failed to install Python dependencies"
        log_success "Python dependencies installed"
    else
        log_warning "requirements.txt not found, skipping dependency installation"
    fi
    
    # Verify Django installation
    if ! python -c "import django" 2>/dev/null; then
        log_warning "Django not found, installing..."
        pip install django channels daphne django-cors-headers djangorestframework \
                   django-redis redis psycopg2-binary || error_exit "Failed to install Django"
        log_success "Django installed successfully"
    fi
    
    log_success "Virtual environment setup completed"
}

# Generate .env file
generate_env() {
    if [ -f "$ENV_FILE" ]; then
        log_info "Using existing .env file"
        return 0
    fi
    
    log_info "Generating .env configuration..."
    
    # Generate secure secrets
    if command_exists openssl; then
        SESSION_SECRET=$(openssl rand -hex 32)
        DJANGO_SECRET_KEY=$(openssl rand -hex 32)
        JWT_SECRET_KEY=$(openssl rand -hex 32)
    else
        # Fallback method using /dev/urandom
        SESSION_SECRET=$(head -c 32 /dev/urandom | base64 | tr -d "=+/" | cut -c1-64)
        DJANGO_SECRET_KEY=$(head -c 32 /dev/urandom | base64 | tr -d "=+/" | cut -c1-64)
        JWT_SECRET_KEY=$(head -c 32 /dev/urandom | base64 | tr -d "=+/" | cut -c1-64)
    fi
    
    # Database configuration
    DATABASE_URL="postgresql://fajar:fajar@localhost:5432/hurtrock_music_store"
    REDIS_URL="redis://localhost:6379/0"
    
    cat > "$ENV_FILE" <<EOF
# Hurtrock Music Store Configuration
# Auto-generated on $(date)

# Flask Configuration
SESSION_SECRET=$SESSION_SECRET
FLASK_APP=main.py
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
IS_PRODUCTION=false

# Database Configuration
DATABASE_URL=$DATABASE_URL

# Cache Configuration
REDIS_URL=$REDIS_URL
CACHE_URL=$REDIS_URL

# Django Configuration
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
DJANGO_DEBUG=True
DJANGO_HOST=0.0.0.0
DJANGO_PORT=8000

# JWT Configuration
JWT_SECRET_KEY=$JWT_SECRET_KEY

# Payment Configuration (Set these with your actual keys)
STRIPE_PUBLISHABLE_KEY=pk_test_placeholder
STRIPE_SECRET_KEY=sk_test_placeholder
MIDTRANS_SERVER_KEY=your_midtrans_server_key_here
MIDTRANS_CLIENT_KEY=your_midtrans_client_key_here

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_USE_TLS=True

# Domain Configuration
DOMAINS=localhost,127.0.0.1,0.0.0.0
EOF
    
    log_success ".env file generated at $ENV_FILE"
}

# Load environment variables
load_env() {
    if [ -f "$ENV_FILE" ]; then
        log_info "Loading environment variables..."
        set -a
        source "$ENV_FILE"
        set +a
        log_success "Environment variables loaded"
    else
        log_warning "No .env file found"
    fi
}

# Initialize database
init_database() {
    log_info "Initializing database..."
    
    # Check PostgreSQL connection
    if ! command_exists psql; then
        log_warning "PostgreSQL client not found, skipping database check"
        return 0
    fi
    
    # Test database connection
    if PGPASSWORD=fajar psql -h localhost -U fajar -d hurtrock_music_store -c "SELECT 1;" >/dev/null 2>&1; then
        log_success "Database connection successful"
    else
        log_warning "Database connection failed, but continuing..."
    fi
    
    # Run Flask database initialization
    log_info "Running Flask database setup..."
    python -c "
try:
    from main import app
    with app.app_context():
        from database import db
        db.create_all()
        print('Flask database tables created successfully')
except Exception as e:
    print(f'Flask database setup error: {e}')
    raise
" || log_warning "Flask database setup failed"
    
    log_success "Database initialization completed"
}

# Setup Django service
setup_django() {
    log_info "Setting up Django chat service..."
    
    # Check if chat_service directory exists
    if [ ! -d "$APP_DIR/chat_service" ]; then
        log_warning "chat_service directory not found, skipping Django setup"
        return 1
    fi
    
    cd "$APP_DIR/chat_service" || {
        log_error "Failed to enter chat_service directory"
        return 1
    }
    
    # Set Django environment
    export DJANGO_SETTINGS_MODULE=chat_microservice.settings
    
    # Check Django installation
    if ! python -c "import django" 2>/dev/null; then
        log_error "Django not installed in virtual environment"
        cd "$APP_DIR"
        return 1
    fi
    
    # Clean old migrations
    if [ -d "chat/migrations" ]; then
        find chat/migrations -name "*.py" ! -name "__init__.py" -delete 2>/dev/null || true
        log_info "Cleaned old migrations"
    fi
    
    # Create migrations
    log_info "Creating Django migrations..."
    if python manage.py makemigrations chat 2>/dev/null; then
        log_success "Django migrations created"
    else
        log_warning "Failed to create migrations, continuing..."
    fi
    
    # Apply migrations
    log_info "Applying Django migrations..."
    if python manage.py migrate --run-syncdb 2>/dev/null; then
        log_success "Django migrations applied"
    else
        log_warning "Migration failed, trying without --run-syncdb"
        python manage.py migrate 2>/dev/null || log_warning "Migration still failed"
    fi
    
    cd "$APP_DIR"
    log_success "Django setup completed"
    return 0
}

# Start Django service
start_django() {
    log_info "Starting Django chat service..."
    
    if ! check_port 8000; then
        log_warning "Port 8000 already in use, attempting to stop existing service..."
        kill_by_pid_file "$DJANGO_PID_FILE" "Django"
        sleep 2
        if ! check_port 8000; then
            log_error "Port 8000 still in use after cleanup"
            return 1
        fi
    fi
    
    if [ ! -d "$APP_DIR/chat_service" ]; then
        log_warning "Django chat service directory not found"
        return 1
    fi
    
    cd "$APP_DIR/chat_service" || return 1
    
    export DJANGO_SETTINGS_MODULE=chat_microservice.settings
    
    # Start Django service in background
    nohup python manage.py runserver 0.0.0.0:8000 --noreload > "$APP_DIR/django.log" 2>&1 &
    local django_pid=$!
    echo $django_pid > "$DJANGO_PID_FILE"
    
    cd "$APP_DIR"
    
    # Wait for Django to start
    sleep 3
    if ps -p $django_pid > /dev/null 2>&1; then
        log_success "Django chat service started (PID: $django_pid)"
        return 0
    else
        log_error "Django service failed to start"
        rm -f "$DJANGO_PID_FILE"
        return 1
    fi
}

# Start Flask service
start_flask() {
    log_info "Starting Flask main service..."
    
    if ! check_port 5000; then
        log_warning "Port 5000 already in use, attempting to stop existing service..."
        kill_by_pid_file "$FLASK_PID_FILE" "Flask"
        sleep 2
        if ! check_port 5000; then
            log_error "Port 5000 still in use after cleanup"
            return 1
        fi
    fi
    
    # Test Flask application
    if ! python -c "from main import app; print('Flask app loaded successfully')" 2>/dev/null; then
        log_error "Flask application failed to load"
        return 1
    fi
    
    # Start Flask service
    nohup python main.py > "$APP_DIR/flask.log" 2>&1 &
    local flask_pid=$!
    echo $flask_pid > "$FLASK_PID_FILE"
    
    # Wait for Flask to start
    sleep 3
    if ps -p $flask_pid > /dev/null 2>&1; then
        log_success "Flask main service started (PID: $flask_pid)"
        return 0
    else
        log_error "Flask service failed to start"
        rm -f "$FLASK_PID_FILE"
        return 1
    fi
}

# Stop all services
stop_services() {
    log_info "Stopping all services..."
    
    kill_by_pid_file "$FLASK_PID_FILE" "Flask"
    kill_by_pid_file "$DJANGO_PID_FILE" "Django"
    
    # Cleanup any remaining processes
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "manage.py runserver" 2>/dev/null || true
    
    log_success "All services stopped"
}

# Show service status
show_status() {
    echo ""
    log_info "=== Service Status ==="
    
    # Flask status
    if [ -f "$FLASK_PID_FILE" ]; then
        local flask_pid=$(cat "$FLASK_PID_FILE")
        if ps -p "$flask_pid" > /dev/null 2>&1; then
            log_success "Flask Main Service: Running (PID: $flask_pid, Port: 5000)"
        else
            log_warning "Flask Main Service: Not running (stale PID file)"
            rm -f "$FLASK_PID_FILE"
        fi
    else
        log_warning "Flask Main Service: Not running"
    fi
    
    # Django status
    if [ -f "$DJANGO_PID_FILE" ]; then
        local django_pid=$(cat "$DJANGO_PID_FILE")
        if ps -p "$django_pid" > /dev/null 2>&1; then
            log_success "Django Chat Service: Running (PID: $django_pid, Port: 8000)"
        else
            log_warning "Django Chat Service: Not running (stale PID file)"
            rm -f "$DJANGO_PID_FILE"
        fi
    else
        log_warning "Django Chat Service: Not running"
    fi
    
    echo ""
    log_info "=== Access URLs ==="
    echo "  Main Store: http://0.0.0.0:5000"
    echo "  Admin Panel: http://0.0.0.0:5000/admin"
    echo "  Chat API: http://0.0.0.0:8000"
    echo ""
    log_info "=== Default Admin Login ==="
    echo "  Email: admin@hurtrock.com"
    echo "  Password: admin123"
    echo ""
}

# Show logs
show_logs() {
    log_info "Showing service logs (press Ctrl+C to exit)..."
    
    if [ -f "$APP_DIR/flask.log" ] && [ -f "$APP_DIR/django.log" ]; then
        tail -f "$APP_DIR/flask.log" "$APP_DIR/django.log"
    elif [ -f "$APP_DIR/flask.log" ]; then
        tail -f "$APP_DIR/flask.log"
    elif [ -f "$APP_DIR/django.log" ]; then
        tail -f "$APP_DIR/django.log"
    else
        log_warning "No log files found"
    fi
}

# Load sample data
load_sample_data() {
    log_info "Loading sample data..."
    
    if [ -f "$APP_DIR/sample_data.py" ]; then
        python "$APP_DIR/sample_data.py" || {
            log_error "Failed to load sample data"
            return 1
        }
        log_success "Sample data loaded successfully"
    else
        log_warning "sample_data.py not found"
    fi
}

# Main execution
main() {
    case "${1:-start}" in
        start)
            log_info "=== Starting Hurtrock Music Store ==="
            
            # Setup environment
            setup_venv
            generate_env
            load_env
            
            # Initialize database
            init_database
            
            # Setup services
            if setup_django; then
                log_success "Django setup completed"
            else
                log_warning "Django setup failed, continuing without chat service"
            fi
            
            # Start services
            local django_started=false
            local flask_started=false
            
            if start_django; then
                django_started=true
            else
                log_warning "Django service failed to start, continuing..."
            fi
            
            if start_flask; then
                flask_started=true
            else
                log_error "Flask service failed to start"
                stop_services
                exit 1
            fi
            
            if $flask_started; then
                log_success "=== Hurtrock Music Store Started Successfully ==="
                show_status
            else
                log_error "=== Failed to Start Services ==="
                exit 1
            fi
            ;;
            
        stop)
            stop_services
            ;;
            
        restart)
            log_info "=== Restarting Services ==="
            stop_services
            sleep 3
            main start
            ;;
            
        status)
            show_status
            ;;
            
        logs)
            show_logs
            ;;
            
        sample-data)
            setup_venv
            load_env
            load_sample_data
            ;;
            
        setup)
            log_info "=== Setting up Environment ==="
            setup_venv
            generate_env
            load_env
            init_database
            setup_django
            log_success "=== Environment Setup Completed ==="
            ;;
            
        *)
            echo "Hurtrock Music Store - Arch Linux Server Script"
            echo ""
            echo "Usage: $0 {start|stop|restart|status|logs|sample-data|setup}"
            echo ""
            echo "Commands:"
            echo "  start       - Start all services (default)"
            echo "  stop        - Stop all services"
            echo "  restart     - Restart all services"
            echo "  status      - Show service status"
            echo "  logs        - Show live logs"
            echo "  sample-data - Load sample data"
            echo "  setup       - Setup environment only"
            echo ""
            echo "Examples:"
            echo "  $0 start       # Start the music store"
            echo "  $0 status      # Check if services are running"
            echo "  $0 logs        # View service logs"
            echo ""
            exit 1
            ;;
    esac
}

# Handle signals for graceful shutdown
trap 'echo ""; log_info "Received interrupt signal, stopping services..."; stop_services; exit 0' INT TERM

# Run main function with all arguments
main "$@"
