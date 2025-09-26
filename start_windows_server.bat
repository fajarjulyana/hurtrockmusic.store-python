
@echo off
setlocal enabledelayedexpansion

REM Hurtrock Music Store - Windows Server Startup Script
REM Complete setup with manual .env configuration and database support

set "APP_DIR=%~dp0"
set "VENV_DIR=%APP_DIR%.venv"
set "ENV_FILE=%APP_DIR%.env"
set "LOG_FILE=%APP_DIR%hurtrock.log"
set "PID_FILE=%APP_DIR%app.pid"
set "DJANGO_PID_FILE=%APP_DIR%django.pid"

REM Colors for Windows (limited support)
set "BLUE=[94m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

goto :main

:log
echo %BLUE%[%date% %time%] %~1%NC%
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

:check_python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    py --version >nul 2>&1
    if !ERRORLEVEL! neq 0 (
        call :log_error "Python not found. Please install Python 3.x from python.org"
        exit /b 1
    ) else (
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_CMD=python"
)
goto :eof

:check_port
netstat -an | find ":%~1 " >nul 2>&1
if %ERRORLEVEL% equ 0 (
    exit /b 1
) else (
    exit /b 0
)

:generate_secret
for /f %%i in ('powershell -command "[System.Web.Security.Membership]::GeneratePassword(32, 0)"') do set "SECRET=%%i"
echo !SECRET!
goto :eof

:setup_environment
call :log "Setting up Python environment..."

call :check_python
if %ERRORLEVEL% neq 0 exit /b 1

call :log_success "Using Python command: %PYTHON_CMD%"

REM Create virtual environment if not exists
if not exist "%VENV_DIR%" (
    call :log "Creating virtual environment..."
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if !ERRORLEVEL! neq 0 (
        call :log_error "Failed to create virtual environment"
        exit /b 1
    )
)

REM Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    call :log_error "Failed to activate virtual environment"
    exit /b 1
)

REM Update pip
pip install --upgrade pip >nul 2>&1

REM Install requirements
if exist "requirements.txt" (
    call :log "Installing Python dependencies..."
    pip install -r requirements.txt --no-cache-dir
    if !ERRORLEVEL! neq 0 (
        call :log_warning "Some dependencies failed to install, continuing..."
    )
)

call :log_success "Environment setup completed"
goto :eof

:interactive_database_setup
echo.
echo 🗄️  Database Configuration
echo =========================
echo.
echo Choose database type:
echo 1) SQLite (Recommended for Windows)
echo 2) PostgreSQL (Requires manual setup)
echo.
set /p "db_choice=Enter choice (1-2) [default: 1]: "

if "%db_choice%"=="2" (
    echo.
    echo PostgreSQL Configuration:
    set /p "db_host=Database host [localhost]: "
    if "!db_host!"=="" set "db_host=localhost"
    
    set /p "db_port=Database port [5432]: "
    if "!db_port!"=="" set "db_port=5432"
    
    set /p "db_name=Database name [hurtrock_music_store]: "
    if "!db_name!"=="" set "db_name=hurtrock_music_store"
    
    set /p "db_user=Database user [postgres]: "
    if "!db_user!"=="" set "db_user=postgres"
    
    set /p "db_password=Database password: "
    
    set "DATABASE_URL=postgresql://!db_user!:!db_password!@!db_host!:!db_port!/!db_name!"
    call :log "Using PostgreSQL database: !db_host!:!db_port!/!db_name!"
) else (
    set "DATABASE_URL=sqlite:///%APP_DIR%hurtrock.db"
    call :log "Using SQLite database"
)
goto :eof

:interactive_server_setup
echo.
echo 🌐 Server Configuration
echo ======================
set /p "flask_host=Flask host [0.0.0.0]: "
if "%flask_host%"=="" set "flask_host=0.0.0.0"

set /p "flask_port=Flask port [5000]: "
if "%flask_port%"=="" set "flask_port=5000"

set /p "django_port=Django port [8000]: "
if "%django_port%"=="" set "django_port=8000"

echo.
echo Environment type:
echo 1) Development (Debug enabled)
echo 2) Production (Debug disabled)
set /p "env_type=Choose (1-2) [default: 1]: "

if "%env_type%"=="2" (
    set "FLASK_ENV=production"
    set "FLASK_DEBUG=0"
    set "IS_PRODUCTION=true"
    set "DJANGO_DEBUG=0"
) else (
    set "FLASK_ENV=development"
    set "FLASK_DEBUG=1"
    set "IS_PRODUCTION=false"
    set "DJANGO_DEBUG=1"
)
goto :eof

:interactive_payment_setup
echo.
echo 💳 Payment Configuration
echo ========================
echo Configure payment gateways (you can skip and configure later in admin panel):
echo.

echo Stripe Configuration:
set /p "stripe_pub_key=Stripe Publishable Key (optional): "
set /p "stripe_secret_key=Stripe Secret Key (optional): "

echo.
echo Midtrans Configuration:
set /p "midtrans_client_key=Midtrans Client Key (optional): "
set /p "midtrans_server_key=Midtrans Server Key (optional): "

REM Set defaults if empty
if "%stripe_pub_key%"=="" set "stripe_pub_key=pk_test_your_stripe_publishable_key_here"
if "%stripe_secret_key%"=="" set "stripe_secret_key=sk_test_your_stripe_secret_key_here"
if "%midtrans_client_key%"=="" set "midtrans_client_key=your_midtrans_client_key_here"
if "%midtrans_server_key%"=="" set "midtrans_server_key=your_midtrans_server_key_here"
goto :eof

:interactive_contact_setup
echo.
echo 📞 Contact Information
echo =====================
set /p "store_email=Store Email [info@hurtrock.com]: "
if "%store_email%"=="" set "store_email=info@hurtrock.com"

set /p "whatsapp_number=WhatsApp Number (e.g., 6282115558035): "
if "%whatsapp_number%"=="" set "whatsapp_number=6282115558035"

set /p "store_phone=Store Phone [0821-1555-8035]: "
if "%store_phone%"=="" set "store_phone=0821-1555-8035"
goto :eof

:setup_env_file
if not exist "%ENV_FILE%" (
    call :log "Creating .env configuration..."
    
    REM Interactive setup
    call :interactive_database_setup
    call :interactive_server_setup
    call :interactive_payment_setup
    call :interactive_contact_setup
    
    REM Generate secrets
    call :log "Generating security keys..."
    call :generate_secret
    set "SESSION_SECRET=!SECRET!"
    call :generate_secret
    set "DJANGO_SECRET_KEY=!SECRET!"
    call :generate_secret
    set "JWT_SECRET_KEY=!SECRET!"

    REM Create .env file
    (
        echo # Hurtrock Music Store Configuration
        echo # Generated on %date% %time%
        echo.
        echo # Database Configuration
        echo DATABASE_URL='!DATABASE_URL!'
        echo.
        echo # Security Keys (Keep these secret!)
        echo SESSION_SECRET='!SESSION_SECRET!'
        echo DJANGO_SECRET_KEY='!DJANGO_SECRET_KEY!'
        echo JWT_SECRET_KEY='!JWT_SECRET_KEY!'
        echo.
        echo # Flask Configuration
        echo FLASK_ENV=!FLASK_ENV!
        echo FLASK_DEBUG=!FLASK_DEBUG!
        echo IS_PRODUCTION=!IS_PRODUCTION!
        echo FLASK_HOST=!flask_host!
        echo FLASK_PORT=!flask_port!
        echo.
        echo # Django Configuration
        echo DJANGO_HOST=!flask_host!
        echo DJANGO_PORT=!django_port!
        echo DJANGO_DEBUG=!DJANGO_DEBUG!
        echo.
        echo # Cache Configuration (Redis - optional)
        echo REDIS_URL=redis://localhost:6379/0
        echo.
        echo # Payment Configuration
        echo STRIPE_PUBLISHABLE_KEY=!stripe_pub_key!
        echo STRIPE_SECRET_KEY=!stripe_secret_key!
        echo MIDTRANS_SERVER_KEY=!midtrans_server_key!
        echo MIDTRANS_CLIENT_KEY=!midtrans_client_key!
        echo.
        echo # Email Configuration (SMTP - optional)
        echo MAIL_SERVER=smtp.gmail.com
        echo MAIL_PORT=587
        echo MAIL_USE_TLS=True
        echo MAIL_USERNAME=!store_email!
        echo MAIL_PASSWORD=your_app_password
        echo.
        echo # Domain Configuration
        echo DOMAINS=localhost,127.0.0.1,0.0.0.0,!flask_host!
        echo.
        echo # Contact Information
        echo STORE_EMAIL=!store_email!
        echo WHATSAPP_NUMBER=!whatsapp_number!
        echo STORE_PHONE=!store_phone!
        echo.
        echo # File Upload Configuration
        echo MAX_CONTENT_LENGTH=16777216
        echo UPLOAD_FOLDER=static/public/produk_images
        echo.
        echo # Session Configuration
        echo PERMANENT_SESSION_LIFETIME=86400
        echo SESSION_COOKIE_SECURE=!IS_PRODUCTION!
        echo SESSION_COOKIE_HTTPONLY=True
        echo SESSION_COOKIE_SAMESITE=Lax
    ) > "%ENV_FILE%"

    call :log_success ".env file created successfully!"
    echo.
    echo 📝 Configuration saved to: %ENV_FILE%
    echo ⚠️  Important: Update payment keys in .env file before production use!
    echo.
) else (
    call :log_success ".env file already exists"
)
goto :eof

:setup_database
call :log "Initializing database..."

REM Initialize Flask database
%PYTHON_CMD% -c "import sys; sys.path.append('.'); from main import app; print('[OK] Flask app initialized and database setup completed')"
if %ERRORLEVEL% neq 0 (
    call :log_error "Failed to initialize Flask database"
    exit /b 1
)

REM Setup Django migrations if chat service exists
if exist "chat_service" (
    cd chat_service
    set "DJANGO_SETTINGS_MODULE=chat_microservice.settings"

    call :log "Running Django migrations..."
    %PYTHON_CMD% manage.py makemigrations chat >nul 2>&1
    %PYTHON_CMD% manage.py migrate >nul 2>&1

    cd ..
)

call :log_success "Database initialization completed"
goto :eof

:setup_sample_data
echo.
echo 📊 Sample Data Setup
echo ===================
echo Would you like to create sample data for testing?
echo This will add sample products, categories, and users to your database.
echo.
set /p "create_sample=Create sample data? (y/N): "

if /i "%create_sample%"=="y" (
    call :log "Creating sample data..."
    if exist "sample_data.py" (
        %PYTHON_CMD% sample_data.py
        if !ERRORLEVEL! neq 0 (
            call :log_warning "Sample data creation failed, continuing..."
        ) else (
            call :log_success "Sample data created successfully!"
        )
    ) else (
        call :log_warning "sample_data.py not found, skipping sample data creation"
    )
) else (
    call :log "Skipping sample data creation"
)
goto :eof

:stop_services
call :log "Stopping existing services..."

REM Stop processes by name
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im py.exe >nul 2>&1

REM Remove PID files
if exist "%PID_FILE%" del "%PID_FILE%"
if exist "%DJANGO_PID_FILE%" del "%DJANGO_PID_FILE%"

call :log_success "Services stopped"
goto :eof

:start_flask
set "flask_port=5000"
set "flask_host=0.0.0.0"

call :check_port %flask_port%
if %ERRORLEVEL% equ 1 (
    call :log_error "Port %flask_port% already in use!"
    exit /b 1
)

call :log "Starting Flask main service on %flask_host%:%flask_port%..."

REM Start Flask
start /b cmd /c "%PYTHON_CMD% main.py >nul 2>&1"

REM Wait for Flask to start
timeout /t 5 /nobreak >nul

call :log_success "Flask service started successfully"
goto :eof

:show_status
echo.
echo ==============================================
echo    🎸 HURTROCK MUSIC STORE STATUS 🎸
echo ==============================================
echo.

echo 📱 Main Website: http://0.0.0.0:5000
echo 👨‍💼 Admin Panel: http://0.0.0.0:5000/admin
echo 💬 Chat API: http://0.0.0.0:8000
echo.
echo 🔑 Default Admin Login:
echo    Email: admin@hurtrock.com
echo    Password: admin123
echo.
echo 📂 Configuration Files:
echo    Environment: %ENV_FILE%
echo    Logs: %LOG_FILE%
echo    Virtual Environment: %VENV_DIR%
echo.
echo ==============================================
goto :eof

:show_help
echo.
echo 🎸 Hurtrock Music Store - Windows Server
echo ========================================
echo.
echo Usage: %~nx0 [COMMAND]
echo.
echo Commands:
echo   start         Start all services (default)
echo   stop          Stop all services
echo   restart       Restart all services
echo   status        Show service status
echo   setup         Complete first-time setup
echo   service       Manage Windows Service (auto-start/restart)
echo   help          Show this help
echo.
echo Service Management:
echo   %~nx0 service install    # Install as Windows Service (auto-start/restart)
echo   %~nx0 service uninstall  # Remove Windows Service
echo   %~nx0 service status     # Show service status
echo.
echo Examples:
echo   %~nx0                    # Start servers (first run will setup)
echo   %~nx0 setup              # Complete first-time setup
echo   %~nx0 service install    # Setup auto-start service (requires admin)
echo.
echo First Time Setup:
echo   1. Run: %~nx0 setup
echo   2. Follow the interactive configuration
echo   3. Update .env file with your payment keys
echo   4. Run: %~nx0 service install (for auto-start, requires admin)
echo   5. Or run: %~nx0 start (manual start)
echo.
goto :eof

:manage_service
if /i "%~2"=="install" (
    if exist "setup-windows-service.bat" (
        echo.
        echo 🔧 Installing Windows Service
        echo =============================
        echo.
        call setup-windows-service.bat install
    ) else (
        call :log_error "setup-windows-service.bat tidak ditemukan!"
    )
) else if /i "%~2"=="uninstall" (
    if exist "setup-windows-service.bat" (
        call setup-windows-service.bat uninstall
    ) else (
        call :log_error "setup-windows-service.bat tidak ditemukan!"
    )
) else if /i "%~2"=="status" (
    if exist "hurtrock-service.py" (
        %PYTHON_CMD% hurtrock-service.py status
    ) else (
        call :log_error "hurtrock-service.py tidak ditemukan!"
    )
) else (
    echo Unknown service action: %~2
    echo.
    echo Available service actions:
    echo   install    - Install Windows Service (requires admin)
    echo   uninstall  - Remove Windows Service (requires admin)
    echo   status     - Show service status
)
goto :eof

:main
if "%~1"=="" goto :start
if /i "%~1"=="start" goto :start
if /i "%~1"=="stop" goto :stop
if /i "%~1"=="restart" goto :restart
if /i "%~1"=="status" goto :show_status
if /i "%~1"=="setup" goto :setup
if /i "%~1"=="service" goto :manage_service
if /i "%~1"=="help" goto :show_help
if /i "%~1"=="--help" goto :show_help
if /i "%~1"=="-h" goto :show_help

echo Unknown command: %~1
echo.
goto :show_help

:setup
echo.
echo 🎸 Hurtrock Music Store - First Time Setup
echo ==========================================
echo.

call :log "Starting complete setup process..."

REM Setup Python environment
call :setup_environment
if %ERRORLEVEL% neq 0 exit /b 1

REM Create .env configuration
call :setup_env_file

REM Initialize database
call :setup_database
if %ERRORLEVEL% neq 0 exit /b 1

REM Setup sample data
call :setup_sample_data

echo.
call :log_success "🎉 Setup completed successfully!"
echo.
echo Next steps:
echo 1. Edit %ENV_FILE% to configure payment keys
echo 2. Run: %~nx0 start
echo.
goto :eof

:start
call :log "🎸 Starting Hurtrock Music Store..."

REM Check if this is first run
if not exist "%ENV_FILE%" (
    echo.
    echo 🔧 First time setup required!
    echo =============================
    echo.
    echo This appears to be your first time running the server.
    echo Let's configure everything for you.
    echo.
    set /p "confirm=Continue with setup? (y/N): "
    if /i "!confirm!"=="y" (
        call :setup
        goto :eof
    ) else (
        echo Setup cancelled. Run '%~nx0 setup' when ready.
        exit /b 1
    )
)

REM Stop any existing services
call :stop_services

REM Setup environment
call :setup_environment
if %ERRORLEVEL% neq 0 exit /b 1

REM Load environment and setup database
call :setup_env_file
call :setup_database
if %ERRORLEVEL% neq 0 exit /b 1

REM Start Flask service
call :start_flask
if %ERRORLEVEL% neq 0 (
    call :log_error "Failed to start Flask service"
    call :stop_services
    exit /b 1
)

call :log_success "🎵 Services started successfully!"
call :show_status

echo Press Ctrl+C to stop all services...
pause >nul
goto :eof

:stop
call :stop_services
goto :eof

:restart
call :log "Restarting services..."
call :stop_services
timeout /t 2 /nobreak >nul
call :start
goto :eof

endlocal
