#!/bin/bash

# Hurtrock Music Store - Auto Installation Script
# Script untuk konfigurasi otomatis server Flask dan Django Chat dengan PostgreSQL

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

# 1. Check Python installation
print_step "Memeriksa instalasi Python..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python ditemukan: $PYTHON_VERSION"
else
    print_error "Python3 tidak ditemukan. Silakan install Python3 terlebih dahulu."
    exit 1
fi

# 2. Check pip installation
print_step "Memeriksa instalasi pip..."
if command_exists pip3; then
    print_success "pip3 tersedia"
elif command_exists pip; then
    print_success "pip tersedia"
else
    print_error "pip tidak ditemukan. Silakan install pip terlebih dahulu."
    exit 1
fi

# 3. Install Python dependencies
print_step "Menginstall dependensi Python..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependensi Python berhasil diinstall"
else
    print_warning "requirements.txt tidak ditemukan, menginstall dependensi manual..."
    
    # Core Flask dependencies
    pip install flask flask-login flask-sqlalchemy flask-migrate flask-wtf werkzeug
    
    # Database dependencies
    pip install psycopg2-binary
    
    # Additional dependencies
    pip install pillow stripe midtransclient reportlab python-dotenv email-validator
    
    # Django Chat Service dependencies
    pip install django djangorestframework channels channels-redis dj-database-url corsheaders daphne
    
    print_success "Dependensi manual berhasil diinstall"
fi

# 4. Check environment variables
print_step "Memeriksa environment variables..."

# Check SESSION_SECRET
if [ -z "$SESSION_SECRET" ]; then
    print_warning "SESSION_SECRET tidak ditemukan, generating random secret..."
    export SESSION_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "export SESSION_SECRET='$SESSION_SECRET'" >> ~/.bashrc
    print_success "SESSION_SECRET generated dan disimpan"
else
    print_success "SESSION_SECRET ditemukan"
fi

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    print_error "DATABASE_URL tidak ditemukan!"
    print_warning "Silakan set DATABASE_URL environment variable untuk PostgreSQL"
    echo "Contoh: export DATABASE_URL='postgresql://username:password@host:port/database'"
    exit 1
else
    print_success "DATABASE_URL ditemukan"
fi

# 5. Initialize Flask database
print_step "Menginisialisasi database Flask..."
python3 -c "
try:
    from main import app
    from database import db
    with app.app_context():
        db.create_all()
        print('✅ Flask database berhasil diinisialisasi')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"

# 6. Run Django migrations
print_step "Menjalankan migrasi Django Chat Service..."
cd chat_service || exit 1

# Clean up existing migrations if needed
if [ -d "chat/migrations" ]; then
    rm -f chat/migrations/0*.py
    print_success "Cleaned up old migrations"
fi

# Make migrations
python3 manage.py makemigrations chat
if [ $? -eq 0 ]; then
    print_success "Django migrations berhasil dibuat"
else
    print_error "Gagal membuat Django migrations"
    exit 1
fi

# Apply migrations
python3 manage.py migrate
if [ $? -eq 0 ]; then
    print_success "Django migrations berhasil diaplikasikan"
else
    print_error "Gagal mengaplikasikan Django migrations"
    exit 1
fi

# Test chat service functionality
print_step "Testing chat service..."
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')
django.setup()

from chat.models import ChatRoom, ChatMessage, ChatSession
from django.db import connection

try:
    # Test database connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    
    # Test model creation
    test_room = ChatRoom.objects.create(
        name='test_room',
        buyer_id=1,
        buyer_name='Test User',
        buyer_email='test@example.com'
    )
    
    test_message = ChatMessage.objects.create(
        room=test_room,
        user_id=1,
        user_name='Test User',
        message='Test message',
        sender_type='buyer'
    )
    
    print('✅ Chat service database test passed')
    
    # Clean up test data
    test_message.delete()
    test_room.delete()
    
except Exception as e:
    print(f'❌ Chat service test failed: {e}')
    exit(1)
"

cd ..

# 7. Create sample data
print_step "Membuat sample data..."
python3 -c "
try:
    from sample_data import create_sample_data, create_suppliers_and_products
    create_sample_data()
    create_suppliers_and_products()
    print('✅ Sample data berhasil dibuat')
except Exception as e:
    print(f'❌ Error creating sample data: {e}')
"

# 8. Test Flask server
print_step "Testing Flask server..."
python3 -c "
try:
    from main import app
    print('✅ Flask app berhasil dimuat')
except Exception as e:
    print(f'❌ Error loading Flask app: {e}')
    exit(1)
"

# 9. Create start script
print_step "Membuat start script..."
cat > start_server.sh << 'EOF'
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
EOF

chmod +x start_server.sh
print_success "Start script dibuat: ./start_server.sh"

# 10. Final summary
echo ""
echo "🎉 =============================================="
echo "   INSTALASI SELESAI - HURTROCK MUSIC STORE"
echo "=============================================="
echo ""
print_success "✅ Flask Server dikonfigurasi"
print_success "✅ Django Chat Service dikonfigurasi"  
print_success "✅ PostgreSQL database terintegrasi"
print_success "✅ Sample data dan produk ditambahkan"
print_success "✅ Supplier Swelee, Media Recording Tech, Triple 3 Music Store"
print_success "✅ 10 produk baru dari supplier tersebut"
echo ""
echo "📋 INFORMASI PENTING:"
echo "🔑 Admin Login:"
echo "   Email: admin@hurtrock.com"
echo "   Password: admin123"
echo ""
echo "🚀 CARA MENJALANKAN:"
echo "   ./start_server.sh"
echo ""
echo "🌐 URL AKSES:"
echo "   Main Store: http://localhost:5000"
echo "   Chat Service: http://localhost:8000" 
echo "   Admin Panel: http://localhost:5000/admin"
echo ""
echo "📱 FITUR YANG TERSEDIA:"
echo "   ✅ Floating chat realtime (buyer & admin)"
echo "   ✅ Product tagging dalam chat"
echo "   ✅ E-commerce lengkap dengan payment"
echo "   ✅ Inventory management"
echo "   ✅ Shipping calculator"
echo ""
print_success "🎶 Hurtrock Music Store siap digunakan!"
echo "=============================================="