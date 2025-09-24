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

# Placeholder for check_django_service function if it's not defined elsewhere in the original code
# Assuming it's defined or intended to be defined to check Django's availability
def check_django_service():
    """Check if Django service is responding on port 8000"""
    try:
        import requests
        response = requests.get('http://127.0.0.1:8000/health/', timeout=2) # Use a short timeout for health check
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

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
        """Wait for port to become occupied (service started)"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.check_port(port):  # Port is occupied (service is running)
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

        original_cwd = os.getcwd()
        try:
            # Change to chat service directory
            os.chdir(str(chat_service_dir))

            # Run migrations
            logger.info("Running Django migrations...")
            # Ensure we capture output for better debugging if migrations fail
            migrate_result = subprocess.run([
                sys.executable, 'manage.py', 'migrate', '--run-syncdb'
            ], check=False, capture_output=True, text=True)
            
            if migrate_result.returncode != 0:
                logger.warning(f"Django migrations returned non-zero exit code. STDERR:\n{migrate_result.stderr}")
            else:
                logger.info("Django migrations completed.")


            # Test Django configuration and model access
            logger.info("Testing Django configuration and models...")
            test_script = """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_microservice.settings')
django.setup()
try:
    from chat.models import ChatRoom # Example model
    # Attempt a simple query or operation to confirm DB access
    # For example: ChatRoom.objects.exists()
    print("Django setup OK and models are accessible.")
except ImportError:
    print("Django setup OK, but could not import models.")
except Exception as e:
    print(f"Error during Django model access: {e}")
"""
            result = subprocess.run([
                sys.executable, '-c', test_script
            ], capture_output=True, text=True, cwd=str(chat_service_dir))

            if "Django setup OK" in result.stdout:
                logger.info("Django setup completed successfully")
            else:
                logger.warning(f"Django setup validation failed. STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

            # Return to original directory
            os.chdir(original_cwd)
            return True

        except Exception as e:
            logger.error(f"Django setup failed: {e}", exc_info=True)
            os.chdir(original_cwd)
            return False

    def start_django(self):
        """Start Django service with improved stability"""
        if not self.check_port(8000):
            logger.warning("Port 8000 already in use. Skipping Django start.")
            return False

        logger.info("Starting Django chat service on port 8000...")

        chat_service_dir = self.project_root / 'chat_service'
        manage_py = chat_service_dir / 'manage.py'

        if not manage_py.exists():
            logger.error("Django manage.py not found. Cannot start Django.")
            return False

        # Change to chat service directory
        original_cwd = os.getcwd()
        os.chdir(str(chat_service_dir))

        # Set environment variables for Django
        env = os.environ.copy()
        env.update({
            'DJANGO_SETTINGS_MODULE': 'chat_microservice.settings',
            'PYTHONPATH': str(chat_service_dir),
        })

        try:
            # Start Django development server with improved settings
            self.django_process = subprocess.Popen([
                sys.executable, str(manage_py), 'runserver',
                '0.0.0.0:8000',
                '--noreload',
                '--insecure'  # Serve static files in development
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')

            # Wait for Django to start
            logger.info("Waiting for Django service to start...")
            
            # Wait for port to be occupied
            if self.wait_for_port(8000, timeout=45):
                logger.info("Django port 8000 is now active")
                
                # Give Django a moment to fully initialize
                time.sleep(3)
                
                # Check health endpoint
                if check_django_service():
                    logger.info("Django service started successfully")
                    return True
                else:
                    logger.warning("Django port is active but health check failed")
                    # Continue anyway, might be startup delay
                    return True
            
            # Check if the process has terminated unexpectedly
            if self.django_process.poll() is not None:
                try:
                    stdout, stderr = self.django_process.communicate(timeout=5)
                    logger.error(f"Django process terminated early. Exit code: {self.django_process.returncode}")
                    if stdout:
                        logger.error(f"STDOUT: {stdout}")
                    if stderr:
                        logger.error(f"STDERR: {stderr}")
                except subprocess.TimeoutExpired:
                    logger.error("Could not retrieve output from terminated Django process")
                return False

            # If we get here, Django didn't start in time
            logger.error("Django service failed to start within timeout period")
            try:
                stdout, stderr = self.django_process.communicate(timeout=5)
                logger.error(f"Django STDOUT: {stdout}")
                logger.error(f"Django STDERR: {stderr}")
            except subprocess.TimeoutExpired:
                logger.error("Could not retrieve output from terminated Django process.")
            
            self.django_process.terminate() # Ensure termination
            return False

        except Exception as e:
            logger.error(f"Failed to start Django service: {e}", exc_info=True)
            return False
        finally:
            # Return to original directory
            os.chdir(original_cwd)


    def start_flask(self):
        """Start Flask service"""
        if not self.check_port(5000):
            logger.warning("Port 5000 already in use. Skipping Flask start.")
            return False

        logger.info("Starting Flask main service on port 5000...")

        try:
            # Import and run Flask app directly in thread
            def run_flask():
                try:
                    # Import Flask app
                    from main import app
                    # Use a more robust run method if possible, but keep original structure
                    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
                except Exception as e:
                    logger.error(f"Flask error: {e}", exc_info=True)
            
            # Ensure Flask runs with the correct environment and settings
            # It's assumed 'main.py' and 'app' instance are correctly set up
            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()

            # Wait for Flask to start
            if self.wait_for_port(5000):
                logger.info("Flask service started successfully")
                return True
            else:
                logger.error("Flask service failed to start within timeout")
                return False

        except Exception as e:
            logger.error(f"Failed to start Flask: {e}", exc_info=True)
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
        logger.info(f"Shutdown signal {signum} received, stopping services...")
        self.stop()
        sys.exit(0)

    def stop(self):
        """Stop all services"""
        self.running = False

        if self.django_process and self.django_process.poll() is None: # Check if process is running
            logger.info("Stopping Django service...")
            try:
                self.django_process.terminate()
                self.django_process.wait(timeout=10)
                logger.info("Django service stopped.")
            except subprocess.TimeoutExpired:
                logger.warning("Django process did not terminate gracefully, killing...")
                self.django_process.kill()
            except Exception as e:
                logger.error(f"Error stopping Django: {e}")

        # Add logic to stop Flask if it was started in a managed way (e.g., via a subprocess)
        # If Flask is run in a thread as in start_flask, it will exit when the main process exits.
        # If it needs explicit stopping, a mechanism to signal the thread or manage its process would be needed.
        logger.info("All managed services stopped.")


    def start(self):
        """Start all services"""
        logger.info("=" * 60)
        logger.info("🎸 STARTING HURTROCK MUSIC STORE 🎸")
        logger.info("=" * 60)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Setup Django (migrations, etc.)
        if not self.setup_django():
            logger.error("Django setup failed. Proceeding with caution.")
        else:
            logger.info("Django setup completed.")

        # Start Django service
        if not self.start_django():
            logger.error("Failed to start Django service. Flask will run standalone.")
            # Optionally, decide if Flask should still start or if the whole server should exit.
            # For now, we allow Flask to start.

        # Start Flask service
        if not self.start_flask():
            logger.error("Failed to start Flask service. Exiting.")
            self.stop() # Ensure any started services are stopped
            return False

        # Wait a moment for services to stabilize before testing
        time.sleep(5) # Increased sleep time

        # Test services
        logger.info("Testing services...")
        if self.test_services():
            logger.info("✓ All services are healthy")
        else:
            logger.warning("⚠ Some services may have issues. Check logs for details.")

        self.running = True

        # Print service information
        logger.info("")
        logger.info("🎵 HURTROCK MUSIC STORE SERVICES STARTED 🎵")
        logger.info("=" * 60)
        logger.info("📱 MAIN WEBSITE (Flask):   http://0.0.0.0:5000")
        logger.info("💬 Chat Service (Django):  http://0.0.0.0:8000")
        logger.info("👨‍💼 Admin Panel:            http://0.0.0.0:5000/admin")
        logger.info("💬 Chat Interface:          http://0.0.0.0:5000/admin/chat")
        logger.info("")
        logger.info("🔑 Default Admin Login:")
        logger.info("   Email: admin@hurtrock.com")
        logger.info("   Password: admin123")
        logger.info("")
        logger.info("⭐ AKSES UTAMA: PORT 5000 (bukan 8000)")
        logger.info("   Django di port 8000 hanya untuk API chat internal")
        logger.info("")
        logger.info("📱 Mobile App Chat API:    http://0.0.0.0:8000/api/")
        logger.info("🌐 WebSocket Chat:          ws://0.0.0.0:8000/ws/chat/")
        logger.info("=" * 60)
        logger.info("🎸 Press Ctrl+C to stop all services")
        logger.info("=" * 60)

        # Keep running
        try:
            while self.running:
                # Add a small sleep to prevent high CPU usage in the main loop
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
        logger.error(f"Server startup failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()