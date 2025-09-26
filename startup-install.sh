
#!/bin/bash

# Hurtrock Music Store - Universal Linux Startup Installer
# Automated installation and setup script for Linux distributions
# Supports Ubuntu, Debian, CentOS, RHEL, Fedora, openSUSE, and other distributions

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$APP_DIR/install.log"

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

# --- System Detection ---
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

detect_package_manager() {
    local distro=$(detect_linux_distro)
    case $distro in
        "ubuntu"|"debian"|"linuxmint"|"elementary")
            echo "apt"
            ;;
        "fedora"|"rhel"|"centos"|"rocky"|"almalinux")
            if command -v dnf >/dev/null 2>&1; then
                echo "dnf"
            else
                echo "yum"
            fi
            ;;
        "opensuse"|"sles")
            echo "zypper"
            ;;
        "arch"|"manjaro")
            echo "pacman"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# --- Update System ---
update_system() {
    local pkg_manager=$(detect_package_manager)
    log "Memperbarui sistem..."

    case $pkg_manager in
        "apt")
            sudo apt update && sudo apt upgrade -y
            ;;
        "dnf")
            sudo dnf update -y
            ;;
        "yum")
            sudo yum update -y
            ;;
        "zypper")
            sudo zypper refresh && sudo zypper update -y
            ;;
        "pacman")
            sudo pacman -Syu --noconfirm
            ;;
        *)
            log_warning "Package manager tidak dikenali, lewati update sistem"
            return 0
            ;;
    esac

    log_success "Sistem berhasil diperbarui"
}

# --- Install Python and Dependencies ---
install_python_deps() {
    local pkg_manager=$(detect_package_manager)
    log "Menginstall Python dan dependensi..."

    case $pkg_manager in
        "apt")
            sudo apt install -y python3 python3-pip python3-venv python3-dev \
                               build-essential curl wget git \
                               libffi-dev libssl-dev pkg-config \
                               libjpeg-dev zlib1g-dev \
                               python3-psycopg2
            ;;
        "dnf")
            sudo dnf install -y python3 python3-pip python3-devel \
                               gcc gcc-c++ make curl wget git \
                               libffi-devel openssl-devel pkgconfig \
                               libjpeg-turbo-devel zlib-devel \
                               python3-psycopg2
            ;;
        "yum")
            sudo yum install -y python3 python3-pip python3-devel \
                               gcc gcc-c++ make curl wget git \
                               libffi-devel openssl-devel pkgconfig \
                               libjpeg-turbo-devel zlib-devel \
                               python3-psycopg2
            ;;
        "zypper")
            sudo zypper install -y python3 python3-pip python3-devel \
                                  gcc gcc-c++ make curl wget git \
                                  libffi-devel libopenssl-devel pkg-config \
                                  libjpeg62-devel zlib-devel \
                                  python3-psycopg2
            ;;
        "pacman")
            sudo pacman -S --noconfirm python python-pip gcc make curl wget git \
                                       libffi openssl pkgconf \
                                       libjpeg-turbo zlib \
                                       python-psycopg2
            ;;
        *)
            log_error "Package manager tidak didukung!"
            return 1
            ;;
    esac

    log_success "Python dan dependensi berhasil diinstall"
}

# --- Install PostgreSQL ---
install_postgresql() {
    local pkg_manager=$(detect_package_manager)
    log "Menginstall PostgreSQL..."

    case $pkg_manager in
        "apt")
            sudo apt install -y postgresql postgresql-contrib
            ;;
        "dnf")
            sudo dnf install -y postgresql postgresql-server postgresql-contrib
            sudo postgresql-setup --initdb 2>/dev/null || sudo postgresql-setup initdb 2>/dev/null || true
            ;;
        "yum")
            sudo yum install -y postgresql postgresql-server postgresql-contrib
            sudo postgresql-setup initdb 2>/dev/null || true
            ;;
        "zypper")
            sudo zypper install -y postgresql postgresql-server postgresql-contrib
            ;;
        "pacman")
            sudo pacman -S --noconfirm postgresql
            sudo -u postgres initdb -D /var/lib/postgres/data 2>/dev/null || true
            ;;
        *)
            log_warning "Package manager tidak didukung untuk PostgreSQL"
            return 0
            ;;
    esac

    # Start and enable PostgreSQL
    sudo systemctl enable postgresql 2>/dev/null || true
    sudo systemctl start postgresql 2>/dev/null || true

    log_success "PostgreSQL berhasil diinstall"
}

# --- Install Redis (Optional) ---
install_redis() {
    local pkg_manager=$(detect_package_manager)
    log "Menginstall Redis (opsional)..."

    case $pkg_manager in
        "apt")
            sudo apt install -y redis-server
            ;;
        "dnf")
            sudo dnf install -y redis
            ;;
        "yum")
            sudo yum install -y redis
            ;;
        "zypper")
            sudo zypper install -y redis
            ;;
        "pacman")
            sudo pacman -S --noconfirm redis
            ;;
        *)
            log_warning "Package manager tidak didukung untuk Redis"
            return 0
            ;;
    esac

    # Start and enable Redis
    sudo systemctl enable redis 2>/dev/null || sudo systemctl enable redis-server 2>/dev/null || true
    sudo systemctl start redis 2>/dev/null || sudo systemctl start redis-server 2>/dev/null || true

    log_success "Redis berhasil diinstall"
}

# --- Setup Python Virtual Environment ---
setup_python_env() {
    log "Setup Python virtual environment..."

    # Detect Python command
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
    else
        log_error "Python tidak ditemukan!"
        return 1
    fi

    log_info "Menggunakan Python: $PYTHON_CMD"

    # Create virtual environment
    if [ ! -d ".venv" ]; then
        $PYTHON_CMD -m venv .venv
        log_success "Virtual environment berhasil dibuat"
    else
        log_info "Virtual environment sudah ada"
    fi

    # Activate virtual environment
    source .venv/bin/activate

    # Update pip
    pip install --upgrade pip

    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        log "Menginstall dependensi Python..."
        pip install -r requirements.txt
        log_success "Dependensi Python berhasil diinstall"
    else
        log_warning "File requirements.txt tidak ditemukan"
    fi
}

# --- Setup Database ---
setup_database() {
    log "Setup database PostgreSQL..."

    # Create database user
    sudo -u postgres createuser -s $USER 2>/dev/null || true
    sudo -u postgres psql -c "ALTER USER $USER WITH PASSWORD '$USER';" 2>/dev/null || true

    # Create database
    sudo -u postgres createdb hurtrock_music_store -O $USER 2>/dev/null || true

    log_success "Database PostgreSQL berhasil disetup"
}

# --- Create startup scripts if not exist ---
create_startup_scripts() {
    log "Membuat startup scripts..."

    # Make startup scripts executable
    chmod +x start_linux_server_universal.sh 2>/dev/null || true
    chmod +x start_arch_server.sh 2>/dev/null || true

    log_success "Startup scripts berhasil disetup"
}

# --- Display completion message ---
show_completion() {
    echo ""
    echo "=============================================="
    echo "   🎸 HURTROCK MUSIC STORE INSTALLER 🎸"
    echo "=============================================="
    echo ""
    log_success "🎉 Instalasi berhasil diselesaikan!"
    echo ""
    echo "📋 Yang telah diinstall:"
    echo "   ✓ Python 3 dan dependensi"
    echo "   ✓ PostgreSQL database"
    echo "   ✓ Redis server (opsional)"
    echo "   ✓ Python virtual environment"
    echo "   ✓ Semua dependensi aplikasi"
    echo ""
    echo "🚀 Langkah selanjutnya:"
    echo "   1. Jalankan: ./start_linux_server_universal.sh setup"
    echo "   2. Atau jalankan: ./start_linux_server_universal.sh"
    echo ""
    echo "🌐 Setelah setup, aplikasi akan tersedia di:"
    echo "   📱 Website: http://0.0.0.0:5000"
    echo "   👨‍💼 Admin Panel: http://0.0.0.0:5000/admin"
    echo ""
    echo "🔑 Login default:"
    echo "   Email: admin@hurtrock.com"
    echo "   Password: admin123"
    echo ""
    echo "📄 Log instalasi tersimpan di: $LOG_FILE"
    echo "=============================================="
}

# --- Main Installation Process ---
main() {
    echo ""
    echo "🎸 Hurtrock Music Store - Linux Installer"
    echo "=========================================="
    echo ""

    local distro=$(detect_linux_distro)
    local pkg_manager=$(detect_package_manager)

    log "Memulai instalasi untuk $distro (menggunakan $pkg_manager)"
    log "Direktori aplikasi: $APP_DIR"

    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        log_error "Jangan jalankan script ini sebagai root!"
        echo "Gunakan: ./startup-install.sh"
        exit 1
    fi

    # Check sudo access
    if ! sudo -n true 2>/dev/null; then
        log "Script ini memerlukan akses sudo untuk menginstall package sistem"
        echo "Silakan masukkan password sudo ketika diminta..."
        sudo true || {
            log_error "Akses sudo diperlukan untuk instalasi"
            exit 1
        }
    fi

    # Ask for confirmation
    echo "Script ini akan menginstall:"
    echo "  - Python 3 dan dependensi development"
    echo "  - PostgreSQL database server"
    echo "  - Redis server (opsional)"
    echo "  - Semua dependensi Python untuk aplikasi"
    echo ""
    read -p "Lanjutkan instalasi? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Instalasi dibatalkan."
        exit 0
    fi

    echo ""
    log "🚀 Memulai proses instalasi..."

    # Update system
    update_system || {
        log_error "Gagal update sistem"
        exit 1
    }

    # Install Python and dependencies
    install_python_deps || {
        log_error "Gagal install Python dependencies"
        exit 1
    }

    # Install PostgreSQL
    install_postgresql || {
        log_warning "PostgreSQL gagal diinstall, lanjutkan dengan SQLite"
    }

    # Install Redis (optional)
    install_redis || {
        log_warning "Redis gagal diinstall (opsional)"
    }

    # Setup Python environment
    setup_python_env || {
        log_error "Gagal setup Python environment"
        exit 1
    }

    # Setup database
    if command -v psql >/dev/null 2>&1; then
        setup_database || {
            log_warning "Database setup gagal, akan menggunakan SQLite"
        }
    else
        log_info "PostgreSQL tidak tersedia, akan menggunakan SQLite"
    fi

    # Create startup scripts
    create_startup_scripts

    # Show completion message
    show_completion
}

# --- Signal handler ---
cleanup() {
    echo ""
    log "Instalasi dibatalkan oleh user"
    exit 1
}

trap cleanup SIGINT SIGTERM

# --- Help function ---
show_help() {
    echo ""
    echo "🎸 Hurtrock Music Store - Linux Installer"
    echo "========================================="
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h     Tampilkan bantuan ini"
    echo "  --version      Tampilkan versi"
    echo ""
    echo "Script ini akan menginstall semua dependensi yang diperlukan"
    echo "untuk menjalankan Hurtrock Music Store di Linux:"
    echo ""
    echo "  ✓ Python 3 dan pip"
    echo "  ✓ PostgreSQL database"
    echo "  ✓ Redis server"
    echo "  ✓ Build tools dan libraries"
    echo "  ✓ Python virtual environment"
    echo "  ✓ Semua dependensi Python"
    echo ""
    echo "Distribusi yang didukung:"
    echo "  • Ubuntu / Debian"
    echo "  • CentOS / RHEL / Fedora"
    echo "  • openSUSE / SLES"
    echo "  • Arch Linux / Manjaro"
    echo ""
    echo "Setelah instalasi, jalankan:"
    echo "  ./start_linux_server_universal.sh setup"
    echo ""
}

# --- Command line argument parsing ---
case "${1:-}" in
    "--help"|"-h")
        show_help
        exit 0
        ;;
    "--version")
        echo "Hurtrock Music Store Installer v1.0"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
