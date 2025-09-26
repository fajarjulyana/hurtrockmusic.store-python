
#!/bin/bash

# Hurtrock Music Store - Enhanced Universal Linux Server Startup Script
# Compatible with Ubuntu, Debian, CentOS, RHEL, Fedora, openSUSE, and other Linux distributions
# Complete setup with manual .env configuration and PostgreSQL database support

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
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# --- Logging Functions ---
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

log_info() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')] ℹ $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" >> "$LOG_FILE"
}

# --- System Detection Functions ---
detect_linux_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/redhat-release ]; then
        echo "rhel"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    else
        echo "unknown"
    fi
}

detect_python() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        if python --version 2>&1 | grep -q "Python 3"; then
            echo "python"
        else
            log_error "Python 2 detected. Python 3 is required!"
            return 1
        fi
    else
        log_error "Python not found. Please install Python 3.x"
        return 1
    fi
}

# Function to detect Python command
detect_python_cmd() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        if python --version 2>&1 | grep -q "Python 3"; then
            echo "python"
        else
            return 1
        fi
    else
        return 1
    fi
}

# --- Port Management ---
check_port() {
    local port=$1
    if command -v ss >/dev/null 2>&1; then
        ! ss -tuln | grep -q ":$port "
    elif command -v netstat >/dev/null 2>&1; then
        ! netstat -tuln 2>/dev/null | grep -q ":$port "
    elif command -v lsof >/dev/null 2>&1; then
        ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1
    else
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

kill_port() {
    local port=$1
    log "Killing processes on port $port..."
    
    if command -v fuser >/dev/null 2>&1; then
        fuser -k $port/tcp 2>/dev/null || true
    fi
    
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
    
    sleep 2
}

# --- Security Functions ---
generate_secret() {
    if command -v openssl >/dev/null 2>&1; then
        openssl rand -base64 32
    elif command -v python3 >/dev/null 2>&1; then
        python3 -c "import secrets; print(secrets.token_urlsafe(32))"
    else
        echo "hurtrock_$(date +%s)_$(shuf -i 1000-9999 -n 1 2>/dev/null || echo $RANDOM)"
    fi
}

# --- PostgreSQL Setup Functions ---
setup_postgresql() {
    local distro=$(detect_linux_distro)
    log "Setting up PostgreSQL for $distro..."

    case $distro in
        "ubuntu"|"debian")
            if ! command -v psql >/dev/null 2>&1; then
                log "Installing PostgreSQL..."
                sudo apt update
                sudo apt install -y postgresql postgresql-contrib python3-psycopg2
            fi
            sudo systemctl enable postgresql
            sudo systemctl start postgresql
            ;;
        "fedora"|"rhel"|"centos"|"rocky"|"almalinux")
            if ! command -v psql >/dev/null 2>&1; then
                log "Installing PostgreSQL..."
                if command -v dnf >/dev/null 2>&1; then
                    sudo dnf install -y postgresql postgresql-server postgresql-contrib python3-psycopg2
                else
                    sudo yum install -y postgresql postgresql-server postgresql-contrib python3-psycopg2
                fi
                sudo postgresql-setup --initdb 2>/dev/null || sudo postgresql-setup initdb 2>/dev/null || true
            fi
            sudo systemctl enable postgresql
            sudo systemctl start postgresql
            ;;
        "opensuse"|"sles")
            if ! command -v psql >/dev/null 2>&1; then
                log "Installing PostgreSQL..."
                sudo zypper install -y postgresql postgresql-server postgresql-contrib python3-psycopg2
            fi
            sudo systemctl enable postgresql
            sudo systemctl start postgresql
            ;;
        *)
            log_warning "Unknown distribution. Please install PostgreSQL manually."
            ;;
    esac

    # Create database user and database
    if command -v psql >/dev/null 2>&1; then
        log "Setting up PostgreSQL database..."
        
        # Create user
        sudo -u postgres createuser -s $USER 2>/dev/null || true
        sudo -u postgres psql -c "ALTER USER $USER WITH PASSWORD '$USER';" 2>/dev/null || true
        
        # Create database
        sudo -u postgres createdb hurtrock_music_store -O $USER 2>/dev/null || true
        
        log_success "PostgreSQL setup completed"
        return 0
    else
        log_error "PostgreSQL installation failed"
        return 1
    fi
}

# --- Environment Setup ---
setup_environment() {
    log "Setting up Python environment..."

    # Detect Python
    PYTHON_CMD=$(detect_python_cmd)
    if [ -z "$PYTHON_CMD" ]; then
        log_error "Python 3 not found! Please install Python 3.x"
        exit 1
    fi
    log_success "Using Python command: $PYTHON_CMD"

    # Install pip if not available
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        log "Installing pip..."
        curl -s https://bootstrap.pypa.io/get-pip.py | $PYTHON_CMD
    fi

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
        pip install -r requirements.txt --no-cache-dir || {
            log_warning "Some dependencies failed to install, continuing..."
        }
    fi

    log_success "Environment setup completed"
}

# --- .env Configuration ---
interactive_database_setup() {
    echo ""
    echo "🗄️  Database Configuration"
    echo "========================="
    echo ""
    echo "Choose database type:"
    echo "1) PostgreSQL (Recommended for production)"
    echo "2) SQLite (Simple, file-based)"
    echo ""
    read -p "Enter choice (1-2) [default: 1]: " db_choice

    case $db_choice in
        2)
            DATABASE_URL="sqlite:///$(pwd)/hurtrock.db"
            log_info "Using SQLite database"
            ;;
        *)
            # PostgreSQL setup
            echo ""
            echo "PostgreSQL Configuration:"
            read -p "Database host [localhost]: " db_host
            db_host=${db_host:-localhost}
            
            read -p "Database port [5432]: " db_port
            db_port=${db_port:-5432}
            
            read -p "Database name [hurtrock_music_store]: " db_name
            db_name=${db_name:-hurtrock_music_store}
            
            read -p "Database user [$USER]: " db_user
            db_user=${db_user:-$USER}
            
            read -s -p "Database password [$USER]: " db_password
            db_password=${db_password:-$USER}
            echo ""
            
            DATABASE_URL="postgresql://$db_user:$db_password@$db_host:$db_port/$db_name"
            log_info "Using PostgreSQL database: $db_host:$db_port/$db_name"
            ;;
    esac
}

interactive_server_setup() {
    echo ""
    echo "🌐 Server Configuration"
    echo "======================"
    read -p "Flask host [0.0.0.0]: " flask_host
    flask_host=${flask_host:-0.0.0.0}
    
    read -p "Flask port [5000]: " flask_port
    flask_port=${flask_port:-5000}
    
    read -p "Django port [8000]: " django_port
    django_port=${django_port:-8000}
    
    # Environment type
    echo ""
    echo "Environment type:"
    echo "1) Development (Debug enabled)"
    echo "2) Production (Debug disabled)"
    read -p "Choose (1-2) [default: 1]: " env_type
    
    if [ "$env_type" = "2" ]; then
        FLASK_ENV="production"
        FLASK_DEBUG="0"
        IS_PRODUCTION="true"
        DJANGO_DEBUG="0"
    else
        FLASK_ENV="development"
        FLASK_DEBUG="1"
        IS_PRODUCTION="false"
        DJANGO_DEBUG="1"
    fi
}

interactive_payment_setup() {
    echo ""
    echo "💳 Payment Configuration"
    echo "========================"
    echo "Configure payment gateways (you can skip and configure later in admin panel):"
    echo ""
    
    # Stripe
    echo "Stripe Configuration:"
    read -p "Stripe Publishable Key (optional): " stripe_pub_key
    read -p "Stripe Secret Key (optional): " stripe_secret_key
    
    echo ""
    # Midtrans
    echo "Midtrans Configuration:"
    read -p "Midtrans Client Key (optional): " midtrans_client_key
    read -p "Midtrans Server Key (optional): " midtrans_server_key
    
    # Set defaults if empty
    stripe_pub_key=${stripe_pub_key:-pk_test_your_stripe_publishable_key_here}
    stripe_secret_key=${stripe_secret_key:-sk_test_your_stripe_secret_key_here}
    midtrans_client_key=${midtrans_client_key:-your_midtrans_client_key_here}
    midtrans_server_key=${midtrans_server_key:-your_midtrans_server_key_here}
}

interactive_contact_setup() {
    echo ""
    echo "📞 Contact Information"
    echo "====================="
    read -p "Store Email [info@hurtrock.com]: " store_email
    store_email=${store_email:-info@hurtrock.com}
    
    read -p "WhatsApp Number (e.g., 6282115558035): " whatsapp_number
    whatsapp_number=${whatsapp_number:-6282115558035}
    
    read -p "Store Phone [0821-1555-8035]: " store_phone
    store_phone=${store_phone:-0821-1555-8035}
}

setup_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        log "Creating .env configuration..."
        
        # Interactive setup
        interactive_database_setup
        interactive_server_setup
        interactive_payment_setup
        interactive_contact_setup
        
        # Generate secrets
        log "Generating security keys..."
        SESSION_SECRET=$(generate_secret)
        DJANGO_SECRET_KEY=$(generate_secret)
        JWT_SECRET_KEY=$(generate_secret)

        # Create .env file
        cat > "$ENV_FILE" << EOF
# Hurtrock Music Store Configuration
# Generated on $(date)

# Database Configuration
DATABASE_URL='$DATABASE_URL'

# Security Keys (Keep these secret!)
SESSION_SECRET='$SESSION_SECRET'
DJANGO_SECRET_KEY='$DJANGO_SECRET_KEY'
JWT_SECRET_KEY='$JWT_SECRET_KEY'

# Flask Configuration
FLASK_ENV=$FLASK_ENV
FLASK_DEBUG=$FLASK_DEBUG
IS_PRODUCTION=$IS_PRODUCTION
FLASK_HOST=$flask_host
FLASK_PORT=$flask_port

# Django Configuration
DJANGO_HOST=$flask_host
DJANGO_PORT=$django_port
DJANGO_DEBUG=$DJANGO_DEBUG

# Cache Configuration (Redis - optional)
REDIS_URL=redis://localhost:6379/0

# Payment Configuration
STRIPE_PUBLISHABLE_KEY=$stripe_pub_key
STRIPE_SECRET_KEY=$stripe_secret_key
MIDTRANS_SERVER_KEY=$midtrans_server_key
MIDTRANS_CLIENT_KEY=$midtrans_client_key

# Email Configuration (SMTP - optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=$store_email
MAIL_PASSWORD=your_app_password

# Domain Configuration
DOMAINS=localhost,127.0.0.1,0.0.0.0,$flask_host

# Contact Information
STORE_EMAIL=$store_email
WHATSAPP_NUMBER=$whatsapp_number
STORE_PHONE=$store_phone

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=static/public/produk_images

# Session Configuration
PERMANENT_SESSION_LIFETIME=86400
SESSION_COOKIE_SECURE=$IS_PRODUCTION
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
EOF

        log_success ".env file created successfully!"
        echo ""
        echo "📝 Configuration saved to: $ENV_FILE"
        echo "⚠️  Important: Update payment keys in .env file before production use!"
        echo ""
    else
        log_success ".env file already exists"
    fi

    # Load environment variables
    set -a
    source "$ENV_FILE"
    set +a
}

# --- Database Initialization ---
setup_database() {
    log "Initializing database..."

    # Load environment
    if [ -f "$ENV_FILE" ]; then
        set -a
        source "$ENV_FILE"
        set +a
    fi

    # Try to create PostgreSQL database if using PostgreSQL
    if [[ "$DATABASE_URL" == postgresql* ]]; then
        # Extract database name from URL
        DB_NAME=$(echo "$DATABASE_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
        if [ -n "$DB_NAME" ] && command -v createdb >/dev/null 2>&1; then
            createdb "$DB_NAME" 2>/dev/null || true
        fi
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

    # Setup Django migrations if chat service exists
    if [ -d "chat_service" ]; then
        cd chat_service
        export DJANGO_SETTINGS_MODULE=chat_microservice.settings

        log "Running Django migrations..."
        $PYTHON_CMD manage.py makemigrations chat >/dev/null 2>&1 || true
        $PYTHON_CMD manage.py migrate >/dev/null 2>&1 || true

        cd ..
    fi

    log_success "Database initialization completed"
}

# --- Sample Data Setup ---
setup_sample_data() {
    echo ""
    echo "📊 Sample Data Setup"
    echo "==================="
    echo "Would you like to create sample data for testing?"
    echo "This will add sample products, categories, and users to your database."
    echo ""
    read -p "Create sample data? (y/N): " create_sample

    if [[ $create_sample =~ ^[Yy]$ ]]; then
        log "Creating sample data..."
        if [ -f "sample_data.py" ]; then
            $PYTHON_CMD sample_data.py || {
                log_warning "Sample data creation failed, continuing..."
            }
            log_success "Sample data created successfully!"
        else
            log_warning "sample_data.py not found, skipping sample data creation"
        fi
    else
        log_info "Skipping sample data creation"
    fi
}

# --- Service Management ---
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

    # Kill by process name and port
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "manage.py.*runserver" 2>/dev/null || true
    kill_port 5000
    kill_port 8000

    log_success "Services stopped"
}

start_django() {
    local django_port=${DJANGO_PORT:-8000}
    
    if ! check_port $django_port; then
        log_warning "Port $django_port already in use, skipping Django start"
        return 0
    fi

    if [ ! -d "chat_service" ]; then
        log_warning "Django chat service not found, skipping"
        return 0
    fi

    log "Starting Django chat service on port $django_port..."

    cd chat_service
    export DJANGO_SETTINGS_MODULE=chat_microservice.settings

    nohup $PYTHON_CMD manage.py runserver 0.0.0.0:$django_port --noreload >/dev/null 2>&1 &
    DJANGO_PID=$!
    echo $DJANGO_PID > "../$DJANGO_PID_FILE"

    cd ..

    # Wait for Django to start
    local count=0
    while ! curl -s http://127.0.0.1:$django_port/health/ >/dev/null 2>&1 && [ $count -lt 30 ]; do
        sleep 1
        count=$((count + 1))
    done

    if curl -s http://127.0.0.1:$django_port/health/ >/dev/null 2>&1; then
        log_success "Django service started successfully"
        return 0
    else
        log_warning "Django service may not be fully ready"
        return 1
    fi
}

start_flask() {
    local flask_port=${FLASK_PORT:-5000}
    local flask_host=${FLASK_HOST:-0.0.0.0}
    
    if ! check_port $flask_port; then
        log_error "Port $flask_port already in use!"
        kill_port $flask_port
        sleep 2
        if ! check_port $flask_port; then
            log_error "Failed to free port $flask_port"
            return 1
        fi
    fi

    log "Starting Flask main service on $flask_host:$flask_port..."

    # Start Flask
    nohup $PYTHON_CMD main.py >/dev/null 2>&1 &
    FLASK_PID=$!
    echo $FLASK_PID > "$PID_FILE"

    # Wait for Flask to start
    local count=0
    while ! curl -s http://127.0.0.1:$flask_port/ >/dev/null 2>&1 && [ $count -lt 30 ]; do
        sleep 1
        count=$((count + 1))
    done

    if curl -s http://127.0.0.1:$flask_port/ >/dev/null 2>&1; then
        log_success "Flask service started successfully"
        return 0
    else
        log_error "Flask service failed to start"
        return 1
    fi
}

# --- System Dependencies ---
install_system_dependencies() {
    local distro=$(detect_linux_distro)
    log "Installing system dependencies for $distro..."

    case $distro in
        "ubuntu"|"debian")
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv python3-dev \
                               curl wget git build-essential \
                               postgresql postgresql-contrib python3-psycopg2 \
                               redis-server \
                               libffi-dev libssl-dev \
                               pkg-config
            ;;
        "fedora"|"rhel"|"centos"|"rocky"|"almalinux")
            if command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y python3 python3-pip python3-devel \
                                   curl wget git gcc gcc-c++ make \
                                   postgresql postgresql-server postgresql-contrib python3-psycopg2 \
                                   redis \
                                   libffi-devel openssl-devel \
                                   pkgconfig
            else
                sudo yum install -y python3 python3-pip python3-devel \
                                   curl wget git gcc gcc-c++ make \
                                   postgresql postgresql-server postgresql-contrib python3-psycopg2 \
                                   redis \
                                   libffi-devel openssl-devel \
                                   pkgconfig
            fi
            ;;
        "opensuse"|"sles")
            sudo zypper install -y python3 python3-pip python3-devel \
                                  curl wget git gcc gcc-c++ make \
                                  postgresql postgresql-server postgresql-contrib python3-psycopg2 \
                                  redis \
                                  libffi-devel libopenssl-devel \
                                  pkg-config
            ;;
        *)
            log_warning "Unknown distribution. Please install dependencies manually:"
            echo "  - Python 3.8+"
            echo "  - pip"
            echo "  - PostgreSQL"
            echo "  - Redis (optional)"
            echo "  - Development tools (gcc, make, etc.)"
            ;;
    esac

    log_success "System dependencies installation completed"
}

# --- Status Display ---
show_status() {
    echo ""
    echo "=============================================="
    echo "   🎸 HURTROCK MUSIC STORE STATUS 🎸"
    echo "=============================================="
    echo ""

    # Load environment
    if [ -f "$ENV_FILE" ]; then
        set -a
        source "$ENV_FILE"
        set +a
    fi

    local flask_port=${FLASK_PORT:-5000}
    local django_port=${DJANGO_PORT:-8000}
    local flask_host=${FLASK_HOST:-0.0.0.0}

    # Check Flask
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        log_success "Flask Server: Running (PID: $(cat "$PID_FILE"))"
        echo "   📱 Main Website: http://$flask_host:$flask_port"
        echo "   👨‍💼 Admin Panel: http://$flask_host:$flask_port/admin"
    else
        log_error "Flask Server: Not running"
    fi

    # Check Django
    if [ -f "$DJANGO_PID_FILE" ] && kill -0 "$(cat "$DJANGO_PID_FILE")" 2>/dev/null; then
        log_success "Django Chat Service: Running (PID: $(cat "$DJANGO_PID_FILE"))"
        echo "   💬 Chat API: http://$flask_host:$django_port"
        echo "   💬 Admin Chat: http://$flask_host:$flask_port/admin/chat"
    else
        log_warning "Django Chat Service: Not running"
    fi

    # System information
    echo ""
    echo "🖥️  System Information:"
    echo "   Distribution: $(detect_linux_distro)"
    echo "   Python: $(detect_python_cmd) ($($(detect_python_cmd) --version 2>&1))"
    echo "   PostgreSQL: $(command -v psql >/dev/null 2>&1 && echo "Available" || echo "Not installed")"
    echo "   Redis: $(command -v redis-server >/dev/null 2>&1 && echo "Available" || echo "Not installed")"

    echo ""
    echo "🔑 Default Admin Login:"
    echo "   Email: admin@hurtrock.com"
    echo "   Password: admin123"
    echo ""
    echo "📂 Configuration Files:"
    echo "   Environment: $ENV_FILE"
    echo "   Logs: $LOG_FILE"
    echo "   Virtual Environment: $VENV_DIR"
    echo ""
    echo "⚡ Management Commands:"
    echo "   $0 start      # Start services"
    echo "   $0 stop       # Stop services"
    echo "   $0 restart    # Restart services"
    echo "   $0 status     # Show status"
    echo "   $0 logs       # Show logs"
    echo "   $0 install    # Install dependencies"
    echo "   $0 setup      # Full setup (first time)"
    echo ""
    echo "=============================================="
}

# --- Help Function ---
show_help() {
    echo ""
    echo "🎸 Hurtrock Music Store - Universal Linux Server"
    echo "================================================"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start         Start all services (default)"
    echo "  stop          Stop all services"
    echo "  restart       Restart all services"
    echo "  status        Show service status"
    echo "  logs          Show live logs"
    echo "  install       Install system dependencies"
    echo "  setup         Complete first-time setup"
    echo "  service       Manage systemd service (auto-start/restart)"
    echo "  help          Show this help"
    echo ""
    echo "Options:"
    echo "  --no-deps     Skip dependency installation"
    echo "  --force       Force action even if services are running"
    echo ""
    echo "Service Management:"
    echo "  $0 service install    # Install as systemd service (auto-start/restart)"
    echo "  $0 service uninstall  # Remove systemd service"
    echo "  $0 service status     # Show systemd service status"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start servers (first run will setup)"
    echo "  $0 setup              # Complete first-time setup"
    echo "  $0 install            # Install system dependencies"
    echo "  $0 start --no-deps    # Start without installing dependencies"
    echo "  $0 service install    # Setup auto-start service"
    echo ""
    echo "First Time Setup:"
    echo "  1. Run: $0 setup"
    echo "  2. Follow the interactive configuration"
    echo "  3. Update .env file with your payment keys"
    echo "  4. Run: $0 service install (for auto-start)"
    echo "  5. Or run: $0 start (manual start)"
    echo ""
}

# --- Signal Handlers ---
cleanup() {
    echo ""
    log "Received shutdown signal, stopping services..."
    stop_services
    exit 0
}

trap cleanup SIGINT SIGTERM

# --- Service Management ---
manage_service() {
    local action="$1"
    
    case "$action" in
        "install")
            if [ ! -f "setup-systemd-service.sh" ]; then
                log_error "setup-systemd-service.sh tidak ditemukan!"
                echo "File ini diperlukan untuk instalasi service."
                return 1
            fi
            
            echo ""
            echo "🔧 Installing Systemd Service"
            echo "============================="
            echo ""
            echo "Service ini akan:"
            echo "  ✅ Otomatis start saat sistem boot"
            echo "  ✅ Auto-restart jika aplikasi crash"
            echo "  ✅ Berjalan sebagai system service"
            echo "  ✅ Terintegrasi dengan systemd logging"
            echo ""
            
            chmod +x setup-systemd-service.sh
            sudo ./setup-systemd-service.sh
            ;;
            
        "uninstall")
            if [ ! -f "setup-systemd-service.sh" ]; then
                log_error "setup-systemd-service.sh tidak ditemukan!"
                return 1
            fi
            
            sudo ./setup-systemd-service.sh uninstall
            ;;
            
        "status")
            if command -v systemctl >/dev/null 2>&1; then
                echo ""
                echo "🎸 Systemd Service Status"
                echo "========================"
                systemctl status hurtrock-music-store --no-pager || echo "Service belum diinstall"
                echo ""
                echo "Management commands:"
                echo "  sudo systemctl start hurtrock-music-store"
                echo "  sudo systemctl stop hurtrock-music-store" 
                echo "  sudo systemctl restart hurtrock-music-store"
                echo "  journalctl -u hurtrock-music-store -f"
            else
                log_error "Systemd tidak tersedia di sistem ini"
            fi
            ;;
            
        *)
            echo "Unknown service action: $action"
            echo ""
            echo "Available service actions:"
            echo "  install    - Install systemd service"
            echo "  uninstall  - Remove systemd service"
            echo "  status     - Show service status"
            ;;
    esac
}

# --- Main Execution ---
case "${1:-start}" in
    "service")
        manage_service "$2"
        ;;

    "setup")
        echo ""
        echo "🎸 Hurtrock Music Store - First Time Setup"
        echo "=========================================="
        echo ""
        
        log "Starting complete setup process..."
        
        # Install system dependencies
        install_system_dependencies
        
        # Setup PostgreSQL
        setup_postgresql
        
        # Setup Python environment
        setup_environment
        
        # Create .env configuration
        setup_env_file
        
        # Initialize database
        setup_database
        
        # Setup sample data
        setup_sample_data
        
        echo ""
        log_success "🎉 Setup completed successfully!"
        echo ""
        echo "Next steps:"
        echo "1. Edit $ENV_FILE to configure payment keys"
        echo "2. Run: $0 start"
        echo ""
        ;;

    "install")
        install_system_dependencies
        log_success "System dependencies installed successfully!"
        ;;

    "start")
        log "🎸 Starting Hurtrock Music Store..."

        # Check if this is first run
        if [ ! -f "$ENV_FILE" ]; then
            echo ""
            echo "🔧 First time setup required!"
            echo "============================="
            echo ""
            echo "This appears to be your first time running the server."
            echo "Let's configure everything for you."
            echo ""
            read -p "Continue with setup? (y/N): " confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                exec "$0" setup
            else
                echo "Setup cancelled. Run '$0 setup' when ready."
                exit 1
            fi
        fi

        # Stop any existing services
        stop_services

        # Setup environment if not using --no-deps
        if [[ "$2" != "--no-deps" ]]; then
            setup_environment
        fi

        # Load environment and setup database
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

    "help"|"--help"|"-h")
        show_help
        ;;

    *)
        echo "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
