
@echo off
setlocal enabledelayedexpansion

REM Hurtrock Music Store - Windows Service Setup Script

set "APP_DIR=%~dp0"
set "SERVICE_SCRIPT=%APP_DIR%hurtrock-service.py"
set "PYTHON_CMD=python"

REM Colors (limited Windows support)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "NC=[0m"

goto :main

:log
echo %BLUE%[%date% %time%] %~1%NC%
goto :eof

:log_success
echo %GREEN%[%date% %time%] ✓ %~1%NC%
goto :eof

:log_warning
echo %YELLOW%[%date% %time%] ⚠ %~1%NC%
goto :eof

:log_error
echo %RED%[%date% %time%] ✗ %~1%NC%
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
    ) else (
        set "PYTHON_CMD=py"
        set "PYTHON_AVAILABLE=1"
    )
) else (
    set "PYTHON_AVAILABLE=1"
)
goto :eof

:install_pywin32
call :log "Menginstall pywin32..."
%PYTHON_CMD% -m pip install pywin32
if %ERRORLEVEL% neq 0 (
    call :log_error "Gagal menginstall pywin32"
    exit /b 1
)
call :log_success "pywin32 berhasil diinstall"
goto :eof

:install_service
call :log "Menginstall Windows Service..."

REM Check admin rights
call :check_admin
if !IS_ADMIN! == 0 (
    call :log_error "Script harus dijalankan sebagai Administrator!"
    echo Klik kanan dan pilih "Run as administrator"
    pause
    exit /b 1
)

REM Check Python
call :check_python
if !PYTHON_AVAILABLE! == 0 (
    call :log_error "Python tidak ditemukan!"
    exit /b 1
)

REM Install pywin32 if needed
%PYTHON_CMD% -c "import win32serviceutil" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :install_pywin32
)

REM Install service
call :log "Menginstall service..."
%PYTHON_CMD% "%SERVICE_SCRIPT%" install
if %ERRORLEVEL% neq 0 (
    call :log_error "Gagal menginstall service"
    exit /b 1
)

call :log_success "Service berhasil diinstall!"
goto :eof

:start_service
call :log "Memulai service..."
%PYTHON_CMD% "%SERVICE_SCRIPT%" start
goto :eof

:stop_service
call :log "Menghentikan service..."
%PYTHON_CMD% "%SERVICE_SCRIPT%" stop
goto :eof

:uninstall_service
call :log "Menghapus service..."

call :check_admin
if !IS_ADMIN! == 0 (
    call :log_error "Script harus dijalankan sebagai Administrator!"
    pause
    exit /b 1
)

%PYTHON_CMD% "%SERVICE_SCRIPT%" uninstall
call :log_success "Service berhasil dihapus!"
goto :eof

:show_status
echo.
echo ==============================================
echo    🎸 HURTROCK MUSIC STORE SERVICE 🎸
echo ==============================================
echo.

%PYTHON_CMD% "%SERVICE_SCRIPT%" status

echo.
echo 🌐 Aplikasi berjalan di:
echo    📱 Website: http://localhost:5000
echo    👨‍💼 Admin Panel: http://localhost:5000/admin
echo.
echo ⚡ Service Management Commands:
echo    %~nx0 start      # Start service
echo    %~nx0 stop       # Stop service
echo    %~nx0 status     # Check status
echo    %~nx0 install    # Install service
echo    %~nx0 uninstall  # Remove service
echo.
echo 📄 Logs tersimpan di: logs\service.log
echo ==============================================
goto :eof

:show_help
echo.
echo 🎸 Hurtrock Music Store - Windows Service Setup
echo ==============================================
echo.
echo Usage: %~nx0 [COMMAND]
echo.
echo Commands:
echo   install       Install Windows Service
echo   uninstall     Remove Windows Service
echo   start         Start service
echo   stop          Stop service
echo   status        Show service status
echo   help          Show this help
echo.
echo Examples:
echo   %~nx0 install    # Install service (requires admin)
echo   %~nx0 start      # Start service
echo   %~nx0 status     # Check status
echo.
echo Service Features:
echo   ✅ Auto-start saat Windows boot
echo   ✅ Auto-restart jika aplikasi crash
echo   ✅ Berjalan di background
echo   ✅ Windows Event Log integration
echo.
echo Requirements:
echo   • Python 3.x
echo   • pip install pywin32
echo   • Administrator rights (untuk install/uninstall)
echo.
goto :eof

:main
if "%~1"=="" goto :install_and_start
if /i "%~1"=="install" goto :install_service
if /i "%~1"=="uninstall" goto :uninstall_service
if /i "%~1"=="start" goto :start_service
if /i "%~1"=="stop" goto :stop_service
if /i "%~1"=="status" goto :show_status
if /i "%~1"=="help" goto :show_help
if /i "%~1"=="--help" goto :show_help
if /i "%~1"=="-h" goto :show_help

echo Unknown command: %~1
echo.
goto :show_help

:install_and_start
echo.
echo 🎸 Hurtrock Music Store - Service Setup
echo ======================================
echo.

call :check_admin
if !IS_ADMIN! == 0 (
    echo ⚠️  Script ini memerlukan hak Administrator untuk install service.
    echo.
    echo Pilihan:
    echo 1) Install sebagai Windows Service (Recommended)
    echo 2) Setup manual startup script saja
    echo.
    choice /c 12 /m "Pilih opsi"
    if !ERRORLEVEL! == 1 (
        echo.
        echo Silakan jalankan ulang script ini sebagai Administrator:
        echo 1. Klik kanan pada %~nx0
        echo 2. Pilih "Run as administrator"
        pause
        exit /b 1
    ) else (
        call :log "Setup manual startup script..."
        echo File startup sudah tersedia: start_windows_server.bat
        call :log_success "Setup selesai!"
        pause
        exit /b 0
    )
)

echo Script ini akan:
echo   ✅ Install Windows Service
echo   ✅ Konfigurasi auto-start saat boot
echo   ✅ Setup auto-restart jika crash
echo   ✅ Integrasi dengan Windows Event Log
echo.

choice /c YN /m "Lanjutkan instalasi"
if !ERRORLEVEL! == 2 (
    echo Instalasi dibatalkan.
    exit /b 0
)

echo.
call :log "🚀 Memulai instalasi service..."

call :install_service
if %ERRORLEVEL% neq 0 exit /b 1

call :start_service

echo.
call :log_success "🎉 Service berhasil diinstall dan distart!"
call :show_status

echo.
pause
endlocal
