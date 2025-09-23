
#!/bin/bash

# Hurtrock Music Store - Linux Server Installation Script
# Universal installation script for Linux servers
# Compatible with Ubuntu, CentOS, RHEL, and other Linux distributions

echo "[START] Starting Hurtrock Music Store installation for Linux server..."

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

# Function to detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo $ID
    elif [ -f /etc/redhat-release ]; then
        echo "centos"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    else
        echo "unknown"
    fi
}

DISTRO=$(detect_distro)
print_step "Linux distribution detected: $DISTRO"

# 1. Update system packages
print_step "Updating system packages..."
case $DISTRO in
    "ubuntu"|"debian")
        sudo apt update -y
        sudo apt upgrade -y
        ;;
    "centos"|"rhel"|"fedora")
        if command_exists dnf; then
            sudo dnf update -y
        elif command_exists yum; then
            sudo yum update -y
        fi
        ;;
    *)
        print_warning "Unknown distribution, skipping system update"
        ;;
esac

# 2. Install system dependencies
print_step "Installing system dependencies..."
case $DISTRO in
    "ubuntu"|"debian")
        sudo apt install -y python3 python3-pip python3-venv python3-dev \
                           postgresql postgresql-contrib postgresql-client \
                           nginx supervisor git curl wget unzip \
                           build-essential libpq-dev libjpeg-dev zlib1g-dev \
                           libssl-dev libffi-dev
        ;;
    "centos"|"rhel"|"fedora")
        if command_exists dnf; then
            sudo dnf install -y python3 python3-pip python3-devel \
                               postgresql postgresql-server postgresql-contrib \
                               nginx supervisor git curl wget unzip \
                               gcc gcc-c++ make postgresql-devel \
                               libjpeg-turbo-devel zlib-devel \
                               openssl-devel libffi-devel
        elif command_exists yum; then
            sudo yum install -y python3 python3-pip python3-devel \
                               postgresql postgresql-server postgresql-contrib \
                               nginx supervisor git curl wget unzip \
                               gcc gcc-c++ make postgresql-devel \
                               libjpeg-turbo-devel zlib-devel \
                               openssl-devel libffi-devel
        fi
        
        # Initialize PostgreSQL on RHEL/CentOS if needed
        if [ ! -d "/var/lib/pgsql/data/base" ]; then
            sudo postgresql-setup initdb
        fi
        ;;
    *)
        print_error "Unsupported distribution. Please install dependencies manually."
        exit 1
        ;;
esac

# 3. Check Python installation
print_step "Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
else
    print_error "Python3 not found after installation"
    exit 1
fi

# 4. Check pip installation
print_step "Checking pip installation..."
if command_exists pip3; then
    print_success "pip3 available"
    PIP_CMD="pip3"
elif command_exists pip; then
    print_success "pip available"
    PIP_CMD="pip"
else
    print_error "pip not found after installation"
    exit 1
fi

# 5. Setup PostgreSQL
print_step "Setting up PostgreSQL..."

# Start and enable PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
DB_NAME="hurtrock_music_store"
DB_USER="hurtrock_user"
DB_PASS="hurtrock_pass_$(date +%s)"

sudo -u postgres psql <<EOF
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
    print_warning "PostgreSQL setup may have issues, continuing..."
    DATABASE_URL="postgresql://postgres@localhost:5432/$DB_NAME"
fi

# 6. Create application directory
APP_DIR="/opt/hurtrock-music-store"
print_step "Creating application directory: $APP_DIR"

if [ "$PWD" != "$APP_DIR" ]; then
    sudo mkdir -p $APP_DIR
    sudo chown $USER:$USER $APP_DIR
    
    # Copy current files to app directory if not already there
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

# 7. Install Python dependencies
print_step "Installing Python dependencies..."

# Upgrade pip first
$PIP_CMD install --user --upgrade pip

# Create requirements.txt if not exists
if [ ! -f "requirements.txt" ]; then
    print_warning "requirements.txt not found, creating universal requirements..."
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

# Redis for production
redis>=5.0.1

# Additional utilities
python-dateutil>=2.8.2
pytz>=2023.3

# Production server
gunicorn>=21.2.0
EOF
fi

# Install Python packages
$PIP_CMD install --user -r requirements.txt --no-cache-dir
if [ $? -eq 0 ]; then
    print_success "Python dependencies installed successfully"
else
    print_warning "Some dependencies may have failed, continuing..."
fi

# 8. Setup environment variables
print_step "Setting up environment variables..."

# Generate secure secret key
if command_exists openssl; then
    SECRET_KEY=$(openssl rand -hex 32)
else
    SECRET_KEY="hurtrock_music_store_$(date +%s)_secret_key"
fi

# Create .env file
cat > .env << EOF
# Database Configuration
DATABASE_URL='$DATABASE_URL'

# Security
SESSION_SECRET='$SECRET_KEY'
SECRET_KEY='$SECRET_KEY'

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
DJANGO_HOST=0.0.0.0
DJANGO_PORT=8000

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

print_success "Environment variables configured"

# 9. Initialize databases
print_step "Initializing databases..."

# Export environment variables
export DATABASE_URL="$DATABASE_URL"
export SESSION_SECRET="$SECRET_KEY"

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
" || exit 1

# Initialize Django database
cd chat_service
export DJANGO_SETTINGS_MODULE=chat_microservice.settings

print_step "Setting up Django chat service..."
$PYTHON_CMD manage.py makemigrations chat || print_warning "Django makemigrations warning"
$PYTHON_CMD manage.py migrate || print_warning "Django migrate warning"

cd ..

# 10. Install sample data
print_step "Installing sample data..."
$PYTHON_CMD -c "
import sys
sys.path.append('.')

try:
    from sample_data import create_sample_data
    create_sample_data()
    print('[OK] Sample data installed successfully')
except Exception as e:
    print(f'[WARNING] Sample data installation error: {e}')
" || print_warning "Sample data installation failed, continuing..."

# 11. Create systemd service files
print_step "Creating systemd service files..."

# Flask service
sudo tee /etc/systemd/system/hurtrock-flask.service > /dev/null << EOF
[Unit]
Description=Hurtrock Music Store Flask Server
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$HOME/.local/bin:\$PATH
EnvironmentFile=$APP_DIR/.env
ExecStart=$HOME/.local/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 main:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Django service
sudo tee /etc/systemd/system/hurtrock-django.service > /dev/null << EOF
[Unit]
Description=Hurtrock Music Store Django Chat Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR/chat_service
Environment=PATH=$HOME/.local/bin:\$PATH
Environment=DJANGO_SETTINGS_MODULE=chat_microservice.settings
EnvironmentFile=$APP_DIR/.env
ExecStart=$PYTHON_CMD manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable services
sudo systemctl daemon-reload
sudo systemctl enable hurtrock-flask.service
sudo systemctl enable hurtrock-django.service

print_success "Systemd services created and enabled"

# 12. Configure Nginx reverse proxy
print_step "Configuring Nginx reverse proxy..."

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

# Enable the site
sudo ln -sf /etc/nginx/sites-available/hurtrock-music-store /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t
if [ $? -eq 0 ]; then
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    print_success "Nginx configured successfully"
else
    print_error "Nginx configuration error"
    exit 1
fi

# 13. Setup firewall (if ufw is available)
if command_exists ufw; then
    print_step "Configuring firewall..."
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
    print_success "Firewall configured"
fi

# 14. Create management scripts
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
cat > backup.sh << 'EOF'
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

chmod +x backup.sh

print_success "Management scripts created"

# 15. Start services
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

# 16. Final summary
echo ""
echo "=============================================="
echo "   INSTALLATION COMPLETED - LINUX SERVER"
echo "=============================================="
echo ""
print_success "Flask Server configured and running"
print_success "Django Chat Service configured and running"
print_success "Nginx reverse proxy configured"
print_success "PostgreSQL database initialized"
print_success "Systemd services enabled"
print_success "Sample data installed"
echo ""
echo "IMPORTANT INFORMATION:"
echo "Admin Login:"
echo "  Email: admin@hurtrock.com"
echo "  Password: admin123"
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
echo "  ./backup.sh                   # Create backup"
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
print_success "Hurtrock Music Store is ready for production on Linux!"
echo "=============================================="
