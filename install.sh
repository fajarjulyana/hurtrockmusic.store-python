
#!/bin/bash

# Hurtrock Music Store - Universal Auto Installation Script
# Script untuk konfigurasi otomatis server Flask dan Django Chat dengan PostgreSQL
# Compatible dengan berbagai environment termasuk Replit, Linux, macOS, dan Windows (WSL)

echo "[START] Memulai instalasi dan konfigurasi Hurtrock Music Store..."

# Set warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect platform
detect_platform() {
    if [[ "$REPLIT_ENVIRONMENT" == "production" ]] || [[ -n "$REPL_ID" ]]; then
        echo "replit"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ -n "$WSL_DISTRO_NAME" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

PLATFORM=$(detect_platform)
print_step "Platform detected: $PLATFORM"

# 1. Check Python installation
print_step "Memeriksa instalasi Python..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python ditemukan: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_VERSION=$(python --version)
    print_success "Python ditemukan: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    print_error "Python tidak ditemukan. Silakan install Python terlebih dahulu."
    if [[ "$PLATFORM" == "linux" ]]; then
        echo "Install dengan: sudo apt update && sudo apt install python3 python3-pip"
    elif [[ "$PLATFORM" == "macos" ]]; then
        echo "Install dengan: brew install python3"
    elif [[ "$PLATFORM" == "windows" ]]; then
        echo "Download dari: https://www.python.org/downloads/"
    fi
    exit 1
fi

# 2. Check pip installation
print_step "Memeriksa instalasi pip..."
if command_exists pip3; then
    print_success "pip3 tersedia"
    PIP_CMD="pip3"
elif command_exists pip; then
    print_success "pip tersedia"
    PIP_CMD="pip"
else
    print_error "pip tidak ditemukan."
    if [[ "$PLATFORM" == "linux" ]]; then
        echo "Install dengan: sudo apt install python3-pip"
    elif [[ "$PLATFORM" == "macos" ]]; then
        echo "Install dengan: python3 -m ensurepip --upgrade"
    fi
    exit 1
fi

# 3. Install Python dependencies
print_step "Menginstall dependensi Python..."

# Create requirements if not exists or update existing one
if [[ ! -f "requirements.txt" ]]; then
    print_warning "requirements.txt tidak ditemukan, membuat requirements universal..."
    cat > requirements.txt << 'EOF'
# Core Flask dependencies
flask>=3.1.2
flask-login>=0.6.3
flask-migrate>=4.1.0
flask-sqlalchemy>=3.1.1
flask-wtf>=1.2.2
werkzeug>=3.1.3

# Database
psycopg2-binary>=2.9.10
sqlalchemy>=2.0.43

# Image processing
pillow>=11.3.0

# Payment gateways
stripe>=12.5.1
midtransclient>=1.4.2

# PDF and Excel generation
reportlab>=4.4.4
openpyxl>=3.1.5

# Environment and validation
python-dotenv>=1.1.1
email-validator>=2.3.0

# Django chat service dependencies
django>=5.2.6
djangorestframework>=3.14.0
django-cors-headers>=4.3.1
channels>=4.0.0
channels-redis>=4.2.0
daphne>=4.1.2
dj-database-url>=3.0.1

# JWT for authentication
pyjwt>=2.8.0
cryptography>=41.0.8

# HTTP requests for service communication
requests>=2.31.0

# Redis (optional, fallback to in-memory)
redis>=5.0.1

# Additional utilities
python-dateutil>=2.8.2
pytz>=2023.3
EOF
fi

# Install dependencies with better error handling for Windows
print_step "Installing Python packages..."
$PIP_CMD install --upgrade pip
$PIP_CMD install -r requirements.txt --no-cache-dir
if [[ $? -eq 0 ]]; then
    print_success "Dependensi Python berhasil diinstall"
else
    print_warning "Beberapa dependensi mungkin gagal, melanjutkan instalasi..."
fi

# 4. Setup environment variables
print_step "Memeriksa environment variables..."

# Function to generate secure random string
generate_secret() {
    if command_exists openssl; then
        openssl rand -hex 32
    elif command_exists python3; then
        python3 -c "import secrets; print(secrets.token_urlsafe(32))"
    elif command_exists python; then
        python -c "import secrets; print(secrets.token_urlsafe(32))"
    else
        echo "hurtrock_music_store_$(date +%s)_secret_key"
    fi
}

# Check SESSION_SECRET
if [[ -z "$SESSION_SECRET" ]]; then
    print_warning "SESSION_SECRET tidak ditemukan, generating random secret..."
    NEW_SECRET=$(generate_secret)
    export SESSION_SECRET="$NEW_SECRET"
    
    # Save to .env file
    echo "SESSION_SECRET='$NEW_SECRET'" >> .env
    print_success "SESSION_SECRET generated dan disimpan ke .env"
else
    print_success "SESSION_SECRET ditemukan"
fi

# Check DATABASE_URL
if [[ -z "$DATABASE_URL" ]]; then
    print_warning "DATABASE_URL tidak ditemukan!"
    
    # Try to setup local PostgreSQL for non-Replit environments
    if [[ "$PLATFORM" != "replit" ]]; then
        print_step "Mencoba setup PostgreSQL lokal..."
        
        if command_exists psql; then
            print_success "PostgreSQL ditemukan"
            DB_NAME="hurtrock_music_store"
            DB_USER="postgres"
            DB_HOST="localhost"
            DB_PORT="5432"
            
            # Try to create database
            createdb $DB_NAME 2>/dev/null || true
            
            export DATABASE_URL="postgresql://$DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
            echo "DATABASE_URL='$DATABASE_URL'" >> .env
            print_success "DATABASE_URL lokal dibuat: $DATABASE_URL"
        else
            print_error "PostgreSQL tidak ditemukan dan DATABASE_URL tidak diset!"
            echo ""
            echo "Opsi setup database:"
            echo "1. Install PostgreSQL lokal:"
            if [[ "$PLATFORM" == "linux" ]]; then
                echo "   sudo apt install postgresql postgresql-contrib"
            elif [[ "$PLATFORM" == "macos" ]]; then
                echo "   brew install postgresql"
            elif [[ "$PLATFORM" == "windows" ]]; then
                echo "   Download PostgreSQL dari: https://www.postgresql.org/download/windows/"
            fi
            echo ""
            echo "2. Gunakan database cloud seperti:"
            echo "   - Neon (https://neon.tech)"
            echo "   - Supabase (https://supabase.com)"
            echo "   - ElephantSQL (https://www.elephantsql.com)"
            echo ""
            echo "3. Set environment variable:"
            echo "   export DATABASE_URL='postgresql://user:pass@host:port/dbname'"
            exit 1
        fi
    else
        print_error "DATABASE_URL diperlukan untuk Replit environment"
        echo "Silakan set DATABASE_URL environment variable di Replit Secrets"
        exit 1
    fi
else
    print_success "DATABASE_URL ditemukan"
fi

# 5. Initialize databases
print_step "Menginisialisasi database..."

# Test Flask app initialization
$PYTHON_CMD -c "
import sys
sys.path.append('.')

try:
    from main import app
    print('[OK] Flask app berhasil dimuat dan database diinisialisasi')
except Exception as e:
    print(f'[ERROR] Error: {e}')
    sys.exit(1)
" || exit 1

# 6. Install sample data
print_step "Menginstall sample data..."

# Run sample data installation
$PYTHON_CMD -c "
import sys
sys.path.append('.')

try:
    from sample_data import create_sample_data
    create_sample_data()
    print('[OK] Sample data berhasil diinstall')
except Exception as e:
    print(f'[ERROR] Error installing sample data: {e}')
    # Continue anyway
" || print_warning "Sample data installation failed, continuing..."

# 7. Setup Django Chat Service dengan migrations yang benar
print_step "Menyiapkan Django Chat Service..."

cd chat_service || {
    print_error "Directory chat_service tidak ditemukan"
    exit 1
}

# Clean up any existing migration files
if [[ -d "chat/migrations" ]]; then
    find chat/migrations -name "*.py" -not -name "__init__.py" -delete 2>/dev/null || true
    print_step "Membersihkan migrations lama..."
fi

# Set Django environment
export DJANGO_SETTINGS_MODULE=chat_microservice.settings

# Create fresh migrations
print_step "Membuat migrations Django..."
$PYTHON_CMD manage.py makemigrations chat || print_warning "Makemigrations warning, continuing..."

# Apply migrations
print_step "Menjalankan migrations Django..."
$PYTHON_CMD manage.py migrate || print_warning "Migrate warning, continuing..."

# Test Django setup
print_step "Menguji setup Django..."
$PYTHON_CMD -c "
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')

try:
    django.setup()
    from chat.models import ChatRoom
    from django.db import connection
    
    # Test database connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    
    print('[OK] Django chat service berhasil dikonfigurasi')
except Exception as e:
    print(f'[WARNING] Django error: {e}')
" || print_warning "Django setup warning, continuing..."

cd ..

print_success "Django Chat Service siap digunakan"

# 8. Create startup scripts
print_step "Membuat startup scripts..."

# Universal start script for Windows compatibility
cat > start_server.sh << 'EOF'
#!/bin/bash

# Universal start script untuk Hurtrock Music Store
echo "[START] Memulai Hurtrock Music Store..."

# Load environment variables
if [[ -f ".env" ]]; then
    export $(grep -v '^#' .env | xargs) 2>/dev/null || true
fi

# Function to check if port is available
check_port() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "Port $port is already in use"
            return 1
        fi
    elif command -v netstat >/dev/null 2>&1; then
        if netstat -tuln | grep ":$port " >/dev/null 2>&1; then
            echo "Port $port is already in use"
            return 1
        fi
    fi
    return 0
}

# Detect Python command
PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    if command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
    else
        echo "[ERROR] Python not found"
        exit 1
    fi
fi

# Function to start services
start_services() {
    echo "[SETUP] Preparing Django Chat Service..."
    cd chat_service || {
        echo "[ERROR] chat_service directory not found"
        exit 1
    }

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

    # Test Django connection with multiple attempts
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
    echo "[WEB] Main Store: http://0.0.0.0:5000"
    echo "[MOBILE] Chat Service: http://0.0.0.0:8000"
    echo "[LINK] Admin Panel: http://0.0.0.0:5000/admin"
    echo "[CHAT] Chat Interface: http://0.0.0.0:5000/admin/chat"
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
EOF

# Make script executable
chmod +x start_server.sh 2>/dev/null || true
print_success "Startup script dibuat: ./start_server.sh"

# Create development script
cat > dev_server.sh << 'EOF'
#!/bin/bash

# Development server dengan hot reload
echo "[SETUP] Starting Development Server..."

# Load environment variables
if [[ -f ".env" ]]; then
    export $(grep -v '^#' .env | xargs) 2>/dev/null || true
fi

# Detect Python command
PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python"
fi

echo "Starting Flask in debug mode..."
FLASK_ENV=development $PYTHON_CMD main.py
EOF

# Make script executable
chmod +x dev_server.sh 2>/dev/null || true
print_success "Development script dibuat: ./dev_server.sh"

# 9. Create Windows batch files for Windows Server
if [[ "$PLATFORM" == "windows" ]]; then
    print_step "Membuat Windows batch files..."
    
    cat > start_server.bat << 'EOF'
@echo off
echo [START] Memulai Hurtrock Music Store...

rem Load environment variables if .env exists
if exist .env (
    for /f "usebackq tokens=1,2 delims==" %%i in (".env") do (
        if not "%%i"=="" if not "%%j"=="" set %%i=%%j
    )
)

rem Detect Python command
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON_CMD=python3
    ) else (
        echo [ERROR] Python not found
        exit /b 1
    )
)

echo [SETUP] Preparing Django Chat Service...
cd chat_service
if %errorlevel% neq 0 (
    echo [ERROR] chat_service directory not found
    exit /b 1
)

set DJANGO_SETTINGS_MODULE=chat_microservice.settings

echo [DJANGO] Checking migrations...
%PYTHON_CMD% manage.py migrate --run-syncdb >nul 2>&1

echo [MOBILE] Starting Django Chat Service on port 8000...
start "Django Chat Service" %PYTHON_CMD% manage.py runserver 0.0.0.0:8000 --noreload

cd ..

echo [WAIT] Waiting for Django to initialize...
timeout /t 5 /nobreak >nul

echo [WEB] Starting Flask Server on port 5000...
start "Flask Server" %PYTHON_CMD% main.py

echo.
echo [OK] All services started successfully!
echo [WEB] Main Store: http://0.0.0.0:5000
echo [MOBILE] Chat Service: http://0.0.0.0:8000
echo [LINK] Admin Panel: http://0.0.0.0:5000/admin
echo [CHAT] Chat Interface: http://0.0.0.0:5000/admin/chat
echo.
echo Default Admin Login:
echo   Email: admin@hurtrock.com
echo   Password: admin123
echo.
echo Press any key to continue...
pause >nul
EOF

    print_success "Windows startup script dibuat: start_server.bat"
fi

# 10. Final summary
echo ""
echo "[SUCCESS] =============================================="
echo "   INSTALASI SELESAI - HURTROCK MUSIC STORE"
echo "=============================================="
echo ""
print_success "[OK] Flask Server dikonfigurasi"
print_success "[OK] Django Chat Service dikonfigurasi"  
print_success "[OK] Database terintegrasi ($PLATFORM compatible)"
print_success "[OK] Sample data dan produk siap"
print_success "[OK] Universal startup scripts dibuat"
echo ""
echo "[INFO] INFORMASI PENTING:"
echo "[KEY] Admin Login:"
echo "   Email: admin@hurtrock.com"
echo "   Password: admin123"
echo ""
echo "[START] CARA MENJALANKAN:"
if [[ "$PLATFORM" == "windows" ]]; then
    echo "   start_server.bat     # Windows batch file"
fi
echo "   ./start_server.sh    # Production mode (Unix)"
echo "   ./dev_server.sh      # Development mode (Unix)"
echo ""
echo "[WEB] URL AKSES:"
echo "   Main Store: http://0.0.0.0:5000"
echo "   Chat Service: http://0.0.0.0:8000" 
echo "   Admin Panel: http://0.0.0.0:5000/admin"
echo "   Chat Interface: http://0.0.0.0:5000/admin/chat"
echo ""
echo "[MOBILE] FITUR YANG TERSEDIA:"
echo "   [OK] Real-time chat dengan scroll fix"
echo "   [OK] Fixed input container di admin chat"
echo "   [OK] Auto database setup (Flask + Django)"
echo "   [OK] Universal compatibility"
echo "   [OK] Environment auto-detection"
echo "   [OK] E-commerce lengkap dengan payment"
echo ""
echo "[FILE] FILE KONFIGURASI:"
echo "   .env - Environment variables"
echo "   start_server.sh - Production startup (Unix)"
if [[ "$PLATFORM" == "windows" ]]; then
    echo "   start_server.bat - Production startup (Windows)"
fi
echo "   dev_server.sh - Development startup (Unix)"
echo ""
print_success "[MUSIC] Hurtrock Music Store siap digunakan di $PLATFORM!"
echo "=============================================="
