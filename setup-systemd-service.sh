
#!/bin/bash

# Hurtrock Music Store - Systemd Service Setup Script
# Otomatis install dan konfigurasi service untuk auto-start dan auto-restart

set -e

SERVICE_NAME="hurtrock-music-store"
SERVICE_FILE="$SERVICE_NAME.service"
SYSTEMD_PATH="/etc/systemd/system"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$APP_DIR/service-setup.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Script ini harus dijalankan sebagai root (sudo)"
        exit 1
    fi
}

# Get the current user who called sudo
get_real_user() {
    if [ -n "$SUDO_USER" ]; then
        echo "$SUDO_USER"
    else
        echo "$USER"
    fi
}

# Create app user and group
create_app_user() {
    log "Membuat user dan group untuk aplikasi..."
    
    # Create system user
    if ! id "hurtrock" &>/dev/null; then
        useradd --system --no-create-home --shell /bin/false hurtrock
        log_success "User 'hurtrock' berhasil dibuat"
    else
        log_warning "User 'hurtrock' sudah ada"
    fi
    
    # Add current user to hurtrock group
    REAL_USER=$(get_real_user)
    usermod -a -G hurtrock "$REAL_USER"
}

# Setup application directory
setup_app_directory() {
    log "Setup direktori aplikasi..."
    
    # Create target directory
    TARGET_DIR="/opt/hurtrock-music-store"
    
    if [ ! -d "$TARGET_DIR" ]; then
        mkdir -p "$TARGET_DIR"
        log_success "Direktori $TARGET_DIR berhasil dibuat"
    fi
    
    # Copy application files
    log "Menyalin file aplikasi ke $TARGET_DIR..."
    cp -r "$APP_DIR"/* "$TARGET_DIR/"
    
    # Set ownership
    chown -R hurtrock:hurtrock "$TARGET_DIR"
    chmod -R 755 "$TARGET_DIR"
    
    # Make scripts executable
    chmod +x "$TARGET_DIR"/*.sh 2>/dev/null || true
    
    log_success "Aplikasi berhasil disalin ke $TARGET_DIR"
}

# Setup virtual environment
setup_venv() {
    TARGET_DIR="/opt/hurtrock-music-store"
    log "Setup Python virtual environment..."
    
    cd "$TARGET_DIR"
    
    # Create virtual environment as hurtrock user
    sudo -u hurtrock python3 -m venv .venv
    
    # Install dependencies
    sudo -u hurtrock .venv/bin/pip install --upgrade pip
    if [ -f "requirements.txt" ]; then
        sudo -u hurtrock .venv/bin/pip install -r requirements.txt
    fi
    
    log_success "Virtual environment setup selesai"
}

# Create and install systemd service
install_service() {
    log "Menginstall systemd service..."
    
    # Update service file with correct path
    sed -i "s|/opt/hurtrock-music-store|$(readlink -f /opt/hurtrock-music-store)|g" "$SERVICE_FILE"
    sed -i "s|User=www-data|User=hurtrock|g" "$SERVICE_FILE"
    sed -i "s|Group=www-data|Group=hurtrock|g" "$SERVICE_FILE"
    
    # Copy service file
    cp "$SERVICE_FILE" "$SYSTEMD_PATH/"
    
    # Set permissions
    chmod 644 "$SYSTEMD_PATH/$SERVICE_FILE"
    
    # Reload systemd
    systemctl daemon-reload
    
    log_success "Service file berhasil diinstall"
}

# Enable and start service
enable_service() {
    log "Mengaktifkan dan memulai service..."
    
    # Enable service for auto-start
    systemctl enable "$SERVICE_NAME"
    
    # Start service
    systemctl start "$SERVICE_NAME"
    
    # Check status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Service berhasil diaktifkan dan berjalan"
    else
        log_error "Service gagal distart"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

# Show service status
show_status() {
    echo ""
    echo "=============================================="
    echo "   🎸 HURTROCK MUSIC STORE SERVICE 🎸"
    echo "=============================================="
    echo ""
    
    # Service status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Service Status: RUNNING"
    else
        log_error "Service Status: STOPPED"
    fi
    
    if systemctl is-enabled --quiet "$SERVICE_NAME"; then
        log_success "Auto-start: ENABLED"
    else
        log_warning "Auto-start: DISABLED"
    fi
    
    echo ""
    echo "🌐 Aplikasi berjalan di:"
    echo "   📱 Website: http://0.0.0.0:5000"
    echo "   👨‍💼 Admin Panel: http://0.0.0.0:5000/admin"
    echo ""
    echo "⚡ Service Management Commands:"
    echo "   sudo systemctl start $SERVICE_NAME     # Start service"
    echo "   sudo systemctl stop $SERVICE_NAME      # Stop service"
    echo "   sudo systemctl restart $SERVICE_NAME   # Restart service"
    echo "   sudo systemctl status $SERVICE_NAME    # Check status"
    echo "   sudo systemctl enable $SERVICE_NAME    # Enable auto-start"
    echo "   sudo systemctl disable $SERVICE_NAME   # Disable auto-start"
    echo ""
    echo "📄 Logs:"
    echo "   journalctl -u $SERVICE_NAME -f         # Live logs"
    echo "   journalctl -u $SERVICE_NAME --since today  # Today's logs"
    echo ""
    echo "=============================================="
}

# Main installation process
main() {
    echo ""
    echo "🎸 Hurtrock Music Store - Service Installer"
    echo "==========================================="
    echo ""
    
    log "Memulai instalasi systemd service..."
    
    # Check requirements
    check_root
    
    if ! command -v systemctl >/dev/null 2>&1; then
        log_error "Systemd tidak tersedia di sistem ini"
        exit 1
    fi
    
    if [ ! -f "$SERVICE_FILE" ]; then
        log_error "File service $SERVICE_FILE tidak ditemukan"
        exit 1
    fi
    
    echo "Service ini akan:"
    echo "  ✅ Otomatis start saat sistem boot"
    echo "  ✅ Auto-restart jika aplikasi crash"
    echo "  ✅ Berjalan sebagai system service"
    echo "  ✅ Terintegrasi dengan systemd logging"
    echo ""
    
    read -p "Lanjutkan instalasi? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Instalasi dibatalkan."
        exit 0
    fi
    
    echo ""
    log "🚀 Memulai proses instalasi..."
    
    # Stop existing service if running
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        log "Menghentikan service yang sedang berjalan..."
        systemctl stop "$SERVICE_NAME"
    fi
    
    # Installation steps
    create_app_user
    setup_app_directory
    setup_venv
    install_service
    enable_service
    
    log_success "🎉 Instalasi service berhasil!"
    show_status
}

# Help function
show_help() {
    echo ""
    echo "🎸 Hurtrock Music Store - Service Installer"
    echo "==========================================="
    echo ""
    echo "Usage: sudo $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install       Install systemd service (default)"
    echo "  uninstall     Remove systemd service"
    echo "  status        Show service status"
    echo "  help          Show this help"
    echo ""
    echo "Examples:"
    echo "  sudo $0                    # Install service"
    echo "  sudo $0 install            # Install service"
    echo "  sudo $0 uninstall          # Remove service"
    echo "  sudo $0 status             # Show status"
    echo ""
}

# Uninstall service
uninstall_service() {
    log "Menghapus systemd service..."
    
    # Stop service
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        systemctl stop "$SERVICE_NAME"
    fi
    
    # Disable service
    if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
        systemctl disable "$SERVICE_NAME"
    fi
    
    # Remove service file
    if [ -f "$SYSTEMD_PATH/$SERVICE_FILE" ]; then
        rm "$SYSTEMD_PATH/$SERVICE_FILE"
    fi
    
    # Reload systemd
    systemctl daemon-reload
    
    log_success "Service berhasil dihapus"
}

# Command handling
case "${1:-install}" in
    "install")
        main
        ;;
    "uninstall")
        check_root
        uninstall_service
        ;;
    "status")
        show_status
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
