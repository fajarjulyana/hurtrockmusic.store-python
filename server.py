
#!/usr/bin/env python3
"""
Hurtrock Music Store - Universal Server Launcher
Menjalankan Flask dan Django service secara bersamaan
Compatible dengan semua environment dan siap untuk packaging
"""

import os
import sys
import time
import signal
import threading
import subprocess
from pathlib import Path
import socket
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class HurtrockServer:
    def __init__(self):
        self.flask_process = None
        self.django_process = None
        self.running = False
        self.project_root = Path(__file__).resolve().parent
        
        # Setup environment
        self.setup_environment()
        
    def setup_environment(self):
        """Setup environment variables and paths"""
        # Add project paths to Python path
        sys.path.insert(0, str(self.project_root))
        sys.path.insert(0, str(self.project_root / 'chat_service'))
        
        # Set default environment variables
        os.environ.setdefault('PYTHONPATH', str(self.project_root))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')
        
        # Generate session secret if not exists
        if not os.environ.get('SESSION_SECRET'):
            import secrets
            session_secret = secrets.token_urlsafe(32)
            os.environ['SESSION_SECRET'] = session_secret
            logger.info("Generated session secret")
            
            # Save to .env file
            env_file = self.project_root / '.env'
            with open(env_file, 'a') as f:
                f.write(f"\nSESSION_SECRET='{session_secret}'\n")
        
        # Set other default environment variables
        os.environ.setdefault('FLASK_ENV', 'development')
        os.environ.setdefault('FLASK_DEBUG', '1')
        
        logger.info("Environment setup completed")
    
    def check_port(self, port):
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return True
    
    def wait_for_port(self, port, timeout=30):
        """Wait for port to become available"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.check_port(port):
                return True
            time.sleep(0.5)
        return False
    
    def setup_django(self):
        """Setup Django migrations and database"""
        logger.info("Setting up Django chat service...")
        
        chat_service_dir = self.project_root / 'chat_service'
        if not chat_service_dir.exists():
            logger.error("Chat service directory not found")
            return False
        
        try:
            # Change to chat service directory
            original_cwd = os.getcwd()
            os.chdir(str(chat_service_dir))
            
            # Run migrations
            logger.info("Running Django migrations...")
            subprocess.run([
                sys.executable, 'manage.py', 'migrate', '--run-syncdb'
            ], check=False, capture_output=True)
            
            # Test Django configuration
            result = subprocess.run([
                sys.executable, '-c', 
                'import django; django.setup(); from chat.models import ChatRoom; print("Django OK")'
            ], capture_output=True, text=True, cwd=str(chat_service_dir))
            
            if result.returncode == 0:
                logger.info("Django setup completed successfully")
            else:
                logger.warning(f"Django setup warning: {result.stderr}")
            
            # Return to original directory
            os.chdir(original_cwd)
            return True
            
        except Exception as e:
            logger.error(f"Django setup failed: {e}")
            os.chdir(original_cwd)
            return False
    
    def start_django(self):
        """Start Django service"""
        if not self.check_port(8000):
            logger.warning("Port 8000 already in use")
            return False
        
        logger.info("Starting Django chat service on port 8000...")
        
        chat_service_dir = self.project_root / 'chat_service'
        
        try:
            self.django_process = subprocess.Popen([
                sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000', '--noreload'
            ], cwd=str(chat_service_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for Django to start
            if self.wait_for_port(8000, timeout=15):
                logger.info("Django service started successfully")
                return True
            else:
                logger.error("Django service failed to start within timeout")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Django: {e}")
            return False
    
    def start_flask(self):
        """Start Flask service"""
        if not self.check_port(5000):
            logger.warning("Port 5000 already in use")
            return False
        
        logger.info("Starting Flask main service on port 5000...")
        
        try:
            # Import and run Flask app directly in thread
            def run_flask():
                try:
                    # Import Flask app
                    from main import app
                    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
                except Exception as e:
                    logger.error(f"Flask error: {e}")
            
            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()
            
            # Wait for Flask to start
            if self.wait_for_port(5000, timeout=15):
                logger.info("Flask service started successfully")
                return True
            else:
                logger.error("Flask service failed to start within timeout")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Flask: {e}")
            return False
    
    def test_services(self):
        """Test if services are responding"""
        import requests
        
        services_ok = True
        
        # Test Flask
        try:
            response = requests.get('http://127.0.0.1:5000/', timeout=5)
            if response.status_code == 200:
                logger.info("✓ Flask service is responding")
            else:
                logger.warning(f"✗ Flask service returned {response.status_code}")
                services_ok = False
        except Exception as e:
            logger.warning(f"✗ Flask service test failed: {e}")
            services_ok = False
        
        # Test Django
        try:
            response = requests.get('http://127.0.0.1:8000/health/', timeout=5)
            if response.status_code == 200:
                logger.info("✓ Django service is responding")
            else:
                logger.warning(f"✗ Django service returned {response.status_code}")
                services_ok = False
        except Exception as e:
            logger.warning(f"✗ Django service test failed: {e}")
            services_ok = False
        
        return services_ok
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received, stopping services...")
        self.stop()
        sys.exit(0)
    
    def stop(self):
        """Stop all services"""
        self.running = False
        
        if self.django_process:
            logger.info("Stopping Django service...")
            try:
                self.django_process.terminate()
                self.django_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.django_process.kill()
            except Exception as e:
                logger.error(f"Error stopping Django: {e}")
        
        logger.info("All services stopped")
    
    def start(self):
        """Start all services"""
        logger.info("=" * 60)
        logger.info("🎸 STARTING HURTROCK MUSIC STORE 🎸")
        logger.info("=" * 60)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Setup Django
        if not self.setup_django():
            logger.error("Failed to setup Django, continuing anyway...")
        
        # Start Django service
        if not self.start_django():
            logger.error("Failed to start Django service, continuing with Flask only...")
        
        # Start Flask service
        if not self.start_flask():
            logger.error("Failed to start Flask service")
            self.stop()
            return False
        
        # Wait a moment for services to stabilize
        time.sleep(3)
        
        # Test services
        logger.info("Testing services...")
        if self.test_services():
            logger.info("✓ All services are healthy")
        else:
            logger.warning("⚠ Some services may have issues")
        
        self.running = True
        
        # Print service information
        logger.info("")
        logger.info("🎵 HURTROCK MUSIC STORE SERVICES STARTED 🎵")
        logger.info("=" * 60)
        logger.info("📱 Main Store (Flask):     http://0.0.0.0:5000")
        logger.info("💬 Chat Service (Django):  http://0.0.0.0:8000")
        logger.info("👨‍💼 Admin Panel:            http://0.0.0.0:5000/admin")
        logger.info("💬 Chat Interface:          http://0.0.0.0:5000/admin/chat")
        logger.info("")
        logger.info("🔑 Default Admin Login:")
        logger.info("   Email: admin@hurtrock.com")
        logger.info("   Password: admin123")
        logger.info("")
        logger.info("📱 Mobile App Chat API:    http://0.0.0.0:8000/api/")
        logger.info("🌐 WebSocket Chat:          ws://0.0.0.0:8000/ws/chat/")
        logger.info("=" * 60)
        logger.info("🎸 Press Ctrl+C to stop all services")
        logger.info("=" * 60)
        
        # Keep running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.stop()
        
        return True

def main():
    """Main entry point"""
    try:
        server = HurtrockServer()
        success = server.start()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
