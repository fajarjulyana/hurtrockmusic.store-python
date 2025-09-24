#!/bin/bash

# Hurtrock Music Store - Universal Server Management Script
# Script utama untuk semua environment - Linux, macOS, Windows (WSL), Replit
# Menggantikan semua script startup lainnya dengan fitur lengkap

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/.venv"
ENV_FILE="$APP_DIR/.env"
LOG_FILE="$APP_DIR/hurtrock.log"
PID_FILE="$APP_DIR/app.pid"
DJANGO_PID_FILE="$APP_DIR/django.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- Fungsi logging ---
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✓ $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠ $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ✗ $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"
}

# Function to detect Python command
detect_python() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        # Check if it's Python 3
        if python --version 2>&1 | grep -q "Python 3"; then
            echo "python"
        else
            return 1
        fi
    else
        return 1
    fi
}

# Function to check if port is available
check_port() {
    local port=$1
    if command -v ss >/dev/null 2>&1; then
        ! ss -tuln | grep -q ":$port "
    elif command -v netstat >/dev/null 2>&1; then
        ! netstat -tuln 2>/dev/null | grep -q ":$port "
    elif command -v lsof >/dev/null 2>&1; then
        ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1
    else
        # Fallback: try to bind to port
        python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(('0.0.0.0', $port))
    s.close()
    exit(0)
except:
    exit(1)
" 2>/dev/null
    fi
}

# Function to generate secure secret
generate_secret() {
    if command -v openssl >/dev/null 2>&1; then
        openssl rand -hex 32
    else
        python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || \
        python -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || \
        echo "hurtrock_music_store_$(date +%s)_$(shuf -i 1000-9999 -n 1)"
    fi
}

# Function to stop existing services
stop_services() {
    log "Stopping existing services..."

    # Stop Flask
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            sleep 2
            kill -9 "$pid" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi

    # Stop Django
    if [ -f "$DJANGO_PID_FILE" ]; then
        local pid=$(cat "$DJANGO_PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            sleep 2
            kill -9 "$pid" 2>/dev/null || true
        fi
        rm -f "$DJANGO_PID_FILE"
    fi

    # Kill by process name as fallback
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "manage.py.*runserver" 2>/dev/null || true

    # Wait for ports to be free
    local count=0
    while ! check_port 5000 && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done

    count=0
    while ! check_port 8000 && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done
}

# --- Setup environment ---
setup_environment() {
    log "Setting up environment..."

    # Detect Python
    PYTHON_CMD=$(detect_python)
    if [ -z "$PYTHON_CMD" ]; then
        log_error "Python 3 not found! Please install Python 3.x"
        exit 1
    fi
    log_success "Using Python command: $PYTHON_CMD"

    # Create virtual environment if not exists
    if [ ! -d "$VENV_DIR" ]; then
        log "Creating virtual environment..."
        $PYTHON_CMD -m venv "$VENV_DIR" || {
            log_error "Failed to create virtual environment"
            exit 1
        }
    fi

    # Activate virtual environment
    source "$VENV_DIR/bin/activate" || {
        log_error "Failed to activate virtual environment"
        exit 1
    }

    # Update pip
    pip install --upgrade pip >/dev/null 2>&1 || true

    # Install requirements
    if [ -f "requirements.txt" ]; then
        log "Installing Python dependencies..."
        pip install -r requirements.txt --no-cache-dir >/dev/null 2>&1 || {
            log_warning "Some dependencies failed to install, continuing..."
        }
    fi

    log_success "Environment setup completed"
}

# --- Generate .env if not exists ---
setup_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        log "Generating .env file..."

        SESSION_SECRET=$(generate_secret)
        DJANGO_SECRET_KEY=$(generate_secret)
        JWT_SECRET_KEY=$(generate_secret)

        # Detect database
        if command -v psql >/dev/null 2>&1; then
            DATABASE_URL="postgresql://postgres@localhost:5432/hurtrock_music_store"
        else
            DATABASE_URL="sqlite:///$(pwd)/hurtrock.db"
        fi

        cat > "$ENV_FILE" << EOF
# Database Configuration
DATABASE_URL='$DATABASE_URL'

# Security Keys
SESSION_SECRET='$SESSION_SECRET'
DJANGO_SECRET_KEY='$DJANGO_SECRET_KEY'
JWT_SECRET_KEY='$JWT_SECRET_KEY'

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
IS_PRODUCTION=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Django Configuration
DJANGO_HOST=0.0.0.0
DJANGO_PORT=8000
DJANGO_DEBUG=0

# Cache Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# Payment Configuration (set your actual keys)
STRIPE_PUBLISHABLE_KEY=pk_test_placeholder
STRIPE_SECRET_KEY=sk_test_placeholder
MIDTRANS_SERVER_KEY=midtrans_server_key_placeholder
MIDTRANS_CLIENT_KEY=midtrans_client_key_placeholder

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True

# Domain Configuration (remove Replit dependency)
DOMAINS=localhost,127.0.0.1,0.0.0.0
EOF

        log_success ".env file generated"
    else
        log_success ".env file already exists"
    fi

    # Load environment variables
    set -a
    source "$ENV_FILE"
    set +a
}

# --- Database setup ---
setup_database() {
    log "Setting up database..."

    # Try to create database if PostgreSQL is available
    if command -v psql >/dev/null 2>&1; then
        createdb hurtrock_music_store 2>/dev/null || true
    fi

    # Initialize Flask database
    $PYTHON_CMD -c "
import sys
sys.path.append('.')
try:
    from main import app
    print('[OK] Flask app initialized and database setup completed')
except Exception as e:
    print(f'[ERROR] Flask initialization error: {e}')
    sys.exit(1)
" || {
        log_error "Failed to initialize Flask database"
        exit 1
    }

    # Setup Django migrations
    if [ -d "chat_service" ]; then
        cd chat_service
        export DJANGO_SETTINGS_MODULE=chat_microservice.settings

        log "Running Django migrations..."
        $PYTHON_CMD manage.py makemigrations chat >/dev/null 2>&1 || true
        $PYTHON_CMD manage.py migrate >/dev/null 2>&1 || true

        cd ..
    fi

    log_success "Database setup completed"
}

# --- Start Django service ---
start_django() {
    if ! check_port 8000; then
        log_warning "Port 8000 already in use, skipping Django start"
        return 0
    fi

    log "Starting Django chat service on port 8000..."

    cd chat_service
    export DJANGO_SETTINGS_MODULE=chat_microservice.settings

    nohup $PYTHON_CMD manage.py runserver 0.0.0.0:8000 --noreload >/dev/null 2>&1 &
    DJANGO_PID=$!
    echo $DJANGO_PID > "../$DJANGO_PID_FILE"

    cd ..

    # Wait for Django to start
    local count=0
    while ! curl -s http://127.0.0.1:8000/health/ >/dev/null 2>&1 && [ $count -lt 30 ]; do
        sleep 1
        count=$((count + 1))
    done

    if curl -s http://127.0.0.1:8000/health/ >/dev/null 2>&1; then
        log_success "Django service started successfully"
        return 0
    else
        log_warning "Django service may not be fully ready"
        return 1
    fi
}

# --- Start Flask service ---
start_flask() {
    if ! check_port 5000; then
        log_error "Port 5000 already in use!"
        return 1
    fi

    log "Starting Flask main service on port 5000..."

    # Start Flask
    nohup $PYTHON_CMD main.py >/dev/null 2>&1 &
    FLASK_PID=$!
    echo $FLASK_PID > "$PID_FILE"

    # Wait for Flask to start
    local count=0
    while ! curl -s http://127.0.0.1:5000/ >/dev/null 2>&1 && [ $count -lt 30 ]; do
        sleep 1
        count=$((count + 1))
    done

    if curl -s http://127.0.0.1:5000/ >/dev/null 2>&1; then
        log_success "Flask service started successfully"
        return 0
    else
        log_error "Flask service failed to start"
        return 1
    fi
}

# --- Show status ---
show_status() {
    echo ""
    echo "=============================================="
    echo "   🎸 HURTROCK MUSIC STORE STATUS 🎸"
    echo "=============================================="
    echo ""

    # Check Flask
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        log_success "Flask Server: Running (PID: $(cat "$PID_FILE"))"
        echo "   📱 Main Website: http://0.0.0.0:5000"
        echo "   👨‍💼 Admin Panel: http://0.0.0.0:5000/admin"
    else
        log_error "Flask Server: Not running"
    fi

    # Check Django
    if [ -f "$DJANGO_PID_FILE" ] && kill -0 "$(cat "$DJANGO_PID_FILE")" 2>/dev/null; then
        log_success "Django Chat Service: Running (PID: $(cat "$DJANGO_PID_FILE"))"
        echo "   💬 Chat API: http://0.0.0.0:8000"
        echo "   💬 Admin Chat: http://0.0.0.0:5000/admin/chat"
    else
        log_warning "Django Chat Service: Not running"
    fi

    echo ""
    echo "🔑 Default Admin Login:"
    echo "   Email: admin@hurtrock.com"
    echo "   Password: admin123"
    echo ""
    echo "📂 Configuration Files:"
    echo "   Environment: $ENV_FILE"
    echo "   Logs: $LOG_FILE"
    echo ""
    echo "⚡ Management Commands:"
    echo "   $0 start    # Start services"
    echo "   $0 stop     # Stop services"
    echo "   $0 restart  # Restart services"
    echo "   $0 status   # Show status"
    echo "   $0 logs     # Show logs"
    echo ""
    echo "=============================================="
}

# --- Signal handler ---
cleanup() {
    echo ""
    log "Received shutdown signal, stopping services..."
    stop_services
    exit 0
}

# Setup signal handlers
trap cleanup SIGINT SIGTERM

# Function to detect environment
detect_environment() {
    if [[ -n "$REPL_ID" ]] || [[ -n "$REPLIT_ENVIRONMENT" ]]; then
        echo "replit"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -f "/etc/arch-release" ]] || [[ -f "/etc/manjaro-release" ]]; then
            echo "arch"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ -n "$WSL_DISTRO_NAME" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to show help
show_help() {
    echo ""
    echo "🎸 Hurtrock Music Store - Universal Server Manager"
    echo "=================================================="
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start         Start all services (default)"
    echo "  stop          Stop all services"
    echo "  restart       Restart all services"
    echo "  status        Show service status"
    echo "  logs          Show live logs"
    echo "  gui           Start GUI server manager"
    echo "  cli           Start CLI server manager"
    echo "  install       Install dependencies"
    echo "  help          Show this help"
    echo ""
    echo "Options:"
    echo "  --gui         Force GUI mode"
    echo "  --cli         Force CLI mode"
    echo "  --no-deps     Skip dependency installation"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start servers in CLI mode"
    echo "  $0 gui                # Start GUI manager"
    echo "  $0 start --gui        # Start servers with GUI"
    echo "  $0 install            # Install dependencies only"
    echo ""
}

# Function to install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    ENVIRONMENT=$(detect_environment)
    log "Environment detected: $ENVIRONMENT"
    
    # Python dependencies
    if [ -f "requirements.txt" ]; then
        log "Installing Python dependencies..."
        $PYTHON_CMD -m pip install --user -r requirements.txt --no-cache-dir || {
            log_warning "Some Python dependencies failed to install, continuing..."
        }
    fi
    
    # Environment-specific dependencies
    case $ENVIRONMENT in
        "replit")
            log "Replit environment - dependencies managed automatically"
            ;;
        "arch"|"manjaro")
            if command -v pacman >/dev/null 2>&1; then
                log "Installing Arch Linux dependencies..."
                sudo pacman -S --noconfirm --needed python python-pip postgresql redis git curl wget || {
                    log_warning "Some system packages failed to install"
                }
            fi
            ;;
        "linux")
            if command -v apt >/dev/null 2>&1; then
                log "Installing Ubuntu/Debian dependencies..."
                sudo apt update && sudo apt install -y python3 python3-pip postgresql redis-server git curl wget || {
                    log_warning "Some system packages failed to install"
                }
            elif command -v dnf >/dev/null 2>&1; then
                log "Installing Fedora dependencies..."
                sudo dnf install -y python3 python3-pip postgresql redis git curl wget || {
                    log_warning "Some system packages failed to install"
                }
            fi
            ;;
        "macos")
            if command -v brew >/dev/null 2>&1; then
                log "Installing macOS dependencies..."
                brew install python postgresql redis git curl wget || {
                    log_warning "Some packages failed to install"
                }
            fi
            ;;
    esac
    
    log_success "Dependencies installation completed"
}

# Function to choose server mode
choose_server_mode() {
    local force_mode="$1"
    
    if [[ "$force_mode" == "--gui" ]] || [[ "$force_mode" == "gui" ]]; then
        return 0  # GUI mode
    elif [[ "$force_mode" == "--cli" ]] || [[ "$force_mode" == "cli" ]]; then
        return 1  # CLI mode
    fi
    
    # Auto-detect best mode
    ENVIRONMENT=$(detect_environment)
    
    if [[ "$ENVIRONMENT" == "replit" ]]; then
        # Replit environment - prefer CLI
        return 1
    elif command -v python3 >/dev/null 2>&1; then
        # Check if tkinter is available
        if python3 -c "import tkinter" >/dev/null 2>&1; then
            # GUI available, ask user
            echo ""
            echo "🎸 Hurtrock Music Store - Server Manager"
            echo "========================================"
            echo ""
            echo "Pilih mode server manager:"
            echo "1) GUI Mode (Graphic Interface)"
            echo "2) CLI Mode (Command Line)"
            echo ""
            read -p "Pilihan (1/2) [default: 2]: " choice
            
            case $choice in
                1) return 0 ;;  # GUI mode
                *) return 1 ;;  # CLI mode (default)
            esac
        else
            return 1  # CLI mode (no GUI available)
        fi
    else
        return 1  # CLI mode (fallback)
    fi
}

# Function to start GUI manager
start_gui_manager() {
    log "Starting GUI Server Manager..."
    
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "Python3 not found! Please install Python first."
        return 1
    fi
    
    if ! python3 -c "import tkinter" >/dev/null 2>&1; then
        log_error "Tkinter not available! GUI mode not supported."
        log "Falling back to CLI mode..."
        start_cli_manager
        return $?
    fi
    
    if [ ! -f "server_gui.py" ]; then
        log_error "server_gui.py not found!"
        return 1
    fi
    
    # Setup environment first
    setup_environment
    setup_env_file
    
    log_success "Starting GUI Server Manager..."
    exec $PYTHON_CMD server_gui.py
}

# Function to start CLI manager  
start_cli_manager() {
    log "Starting CLI Server Manager..."
    
    if [ ! -f "server.py" ]; then
        log_error "server.py not found!"
        return 1
    fi
    
    # Setup environment first
    setup_environment
    setup_env_file
    setup_database
    
    log_success "Starting CLI Server Manager..."
    exec $PYTHON_CMD server.py
}

# --- Main execution ---
case "${1:-start}" in
    "start")
        # Check for mode options
        MODE_OPTION="$2"
        
        if [[ "$MODE_OPTION" == "--no-deps" ]]; then
            log "Skipping dependency installation as requested"
        else
            install_dependencies
        fi
        
        if choose_server_mode "$MODE_OPTION"; then
            start_gui_manager
        else
            start_cli_manager
        fi
        ;;

    "gui")
        install_dependencies
        start_gui_manager
        ;;

    "cli")
        install_dependencies  
        start_cli_manager
        ;;

    "install")
        install_dependencies
        log_success "Dependencies installed successfully!"
        ;;

    "help"|"--help"|"-h")
        show_help
        ;;

    "legacy-start")
        log "🎸 Starting Hurtrock Music Store (Legacy Mode)..."

        # Stop any existing services
        stop_services

        # Setup environment
        setup_environment
        setup_env_file
        setup_database

        # Start services
        start_django || log_warning "Django service failed to start, continuing with Flask only"
        sleep 2

        if start_flask; then
            log_success "🎵 All services started successfully!"
            show_status

            # Keep running
            log "Press Ctrl+C to stop all services..."
            while true; do
                # Check if services are still running
                if [ -f "$PID_FILE" ] && ! kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
                    log_error "Flask service stopped unexpectedly"
                    break
                fi
                sleep 10
            done
        else
            log_error "Failed to start Flask service"
            stop_services
            exit 1
        fi
        ;;

    "stop")
        stop_services
        log_success "All services stopped"
        ;;

    "restart")
        log "Restarting services..."
        stop_services
        sleep 2
        exec "$0" start
        ;;

    "status")
        show_status
        ;;

    "logs")
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            log_warning "No log file found"
        fi
        ;;

    *)
        echo "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac