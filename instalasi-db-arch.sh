
#!/bin/bash

# Hurtrock Music Store - Arch Linux Database Configuration Script
# Script khusus untuk konfigurasi database PostgreSQL dan Valkey di Arch Linux

echo "[START] Configuring database for Hurtrock Music Store on Arch Linux..."

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

# Database configuration
DB_NAME="hurtrock_music_store"
DB_USER="fajar"
DB_PASS="fajar"
DB_HOST="localhost"
DB_PORT="5432"

# 1. Check if PostgreSQL is installed
print_step "Checking PostgreSQL installation..."
if ! command_exists psql; then
    print_error "PostgreSQL is not installed. Please run instalasi-arch-server.sh first."
    exit 1
fi

print_success "PostgreSQL found"

# 2. Check if PostgreSQL service is running
print_step "Checking PostgreSQL service status..."
if ! sudo systemctl is-active --quiet postgresql.service; then
    print_step "Starting PostgreSQL service..."
    sudo systemctl start postgresql.service
    if [ $? -eq 0 ]; then
        print_success "PostgreSQL service started"
    else
        print_error "Failed to start PostgreSQL service"
        exit 1
    fi
else
    print_success "PostgreSQL service is running"
fi

# 3. Configure PostgreSQL
print_step "Configuring PostgreSQL..."

# Check if database exists
DB_EXISTS=$(sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -w $DB_NAME | wc -l)

if [ $DB_EXISTS -eq 0 ]; then
    print_step "Creating database $DB_NAME..."
    
    # Create database and user
    sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASS';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
ALTER USER $DB_USER SUPERUSER;
\q
EOF

    if [ $? -eq 0 ]; then
        print_success "Database $DB_NAME created successfully"
    else
        print_error "Failed to create database"
        exit 1
    fi
else
    print_warning "Database $DB_NAME already exists"
    
    # Update user password
    sudo -u postgres psql << EOF
ALTER USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASS';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
ALTER USER $DB_USER SUPERUSER;
\q
EOF

    print_success "Database user updated"
fi

# 4. Configure PostgreSQL for local connections
print_step "Configuring PostgreSQL authentication..."

PG_VERSION=$(sudo -u postgres psql -c "SELECT version();" | grep -oP '\d+\.\d+' | head -1)
PG_CONFIG_DIR="/var/lib/postgres/data"
PG_HBA_FILE="$PG_CONFIG_DIR/pg_hba.conf"
POSTGRESQL_CONF="$PG_CONFIG_DIR/postgresql.conf"

# Backup original files
sudo cp $PG_HBA_FILE $PG_HBA_FILE.backup
sudo cp $POSTGRESQL_CONF $POSTGRESQL_CONF.backup

# Update pg_hba.conf for local connections
sudo tee $PG_HBA_FILE > /dev/null << 'EOF'
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust
local   all             postgres                                peer

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5

# Allow replication connections from localhost
local   replication     all                                     peer
host    replication     all             127.0.0.1/32            md5
host    replication     all             ::1/128                 md5
EOF

# Update postgresql.conf
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" $POSTGRESQL_CONF
sudo sed -i "s/#port = 5432/port = 5432/" $POSTGRESQL_CONF
sudo sed -i "s/#max_connections = 100/max_connections = 200/" $POSTGRESQL_CONF
sudo sed -i "s/#shared_buffers = 128MB/shared_buffers = 256MB/" $POSTGRESQL_CONF

print_success "PostgreSQL configuration updated"

# 5. Restart PostgreSQL service
print_step "Restarting PostgreSQL service..."
sudo systemctl restart postgresql.service
if [ $? -eq 0 ]; then
    print_success "PostgreSQL service restarted"
else
    print_error "Failed to restart PostgreSQL service"
    exit 1
fi

# Wait for PostgreSQL to start
sleep 3

# 6. Test database connection
print_step "Testing database connection..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Database connection test successful"
else
    print_error "Database connection test failed"
    exit 1
fi

# 7. Setup Valkey/Redis
print_step "Configuring cache service..."

if command_exists valkey-server; then
    CACHE_SERVICE="valkey"
    CACHE_CONFIG="/etc/valkey/valkey.conf"
    SERVICE_NAME="valkey.service"
elif command_exists redis-server; then
    CACHE_SERVICE="redis"
    CACHE_CONFIG="/etc/redis/redis.conf"
    SERVICE_NAME="redis.service"
else
    print_error "Neither Valkey nor Redis is installed"
    exit 1
fi

print_step "Configuring $CACHE_SERVICE..."

# Configure cache service
if [ -f "$CACHE_CONFIG" ]; then
    sudo cp $CACHE_CONFIG $CACHE_CONFIG.backup
    
    # Update configuration
    sudo sed -i 's/^bind 127.0.0.1 ::1/bind 127.0.0.1/' $CACHE_CONFIG
    sudo sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' $CACHE_CONFIG
    sudo sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' $CACHE_CONFIG
    
    print_success "$CACHE_SERVICE configuration updated"
fi

# Start cache service
if ! sudo systemctl is-active --quiet $SERVICE_NAME; then
    sudo systemctl start $SERVICE_NAME
    if [ $? -eq 0 ]; then
        print_success "$CACHE_SERVICE service started"
    else
        print_error "Failed to start $CACHE_SERVICE service"
        exit 1
    fi
else
    print_success "$CACHE_SERVICE service is already running"
fi

# Enable service
sudo systemctl enable $SERVICE_NAME

# 8. Create Django settings configuration
print_step "Creating Django database configuration..."

DJANGO_SETTINGS_DIR="chat_service/chat_microservice"
if [ -d "$DJANGO_SETTINGS_DIR" ]; then
    cat > $DJANGO_SETTINGS_DIR/database_settings.py << EOF
# Database configuration for Arch Linux deployment
# This file contains the database settings for Django

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '$DB_NAME',
        'USER': '$DB_USER',
        'PASSWORD': '$DB_PASS',
        'HOST': '$DB_HOST',
        'PORT': '$DB_PORT',
        'OPTIONS': {
            'sslmode': 'prefer',
        },
        'CONN_MAX_AGE': 60,
        'CONN_HEALTH_CHECKS': True,
    }
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
EOF

    print_success "Django database configuration created"
fi

# 9. Create Flask database configuration
print_step "Creating Flask database configuration..."

cat > database_config.py << EOF
# Database configuration for Arch Linux deployment
# This file contains the database settings for Flask

import os

# PostgreSQL configuration
DATABASE_CONFIG = {
    'name': '$DB_NAME',
    'user': '$DB_USER',
    'password': '$DB_PASS',
    'host': '$DB_HOST',
    'port': '$DB_PORT'
}

# Build database URL
DATABASE_URL = f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['name']}"

# Cache configuration
CACHE_CONFIG = {
    'type': '$CACHE_SERVICE',
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0
}

# Build cache URL
if CACHE_CONFIG['type'] == 'valkey':
    CACHE_URL = f"redis://{CACHE_CONFIG['host']}:{CACHE_CONFIG['port']}/{CACHE_CONFIG['db']}"
else:
    CACHE_URL = f"redis://{CACHE_CONFIG['host']}:{CACHE_CONFIG['port']}/{CACHE_CONFIG['db']}"

# Export environment variables
os.environ.setdefault('DATABASE_URL', DATABASE_URL)
os.environ.setdefault('CACHE_URL', CACHE_URL)
EOF

print_success "Flask database configuration created"

# 10. Create database management scripts
print_step "Creating database management scripts..."

# Database backup script
cat > backup-database.sh << EOF
#!/bin/bash

# Hurtrock Music Store - Database Backup Script for Arch Linux

BACKUP_DIR="/var/backups/hurtrock/database"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

echo "Creating database backup..."

# PostgreSQL backup
PGPASSWORD='$DB_PASS' pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME > \$BACKUP_DIR/postgresql_\$DATE.sql

if [ \$? -eq 0 ]; then
    echo "PostgreSQL backup created: \$BACKUP_DIR/postgresql_\$DATE.sql"
    
    # Compress backup
    gzip \$BACKUP_DIR/postgresql_\$DATE.sql
    echo "Backup compressed: \$BACKUP_DIR/postgresql_\$DATE.sql.gz"
else
    echo "PostgreSQL backup failed"
    exit 1
fi

# Keep only last 7 backups
find \$BACKUP_DIR -name "postgresql_*.sql.gz" -type f -mtime +7 -delete

echo "Database backup completed successfully"
EOF

chmod +x backup-database.sh

# Database restore script
cat > restore-database.sh << EOF
#!/bin/bash

# Hurtrock Music Store - Database Restore Script for Arch Linux

if [ \$# -eq 0 ]; then
    echo "Usage: \$0 <backup_file.sql.gz>"
    echo "Available backups:"
    ls -la /var/backups/hurtrock/database/postgresql_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="\$1"

if [ ! -f "\$BACKUP_FILE" ]; then
    echo "Backup file not found: \$BACKUP_FILE"
    exit 1
fi

echo "Restoring database from: \$BACKUP_FILE"

# Extract if compressed
if [[ \$BACKUP_FILE == *.gz ]]; then
    SQL_FILE="\${BACKUP_FILE%.gz}"
    gunzip -c "\$BACKUP_FILE" > "\$SQL_FILE"
else
    SQL_FILE="\$BACKUP_FILE"
fi

# Drop and recreate database
sudo -u postgres psql << EOL
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\\q
EOL

# Restore data
PGPASSWORD='$DB_PASS' psql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME < "\$SQL_FILE"

if [ \$? -eq 0 ]; then
    echo "Database restored successfully"
    
    # Clean up temporary SQL file if it was extracted
    if [[ \$BACKUP_FILE == *.gz ]]; then
        rm "\$SQL_FILE"
    fi
else
    echo "Database restore failed"
    exit 1
fi
EOF

chmod +x restore-database.sh

# Database status script
cat > check-database.sh << EOF
#!/bin/bash

# Hurtrock Music Store - Database Status Check Script for Arch Linux

echo "=============================================="
echo "   DATABASE STATUS CHECK"
echo "=============================================="
echo ""

# Check PostgreSQL service
echo "PostgreSQL Service Status:"
sudo systemctl status postgresql.service --no-pager -l

echo ""
echo "PostgreSQL Connection Test:"
PGPASSWORD='$DB_PASS' psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT version();" 2>/dev/null
if [ \$? -eq 0 ]; then
    echo "✓ PostgreSQL connection successful"
else
    echo "✗ PostgreSQL connection failed"
fi

echo ""
echo "Database Information:"
PGPASSWORD='$DB_PASS' psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
SELECT 
    pg_size_pretty(pg_database_size('$DB_NAME')) as database_size,
    (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public') as table_count;
"

echo ""
echo "$CACHE_SERVICE Service Status:"
sudo systemctl status $SERVICE_NAME --no-pager -l

echo ""
echo "$CACHE_SERVICE Connection Test:"
if command_exists redis-cli; then
    redis-cli ping 2>/dev/null
    if [ \$? -eq 0 ]; then
        echo "✓ $CACHE_SERVICE connection successful"
    else
        echo "✗ $CACHE_SERVICE connection failed"
    fi
fi

echo ""
echo "=============================================="
EOF

chmod +x check-database.sh

print_success "Database management scripts created"

# 11. Test all connections
print_step "Running final connectivity tests..."

# Test PostgreSQL
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT 'PostgreSQL connection successful' as status;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "PostgreSQL connection test passed"
else
    print_error "PostgreSQL connection test failed"
fi

# Test cache service
if command_exists redis-cli; then
    redis-cli ping > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_success "$CACHE_SERVICE connection test passed"
    else
        print_warning "$CACHE_SERVICE connection test failed"
    fi
fi

# 12. Final summary
echo ""
echo "=============================================="
echo "   DATABASE CONFIGURATION COMPLETED"
echo "=============================================="
echo ""
print_success "PostgreSQL database configured"
print_success "$CACHE_SERVICE cache service configured"
print_success "Database management scripts created"
echo ""
echo "DATABASE INFORMATION:"
echo "  Database Name: $DB_NAME"
echo "  Database User: $DB_USER"
echo "  Database Password: $DB_PASS"
echo "  Database Host: $DB_HOST"
echo "  Database Port: $DB_PORT"
echo ""
echo "DJANGO SETTINGS:"
echo "DATABASES = {"
echo "    'default': {"
echo "        'ENGINE': 'django.db.backends.postgresql',"
echo "        'NAME': '$DB_NAME',"
echo "        'USER': '$DB_USER',"
echo "        'PASSWORD': '$DB_PASS',"
echo "        'HOST': '$DB_HOST',"
echo "        'PORT': '$DB_PORT',"
echo "    }"
echo "}"
echo ""
echo "DATABASE MANAGEMENT COMMANDS:"
echo "  ./backup-database.sh          # Create database backup"
echo "  ./restore-database.sh <file>  # Restore database"
echo "  ./check-database.sh           # Check database status"
echo ""
echo "SERVICE MANAGEMENT:"
echo "  sudo systemctl status postgresql.service"
echo "  sudo systemctl status $SERVICE_NAME"
echo "  sudo systemctl restart postgresql.service"
echo "  sudo systemctl restart $SERVICE_NAME"
echo ""
print_success "Database configuration completed successfully!"
echo "=============================================="
