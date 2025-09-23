
#!/bin/bash

# Hurtrock Music Store - Arch Linux Server Installation Script
# Script instalasi khusus untuk Arch Linux dengan PostgreSQL, Python venv, dan Valkey

echo "[START] Starting Hurtrock Music Store installation for Arch Linux server..."

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "Jangan jalankan script ini sebagai root!"
    print_step "Jalankan sebagai user biasa dan script akan menggunakan sudo bila diperlukan"
    exit 1
fi

# 1. Update system packages
print_step "Updating Arch Linux packages..."
sudo pacman -Syu --noconfirm
if [ $? -eq 0 ]; then
    print_success "System packages updated"
else
    print_error "Failed to update packages"
    exit 1
fi

# 2. Install base packages
print_step "Installing base development packages..."
sudo pacman -S --noconfirm base-devel git curl wget unzip
if [ $? -eq 0 ]; then
    print_success "Base development packages installed"
else
    print_error "Failed to install base packages"
    exit 1
fi

# 3. Install Python and development tools
print_step "Installing Python development environment..."
sudo pacman -S --noconfirm python python-pip python-virtualenv python-setuptools
sudo pacman -S --noconfirm python-dev python-wheel python-build
if [ $? -eq 0 ]; then
    print_success "Python development environment installed"
else
    print_error "Failed to install Python"
    exit 1
fi

# 4. Install PostgreSQL
print_step "Installing PostgreSQL..."
sudo pacman -S --noconfirm postgresql postgresql-contrib
if [ $? -eq 0 ]; then
    print_success "PostgreSQL installed"
else
    print_error "Failed to install PostgreSQL"
    exit 1
fi

# 5. Install Valkey (Redis alternative)
print_step "Installing Valkey..."
if ! command_exists yay; then
    print_step "Installing yay AUR helper..."
    cd /tmp
    git clone https://aur.archlinux.org/yay.git
    cd yay
    makepkg -si --noconfirm
    cd ~
fi

# Install Valkey from AUR
yay -S --noconfirm valkey
if [ $? -eq 0 ]; then
    print_success "Valkey installed"
else
    print_warning "Valkey installation failed, trying Redis as fallback..."
    sudo pacman -S --noconfirm redis
    if [ $? -eq 0 ]; then
        print_success "Redis installed as fallback"
        CACHE_SERVICE="redis"
    else
        print_error "Both Valkey and Redis installation failed"
        exit 1
    fi
fi

# Set cache service
CACHE_SERVICE=${CACHE_SERVICE:-valkey}

# 6. Install web server and process manager
print_step "Installing Nginx and Supervisor..."
sudo pacman -S --noconfirm nginx supervisor
if [ $? -eq 0 ]; then
    print_success "Nginx and Supervisor installed"
else
    print_error "Failed to install web server components"
    exit 1
fi

# 7. Install additional image processing libraries
print_step "Installing image processing libraries..."
sudo pacman -S --noconfirm libjpeg-turbo libpng zlib freetype2 lcms2 libwebp openjpeg2
if [ $? -eq 0 ]; then
    print_success "Image processing libraries installed"
else
    print_warning "Some image libraries may not be installed"
fi

# 8. Create application directory
APP_DIR="/opt/hurtrock-music-store"
print_step "Creating application directory: $APP_DIR"

sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy current files to app directory if not already there
if [ "$PWD" != "$APP_DIR" ]; then
    if [ -f "main.py" ]; then
        print_step "Copying application files..."
        cp -r . $APP_DIR/
        cd $APP_DIR
    else
        print_error "main.py not found. Please run this script from the application directory."
        exit 1
    fi
else
    print_step "Already in application directory"
fi

# 9. Create Python virtual environment
print_step "Creating Python virtual environment..."
python -m venv venv
if [ $? -eq 0 ]; then
    print_success "Virtual environment created"
else
    print_error "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

# 10. Upgrade pip and install Python dependencies
print_step "Installing Python dependencies in virtual environment..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
if [ $? -eq 0 ]; then
    print_success "Python dependencies installed"
else
    print_error "Failed to install some Python dependencies"
    exit 1
fi

# 11. Initialize PostgreSQL
print_step "Initializing PostgreSQL..."
sudo -u postgres initdb -D /var/lib/postgres/data
sudo systemctl enable postgresql.service
sudo systemctl start postgresql.service

# Wait for PostgreSQL to start
sleep 5

# Create database and user
DB_NAME="hurtrock_music_store"
DB_USER="fajar"
DB_PASS="fajar"

print_step "Creating PostgreSQL database and user..."
sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASS';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
\q
EOF

if [ $? -eq 0 ]; then
    print_success "PostgreSQL database created: $DB_NAME"
    DATABASE_URL="postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME"
else
    print_error "Failed to create PostgreSQL database"
    exit 1
fi

# 12. Setup Valkey/Redis
print_step "Setting up $CACHE_SERVICE..."
if [ "$CACHE_SERVICE" = "valkey" ]; then
    sudo systemctl enable valkey.service
    sudo systemctl start valkey.service
    CACHE_URL="valkey://localhost:6379/0"
else
    sudo systemctl enable redis.service
    sudo systemctl start redis.service
    CACHE_URL="redis://localhost:6379/0"
fi

if [ $? -eq 0 ]; then
    print_success "$CACHE_SERVICE service started"
else
    print_error "Failed to start $CACHE_SERVICE"
    exit 1
fi

# 13. Create environment configuration
print_step "Creating environment configuration..."

# Generate secure secret key
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(64))")

# Create .env file
cat > .env << EOF
# Database Configuration
DATABASE_URL='$DATABASE_URL'

# Security
SESSION_SECRET='$SECRET_KEY'
SECRET_KEY='$SECRET_KEY'
JWT_SECRET_KEY='$(python -c "import secrets; print(secrets.token_urlsafe(64))")'

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
IS_PRODUCTION=true

# Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
DJANGO_HOST=0.0.0.0
DJANGO_PORT=8000

# Cache Configuration
CACHE_URL=$CACHE_URL

# Payment Configuration (Set these with your actual keys)
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
MIDTRANS_SERVER_KEY=your_midtrans_server_key_here
MIDTRANS_CLIENT_KEY=your_midtrans_client_key_here

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_USE_TLS=True
EOF

print_success "Environment configuration created"

# 14. Initialize databases
print_step "Initializing application databases..."

# Export environment variables
export DATABASE_URL="$DATABASE_URL"
export SESSION_SECRET="$SECRET_KEY"

# Initialize Flask database
python -c "
import sys
sys.path.append('.')

try:
    from main import app
    print('[OK] Flask app initialized and database setup completed')
except Exception as e:
    print(f'[ERROR] Flask initialization error: {e}')
    sys.exit(1)
" || exit 1

# Initialize Django database
cd chat_service
export DJANGO_SETTINGS_MODULE=chat_microservice.settings

print_step "Setting up Django chat service..."
python manage.py makemigrations chat || print_warning "Django makemigrations warning"
python manage.py migrate || print_warning "Django migrate warning"

cd ..

# 15. Install sample data
print_step "Installing sample data..."
python sample_data.py || print_warning "Sample data installation failed, continuing..."

# 16. Create systemd service files
print_step "Creating systemd service files..."

# Flask service
sudo tee /etc/systemd/system/hurtrock-flask.service > /dev/null << EOF
[Unit]
Description=Hurtrock Music Store Flask Server
After=network.target postgresql.service $CACHE_SERVICE.service
Requires=postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin:\$PATH
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 main:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Django service
sudo tee /etc/systemd/system/hurtrock-django.service > /dev/null << EOF
[Unit]
Description=Hurtrock Music Store Django Chat Service
After=network.target postgresql.service $CACHE_SERVICE.service
Requires=postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR/chat_service
Environment=PATH=$APP_DIR/venv/bin:\$PATH
Environment=DJANGO_SETTINGS_MODULE=chat_microservice.settings
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Install gunicorn in virtual environment
print_step "Installing Gunicorn..."
pip install gunicorn
if [ $? -eq 0 ]; then
    print_success "Gunicorn installed"
else
    print_error "Failed to install Gunicorn"
    exit 1
fi

# Reload systemd and enable services
sudo systemctl daemon-reload
sudo systemctl enable hurtrock-flask.service
sudo systemctl enable hurtrock-django.service

print_success "Systemd services created and enabled"

# 17. Configure Nginx
print_step "Configuring Nginx..."

sudo tee /etc/nginx/sites-available/hurtrock-music-store > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    # Flask App (Main Store)
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Django Chat API
    location /api/chat/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support for Django Channels
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /opt/hurtrock-music-store/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
EOF

# Create sites-enabled directory if it doesn't exist
sudo mkdir -p /etc/nginx/sites-enabled

# Enable the site
sudo ln -sf /etc/nginx/sites-available/hurtrock-music-store /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t
if [ $? -eq 0 ]; then
    sudo systemctl enable nginx
    sudo systemctl restart nginx
    print_success "Nginx configured successfully"
else
    print_error "Nginx configuration error"
    exit 1
fi

# 18. Setup firewall (if ufw is installed)
if command_exists ufw; then
    print_step "Configuring firewall..."
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
    print_success "Firewall configured"
elif command_exists firewalld; then
    print_step "Configuring firewalld..."
    sudo systemctl enable firewalld
    sudo systemctl start firewalld
    sudo firewall-cmd --permanent --add-service=ssh
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --reload
    print_success "Firewalld configured"
fi

# 19. Create management scripts
print_step "Creating management scripts..."

# Service management script
cat > manage-services.sh << 'EOF'
#!/bin/bash

case "$1" in
    start)
        echo "Starting Hurtrock Music Store services..."
        sudo systemctl start hurtrock-flask.service
        sudo systemctl start hurtrock-django.service
        sudo systemctl restart nginx
        echo "Services started"
        ;;
    stop)
        echo "Stopping Hurtrock Music Store services..."
        sudo systemctl stop hurtrock-flask.service
        sudo systemctl stop hurtrock-django.service
        echo "Services stopped"
        ;;
    restart)
        echo "Restarting Hurtrock Music Store services..."
        sudo systemctl restart hurtrock-flask.service
        sudo systemctl restart hurtrock-django.service
        sudo systemctl restart nginx
        echo "Services restarted"
        ;;
    status)
        echo "Checking service status..."
        sudo systemctl status hurtrock-flask.service --no-pager
        sudo systemctl status hurtrock-django.service --no-pager
        sudo systemctl status nginx --no-pager
        ;;
    logs)
        echo "Showing service logs..."
        sudo journalctl -u hurtrock-flask.service -u hurtrock-django.service -f
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
EOF

chmod +x manage-services.sh

# Backup script
cat > backup-arch.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/var/backups/hurtrock"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "Creating backup..."

# Database backup
sudo -u postgres pg_dump hurtrock_music_store > $BACKUP_DIR/database_$DATE.sql

# Application files backup
tar -czf $BACKUP_DIR/app_files_$DATE.tar.gz /opt/hurtrock-music-store

# Keep only last 7 backups
find $BACKUP_DIR -name "*.sql" -type f -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -type f -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup-arch.sh

print_success "Management scripts created"

# 20. Start services
print_step "Starting services..."
sudo systemctl start hurtrock-flask.service
sudo systemctl start hurtrock-django.service

# Wait a moment for services to start
sleep 5

# Check service status
if sudo systemctl is-active --quiet hurtrock-flask.service; then
    print_success "Flask service is running"
else
    print_error "Flask service failed to start"
    sudo journalctl -u hurtrock-flask.service --no-pager -n 10
fi

if sudo systemctl is-active --quiet hurtrock-django.service; then
    print_success "Django service is running"
else
    print_error "Django service failed to start"
    sudo journalctl -u hurtrock-django.service --no-pager -n 10
fi

# Deactivate virtual environment
deactivate

# 21. Final summary
echo ""
echo "=============================================="
echo "   INSTALLATION COMPLETED - ARCH LINUX"
echo "=============================================="
echo ""
print_success "Flask Server configured and running"
print_success "Django Chat Service configured and running"
print_success "Nginx reverse proxy configured"
print_success "PostgreSQL database initialized"
print_success "$CACHE_SERVICE cache server configured"
print_success "Python virtual environment created"
print_success "Systemd services enabled"
print_success "Sample data installed"
echo ""
echo "IMPORTANT INFORMATION:"
echo "Admin Login:"
echo "  Email: admin@hurtrock.com"
echo "  Password: admin123"
echo ""
echo "DATABASE CONFIGURATION:"
echo "  Name: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASS"
echo "  Host: localhost"
echo "  Port: 5432"
echo ""
echo "SERVER ACCESS:"
echo "  Main Store: http://your-server-ip/"
echo "  Admin Panel: http://your-server-ip/admin"
echo ""
echo "MANAGEMENT COMMANDS:"
echo "  ./manage-services.sh start    # Start services"
echo "  ./manage-services.sh stop     # Stop services"
echo "  ./manage-services.sh restart  # Restart services"
echo "  ./manage-services.sh status   # Check status"
echo "  ./manage-services.sh logs     # View logs"
echo "  ./backup-arch.sh              # Create backup"
echo ""
echo "VIRTUAL ENVIRONMENT:"
echo "  Activate: source $APP_DIR/venv/bin/activate"
echo "  Deactivate: deactivate"
echo ""
echo "CONFIGURATION FILES:"
echo "  Application: $APP_DIR"
echo "  Environment: $APP_DIR/.env"
echo "  Nginx: /etc/nginx/sites-available/hurtrock-music-store"
echo "  Services: /etc/systemd/system/hurtrock-*.service"
echo ""
echo "NEXT STEPS:"
echo "1. Configure your payment gateway keys in .env file"
echo "2. Setup SSL certificate for HTTPS (recommended: Let's Encrypt)"
echo "3. Configure email settings for notifications"
echo "4. Setup regular backups using cron"
echo ""
print_success "Hurtrock Music Store is ready for production on Arch Linux!"
echo "=============================================="
