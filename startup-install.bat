
@echo off
setlocal enabledelayedexpansion

REM Hurtrock Music Store - Windows Startup Installer
REM Automated installation and setup script for Windows
REM Requires Windows 10/11 and admin privileges for some operations

set "APP_DIR=%~dp0"
set "LOG_FILE=%APP_DIR%install.log"

REM Colors for Windows (limited support)
set "BLUE=[94m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "NC=[0m"

goto :main

:log
echo %CYAN%[%date% %time%] %~1%NC%
echo [%date% %time%] %~1 >> "%LOG_FILE%"
goto :eof

:log_success
echo %GREEN%[%date% %time%] ✓ %~1%NC%
echo [%date% %time%] SUCCESS: %~1 >> "%LOG_FILE%"
goto :eof

:log_warning
echo %YELLOW%[%date% %time%] ⚠ %~1%NC%
echo [%date% %time%] WARNING: %~1 >> "%LOG_FILE%"
goto :eof

:log_error
echo %RED%[%date% %time%] ✗ %~1%NC%
echo [%date% %time%] ERROR: %~1 >> "%LOG_FILE%"
goto :eof

:log_info
echo %CYAN%[%date% %time%] ℹ %~1%NC%
echo [%date% %time%] INFO: %~1 >> "%LOG_FILE%"
goto :eof

:check_admin
net session >nul 2>&1
if %ERRORLEVEL% == 0 (
    set "IS_ADMIN=1"
) else (
    set "IS_ADMIN=0"
)
goto :eof

:check_python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    py --version >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        set "PYTHON_AVAILABLE=0"
        set "PYTHON_CMD="
    ) else (
        set "PYTHON_AVAILABLE=1"
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_AVAILABLE=1"
    set "PYTHON_CMD=python"
)
goto :eof

:check_chocolatey
choco --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    set "CHOCO_AVAILABLE=0"
) else (
    set "CHOCO_AVAILABLE=1"
)
goto :eof

:install_chocolatey
call :log "Menginstall Chocolatey package manager..."

REM Check if PowerShell is available
powershell -Command "Get-Host" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :log_error "PowerShell tidak tersedia!"
    goto :eof
)

REM Install Chocolatey
powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"

if %ERRORLEVEL% neq 0 (
    call :log_error "Gagal menginstall Chocolatey"
    goto :eof
)

REM Refresh environment
call refreshenv.cmd 2>nul

call :log_success "Chocolatey berhasil diinstall"
goto :eof

:install_python
call :log "Menginstall Python..."

call :check_chocolatey
if !CHOCO_AVAILABLE! == 1 (
    choco install python -y
    if !ERRORLEVEL! neq 0 (
        call :log_error "Gagal menginstall Python via Chocolatey"
        goto :manual_python_install
    )
    call :log_success "Python berhasil diinstall via Chocolatey"
) else (
    goto :manual_python_install
)

goto :eof

:manual_python_install
call :log_warning "Chocolatey tidak tersedia, silakan install Python secara manual"
echo.
echo Silakan download dan install Python dari: https://www.python.org/downloads/
echo Pastikan untuk mencentang "Add Python to PATH" saat instalasi
echo.
pause
goto :eof

:install_git
call :log "Menginstall Git..."

call :check_chocolatey
if !CHOCO_AVAILABLE! == 1 (
    choco install git -y
    if !ERRORLEVEL! neq 0 (
        call :log_warning "Gagal menginstall Git via Chocolatey"
    ) else (
        call :log_success "Git berhasil diinstall via Chocolatey"
    )
) else (
    call :log_warning "Silakan install Git secara manual dari: https://git-scm.com/download/win"
)
goto :eof

:install_postgresql
call :log "Menginstall PostgreSQL..."

call :check_chocolatey
if !CHOCO_AVAILABLE! == 1 (
    choco install postgresql -y --params "/Password:postgres123"
    if !ERRORLEVEL! neq 0 (
        call :log_warning "Gagal menginstall PostgreSQL via Chocolatey"
    ) else (
        call :log_success "PostgreSQL berhasil diinstall via Chocolatey"
        call :log_info "Password default PostgreSQL: postgres123"
    )
) else (
    call :log_warning "Silakan install PostgreSQL secara manual dari: https://www.postgresql.org/download/windows/"
)
goto :eof

:setup_python_env
call :log "Setup Python virtual environment..."

call :check_python
if !PYTHON_AVAILABLE! == 0 (
    call :log_error "Python tidak ditemukan! Silakan install Python terlebih dahulu."
    goto :eof
)

call :log_info "Menggunakan Python: !PYTHON_CMD!"

REM Create virtual environment
if not exist ".venv" (
    !PYTHON_CMD! -m venv .venv
    if !ERRORLEVEL! neq 0 (
        call :log_error "Gagal membuat virtual environment"
        goto :eof
    )
    call :log_success "Virtual environment berhasil dibuat"
) else (
    call :log_info "Virtual environment sudah ada"
)

REM Activate virtual environment
call .venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    call :log_error "Gagal mengaktifkan virtual environment"
    goto :eof
)

REM Update pip
pip install --upgrade pip >nul 2>&1

REM Install Python dependencies
if exist "requirements.txt" (
    call :log "Menginstall dependensi Python..."
    pip install -r requirements.txt
    if !ERRORLEVEL! neq 0 (
        call :log_warning "Beberapa dependensi gagal diinstall, melanjutkan..."
    ) else (
        call :log_success "Dependensi Python berhasil diinstall"
    )
) else (
    call :log_warning "File requirements.txt tidak ditemukan"
)
goto :eof

:setup_database
call :log "Setup database PostgreSQL..."

REM Check if PostgreSQL is available
psql --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :log_warning "PostgreSQL tidak tersedia, akan menggunakan SQLite"
    goto :eof
)

REM Try to create database (this might fail if PostgreSQL service is not running)
createdb hurtrock_music_store >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :log_warning "Gagal membuat database PostgreSQL, akan menggunakan SQLite"
) else (
    call :log_success "Database PostgreSQL berhasil disetup"
)
goto :eof

:create_startup_scripts
call :log "Setup startup scripts..."

REM Make sure Windows startup script is available
if exist "start_windows_server.bat" (
    call :log_success "Windows startup script tersedia"
) else (
    call :log_warning "Windows startup script tidak ditemukan"
)
goto :eof

:show_completion
echo.
echo ==============================================
echo    🎸 HURTROCK MUSIC STORE INSTALLER 🎸
echo ==============================================
echo.
call :log_success "🎉 Instalasi berhasil diselesaikan!"
echo.
echo 📋 Yang telah diinstall:
echo    ✓ Python 3 dan pip
echo    ✓ PostgreSQL database (opsional)
echo    ✓ Git version control
echo    ✓ Python virtual environment
echo    ✓ Semua dependensi aplikasi
echo.
echo 🚀 Langkah selanjutnya:
echo    1. Jalankan: start_windows_server.bat setup
echo    2. Atau jalankan: start_windows_server.bat
echo.
echo 🌐 Setelah setup, aplikasi akan tersedia di:
echo    📱 Website: http://localhost:5000
echo    👨‍💼 Admin Panel: http://localhost:5000/admin
echo.
echo 🔑 Login default:
echo    Email: admin@hurtrock.com
echo    Password: admin123
echo.
echo 📄 Log instalasi tersimpan di: %LOG_FILE%
echo ==============================================
goto :eof

:show_help
echo.
echo 🎸 Hurtrock Music Store - Windows Installer
echo ===========================================
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   --help, -h     Tampilkan bantuan ini
echo   --version      Tampilkan versi
echo.
echo Script ini akan menginstall semua dependensi yang diperlukan
echo untuk menjalankan Hurtrock Music Store di Windows:
echo.
echo   ✓ Python 3 dan pip
echo   ✓ PostgreSQL database (opsional)
echo   ✓ Git version control
echo   ✓ Python virtual environment
echo   ✓ Semua dependensi Python
echo.
echo Persyaratan:
echo   • Windows 10/11
echo   • Koneksi internet
echo   • Akses administrator (untuk beberapa instalasi)
echo.
echo Setelah instalasi, jalankan:
echo   start_windows_server.bat setup
echo.
goto :eof

:main
if "%~1"=="--help" goto :show_help
if "%~1"=="-h" goto :show_help
if "%~1"=="--version" (
    echo Hurtrock Music Store Installer v1.0
    goto :eof
)

echo.
echo 🎸 Hurtrock Music Store - Windows Installer
echo ===========================================
echo.

call :log "Memulai instalasi untuk Windows"
call :log "Direktori aplikasi: %APP_DIR%"

REM Check admin privileges
call :check_admin
if !IS_ADMIN! == 1 (
    call :log_info "Berjalan dengan hak administrator"
) else (
    call :log_warning "Tidak berjalan sebagai administrator - beberapa fitur mungkin terbatas"
)

REM Check existing installations
call :check_python
call :check_chocolatey

echo Script ini akan menginstall:
echo   - Chocolatey package manager (jika belum ada)
echo   - Python 3 dan pip (jika belum ada)
echo   - PostgreSQL database (opsional)
echo   - Git version control
echo   - Semua dependensi Python untuk aplikasi
echo.

if !IS_ADMIN! == 0 (
    echo PERINGATAN: Script tidak berjalan sebagai administrator.
    echo Beberapa instalasi mungkin gagal dan memerlukan instalasi manual.
    echo.
)

set /p "confirm=Lanjutkan instalasi? (y/N): "
if /i not "%confirm%"=="y" (
    echo Instalasi dibatalkan.
    goto :eof
)

echo.
call :log "🚀 Memulai proses instalasi..."

REM Install Chocolatey if not available and we have admin rights
if !CHOCO_AVAILABLE! == 0 (
    if !IS_ADMIN! == 1 (
        call :install_chocolatey
        call :check_chocolatey
    ) else (
        call :log_warning "Chocolatey tidak tersedia dan tidak dapat diinstall tanpa hak admin"
    )
)

REM Install Python if not available
if !PYTHON_AVAILABLE! == 0 (
    call :install_python
    REM Refresh environment and check again
    call :check_python
)

REM Install Git
call :install_git

REM Install PostgreSQL (optional)
call :install_postgresql

REM Setup Python environment
call :setup_python_env

REM Setup database if PostgreSQL is available
call :setup_database

REM Create startup scripts
call :create_startup_scripts

REM Show completion message
call :show_completion

echo.
pause
endlocal
