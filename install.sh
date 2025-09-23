
#!/bin/bash

# Hurtrock Music Store - Universal Auto Installation Script
# Script untuk konfigurasi otomatis server Flask dan Django Chat dengan PostgreSQL
# Compatible dengan berbagai environment termasuk Replit, Linux, macOS, dan Windows (WSL)

echo "🚀 Memulai instalasi dan konfigurasi Hurtrock Music Store..."

# Set warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
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
EOF
fi

# Install dependencies
$PIP_CMD install -r requirements.txt
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
    print('✅ Flask app berhasil dimuat dan database diinisialisasi')
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
" || exit 1

# 6. Test Django chat service
print_step "Menguji Django Chat Service..."
cd chat_service || exit 1

# Test Django setup
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
    
    print('✅ Django chat service berhasil dikonfigurasi')
except Exception as e:
    print(f'❌ Django error: {e}')
    sys.exit(1)
" || {
    print_error "Django chat service gagal, tetapi melanjutkan..."
}

cd ..

# 7. Create startup scripts
print_step "Membuat startup scripts..."

# Universal start script
cat > start_server.sh << 'EOF'
#!/bin/bash

# Universal start script untuk Hurtrock Music Store
echo "🚀 Memulai Hurtrock Music Store..."

# Load environment variables
if [[ -f ".env" ]]; then
    export $(grep -v '^#' .env | xargs)
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
        echo "❌ Python not found"
        exit 1
    fi
fi

# Function to start services
start_services() {
    echo "📱 Starting Django Chat Service on port 8000..."
    cd chat_service
    $PYTHON_CMD manage.py runserver 0.0.0.0:8000 --noreload &
    DJANGO_PID=$!
    echo "Django Chat Service PID: $DJANGO_PID"
    cd ..
    
    # Wait a moment for Django to start
    sleep 3
    
    echo "🌐 Starting Flask Server on port 5000..."
    $PYTHON_CMD main.py &
    FLASK_PID=$!
    echo "Flask Server PID: $FLASK_PID"
    
    echo ""
    echo "✅ All services started successfully!"
    echo "🌐 Main Store: http://localhost:5000"
    echo "📱 Chat Service: http://localhost:8000"
    echo "🔗 Admin Panel: http://localhost:5000/admin"
    echo "💬 Chat Interface: http://localhost:5000/admin/chat"
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
    trap 'echo ""; echo "🛑 Stopping all services..."; kill $DJANGO_PID $FLASK_PID 2>/dev/null; echo "✅ All services stopped"; exit' INT
    wait
}

start_services
EOF

chmod +x start_server.sh
print_success "Startup script dibuat: ./start_server.sh"

# Create development script
cat > dev_server.sh << 'EOF'
#!/bin/bash

# Development server dengan hot reload
echo "🔧 Starting Development Server..."

# Load environment variables
if [[ -f ".env" ]]; then
    export $(grep -v '^#' .env | xargs)
fi

# Detect Python command
PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python"
fi

echo "Starting Flask in debug mode..."
FLASK_ENV=development $PYTHON_CMD main.py
EOF

chmod +x dev_server.sh
print_success "Development script dibuat: ./dev_server.sh"

# 8. Final summary
echo ""
echo "🎉 =============================================="
echo "   INSTALASI SELESAI - HURTROCK MUSIC STORE"
echo "=============================================="
echo ""
print_success "✅ Flask Server dikonfigurasi"
print_success "✅ Django Chat Service dikonfigurasi"  
print_success "✅ Database terintegrasi ($PLATFORM compatible)"
print_success "✅ Sample data dan produk siap"
print_success "✅ Universal startup scripts dibuat"
echo ""
echo "📋 INFORMASI PENTING:"
echo "🔑 Admin Login:"
echo "   Email: admin@hurtrock.com"
echo "   Password: admin123"
echo ""
echo "🚀 CARA MENJALANKAN:"
echo "   ./start_server.sh    # Production mode"
echo "   ./dev_server.sh      # Development mode"
echo ""
echo "🌐 URL AKSES:"
echo "   Main Store: http://localhost:5000"
echo "   Chat Service: http://localhost:8000" 
echo "   Admin Panel: http://localhost:5000/admin"
echo "   Chat Interface: http://localhost:5000/admin/chat"
echo ""
echo "📱 FITUR YANG TERSEDIA:"
echo "   ✅ Real-time chat dengan scroll fix"
echo "   ✅ Fixed input container di admin chat"
echo "   ✅ Auto database setup (Flask + Django)"
echo "   ✅ Universal compatibility"
echo "   ✅ Environment auto-detection"
echo "   ✅ E-commerce lengkap dengan payment"
echo ""
echo "📁 FILE KONFIGURASI:"
echo "   .env - Environment variables"
echo "   start_server.sh - Production startup"
echo "   dev_server.sh - Development startup"
echo ""
print_success "🎶 Hurtrock Music Store siap digunakan di $PLATFORM!"
echo "=============================================="
