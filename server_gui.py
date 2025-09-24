
#!/usr/bin/env python3
"""
Hurtrock Music Store - GUI Server Manager
Interface GUI untuk mengontrol dan memonitor server Flask dan Django
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import requests
import socket
import time
import os
import sys
import signal
from datetime import datetime
from pathlib import Path

class PortConfig:
    """Class untuk mengelola konfigurasi port"""
    def __init__(self, config_file='config.txt'):
        self.config_file = config_file
        self.default_config = {
            'FLASK_PORT': '5000',
            'DJANGO_PORT': '8000'
        }
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        self.config = self.default_config.copy()
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            self.config[key.strip()] = value.strip()
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Create file if doesn't exist
        if not os.path.exists(self.config_file):
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write("# Hurtrock Music Store - Port Configuration\n")
                f.write("# Format: KEY=VALUE\n\n")
                for key, value in self.config.items():
                    f.write(f"{key}={value}\n")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_flask_port(self):
        return int(self.config.get('FLASK_PORT', 5000))
    
    def get_django_port(self):
        return int(self.config.get('DJANGO_PORT', 8000))
    
    def set_flask_port(self, port):
        self.config['FLASK_PORT'] = str(port)
        self.save_config()
    
    def set_django_port(self, port):
        self.config['DJANGO_PORT'] = str(port)
        self.save_config()

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hurtrock Music Store - Server Manager")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Initialize port configuration
        self.port_config = PortConfig()
        
        # Server process references
        self.flask_process = None
        self.django_process = None
        self.is_running = False
        
        # Get project root
        self.project_root = Path(__file__).resolve().parent
        
        # Setup GUI
        self.setup_gui()
        
        # Start status monitoring
        self.start_monitoring()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_gui(self):
        """Setup the GUI components"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎸 Hurtrock Music Store Server Manager", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Port Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="Port Configuration", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Flask Port
        ttk.Label(config_frame, text="Flask Port:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.flask_port_var = tk.StringVar(value=str(self.port_config.get_flask_port()))
        flask_port_entry = ttk.Entry(config_frame, textvariable=self.flask_port_var, width=10)
        flask_port_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Django Port
        ttk.Label(config_frame, text="Django Port:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W)
        self.django_port_var = tk.StringVar(value=str(self.port_config.get_django_port()))
        django_port_entry = ttk.Entry(config_frame, textvariable=self.django_port_var, width=10)
        django_port_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Apply Config Button
        apply_config_btn = ttk.Button(config_frame, text="Apply Config", command=self.apply_port_config)
        apply_config_btn.grid(row=0, column=2, rowspan=2, padx=(20, 0))
        
        # Server Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Server Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Flask Status
        ttk.Label(status_frame, text="Flask Server:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.flask_status_var = tk.StringVar(value="🔴 Stopped")
        self.flask_status_label = ttk.Label(status_frame, textvariable=self.flask_status_var)
        self.flask_status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Django Status
        ttk.Label(status_frame, text="Django Chat:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W)
        self.django_status_var = tk.StringVar(value="🔴 Stopped")
        self.django_status_label = ttk.Label(status_frame, textvariable=self.django_status_var)
        self.django_status_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Host Information
        ttk.Separator(status_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(status_frame, text="Local Host:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W)
        local_ip = self.get_local_ip()
        self.local_host_var = tk.StringVar()
        self.update_host_display()
        ttk.Label(status_frame, textvariable=self.local_host_var, foreground="blue").grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(status_frame, text="Public Host:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W)
        public_host = self.get_public_host()
        self.public_host_var = tk.StringVar(value=public_host)
        ttk.Label(status_frame, textvariable=self.public_host_var, foreground="green").grid(row=4, column=1, sticky=tk.W, padx=(10, 0))
        
        # Ports Information
        ttk.Label(status_frame, text="Flask Port:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W)
        self.flask_port_display_var = tk.StringVar()
        ttk.Label(status_frame, textvariable=self.flask_port_display_var, foreground="blue").grid(row=5, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(status_frame, text="Django Port:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W)
        self.django_port_display_var = tk.StringVar()
        ttk.Label(status_frame, textvariable=self.django_port_display_var, foreground="blue").grid(row=6, column=1, sticky=tk.W, padx=(10, 0))
        
        self.update_port_display()
        
        # Control Buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="🚀 Start Servers", command=self.start_servers)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="🛑 Stop Servers", command=self.stop_servers, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.restart_button = ttk.Button(control_frame, text="🔄 Restart Servers", command=self.restart_servers, state='disabled')
        self.restart_button.grid(row=0, column=2, padx=(0, 10))
        
        # Quick Access Buttons
        access_frame = ttk.Frame(main_frame)
        access_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(20, 0), pady=(0, 10))
        
        ttk.Button(access_frame, text="🌐 Open Main Store", command=self.open_main_store).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(access_frame, text="👨‍💼 Open Admin", command=self.open_admin).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(access_frame, text="💬 Chat API", command=self.open_chat_api).grid(row=0, column=2)
        
        # Log Display
        log_frame = ttk.LabelFrame(main_frame, text="Server Logs", padding="5")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, state='disabled')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear logs button
        ttk.Button(log_frame, text="Clear Logs", command=self.clear_logs).grid(row=1, column=0, sticky=tk.E, pady=(5, 0))

    def apply_port_config(self):
        """Apply new port configuration"""
        try:
            flask_port = int(self.flask_port_var.get())
            django_port = int(self.django_port_var.get())
            
            # Validate ports
            if not (1024 <= flask_port <= 65535) or not (1024 <= django_port <= 65535):
                messagebox.showerror("Error", "Port harus antara 1024-65535")
                return
            
            if flask_port == django_port:
                messagebox.showerror("Error", "Port Flask dan Django tidak boleh sama")
                return
            
            # Check if servers are running
            if self.is_running:
                result = messagebox.askyesno("Restart Required", 
                    "Server sedang berjalan. Restart server untuk menerapkan konfigurasi baru?")
                if result:
                    # Save config first
                    self.port_config.set_flask_port(flask_port)
                    self.port_config.set_django_port(django_port)
                    self.update_port_display()
                    self.update_host_display()
                    self.restart_servers()
                return
            
            # Save configuration
            self.port_config.set_flask_port(flask_port)
            self.port_config.set_django_port(django_port)
            self.update_port_display()
            self.update_host_display()
            
            self.log_message(f"✅ Configuration saved: Flask:{flask_port}, Django:{django_port}")
            messagebox.showinfo("Success", "Konfigurasi port berhasil disimpan!")
            
        except ValueError:
            messagebox.showerror("Error", "Port harus berupa angka")

    def update_port_display(self):
        """Update port display in status section"""
        flask_port = self.port_config.get_flask_port()
        django_port = self.port_config.get_django_port()
        
        self.flask_port_display_var.set(f"{flask_port} (Main Store)")
        self.django_port_display_var.set(f"{django_port} (Chat API)")

    def update_host_display(self):
        """Update host display with current ports"""
        local_ip = self.get_local_ip()
        flask_port = self.port_config.get_flask_port()
        
        self.local_host_var.set(f"http://127.0.0.1:{flask_port}, http://{local_ip}:{flask_port}")

    def get_local_ip(self):
        """Get local IP address"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
            sock.close()
            return local_ip
        except Exception:
            return "0.0.0.0"

    def get_public_host(self):
        """Get public host if available (Replit environment)"""
        repl_id = os.environ.get('REPL_ID')
        if repl_id:
            return f"https://{repl_id}.replit.dev"
        
        public_url = os.environ.get('PUBLIC_URL', '')
        if public_url:
            return public_url
            
        return "Not available (running locally)"

    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
        # Keep only last 200 lines to prevent memory issues
        lines = self.log_text.get(1.0, tk.END).split('\n')
        if len(lines) > 200:
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, f"{len(lines) - 200}.0")
            self.log_text.config(state='disabled')

    def clear_logs(self):
        """Clear the log display"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

    def check_port(self, port):
        """Check if port is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result != 0
        except Exception:
            return True

    def check_server_health(self, url):
        """Check if server is responding"""
        try:
            response = requests.get(url, timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def start_servers(self):
        """Start both Flask and Django servers"""
        if self.is_running:
            self.log_message("⚠️ Servers already running!")
            return
            
        self.log_message("🚀 Starting servers...")
        
        # Disable start button, enable others
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.restart_button.config(state='normal')
        
        # Start in separate thread to avoid blocking GUI
        threading.Thread(target=self._start_servers_thread, daemon=True).start()

    def _start_servers_thread(self):
        """Thread function to start servers"""
        try:
            # Change to project directory
            os.chdir(str(self.project_root))
            
            flask_port = self.port_config.get_flask_port()
            django_port = self.port_config.get_django_port()
            
            # Start Django first
            self.log_message(f"📡 Starting Django chat service on port {django_port}...")
            django_env = os.environ.copy()
            django_env['DJANGO_SETTINGS_MODULE'] = 'chat_microservice.settings'
            
            self.django_process = subprocess.Popen([
                sys.executable, 'chat_service/manage.py', 'runserver', f'0.0.0.0:{django_port}', '--noreload'
            ], env=django_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            # Wait a moment for Django to start
            time.sleep(3)
            
            # Start Flask with custom port
            self.log_message(f"🌐 Starting Flask main server on port {flask_port}...")
            flask_env = os.environ.copy()
            flask_env['FLASK_PORT'] = str(flask_port)
            
            self.flask_process = subprocess.Popen([
                sys.executable, '-c', f'''
import os
os.environ["FLASK_PORT"] = "{flask_port}"
from main import app
app.run(host="0.0.0.0", port={flask_port}, debug=False, use_reloader=False)
'''
            ], env=flask_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            # Wait for servers to be ready
            time.sleep(5)
            
            self.is_running = True
            self.log_message("✅ Servers started successfully!")
            
            # Start log monitoring threads
            threading.Thread(target=self._monitor_flask_logs, daemon=True).start()
            threading.Thread(target=self._monitor_django_logs, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"❌ Error starting servers: {str(e)}")
            self.is_running = False
            self.root.after(0, self._reset_buttons)

    def _monitor_flask_logs(self):
        """Monitor Flask process logs"""
        if not self.flask_process:
            return
            
        try:
            while self.flask_process and self.flask_process.poll() is None:
                line = self.flask_process.stdout.readline()
                if line:
                    self.root.after(0, lambda: self.log_message(f"Flask: {line.strip()}"))
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Flask log error: {str(e)}"))

    def _monitor_django_logs(self):
        """Monitor Django process logs"""
        if not self.django_process:
            return
            
        try:
            while self.django_process and self.django_process.poll() is None:
                line = self.django_process.stdout.readline()
                if line:
                    self.root.after(0, lambda: self.log_message(f"Django: {line.strip()}"))
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Django log error: {str(e)}"))

    def stop_servers(self):
        """Stop both servers"""
        if not self.is_running:
            self.log_message("⚠️ Servers not running!")
            return
            
        self.log_message("🛑 Stopping servers...")
        
        # Stop processes
        if self.flask_process:
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=5)
                self.log_message("✅ Flask server stopped")
            except subprocess.TimeoutExpired:
                self.flask_process.kill()
                self.log_message("⚡ Flask server force killed")
            except Exception as e:
                self.log_message(f"❌ Error stopping Flask: {str(e)}")
            finally:
                self.flask_process = None
                
        if self.django_process:
            try:
                self.django_process.terminate()
                self.django_process.wait(timeout=5)
                self.log_message("✅ Django server stopped")
            except subprocess.TimeoutExpired:
                self.django_process.kill()
                self.log_message("⚡ Django server force killed")
            except Exception as e:
                self.log_message(f"❌ Error stopping Django: {str(e)}")
            finally:
                self.django_process = None
        
        self.is_running = False
        self._reset_buttons()

    def restart_servers(self):
        """Restart both servers"""
        self.log_message("🔄 Restarting servers...")
        self.stop_servers()
        time.sleep(2)
        self.start_servers()

    def _reset_buttons(self):
        """Reset button states"""
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.restart_button.config(state='disabled')

    def start_monitoring(self):
        """Start periodic status monitoring"""
        self.update_status()
        self.root.after(3000, self.start_monitoring)  # Check every 3 seconds

    def update_status(self):
        """Update server status display"""
        flask_port = self.port_config.get_flask_port()
        django_port = self.port_config.get_django_port()
        
        # Check Flask
        if self.check_server_health(f"http://127.0.0.1:{flask_port}"):
            self.flask_status_var.set("🟢 Running")
        else:
            self.flask_status_var.set("🔴 Stopped")
            
        # Check Django
        if self.check_server_health(f"http://127.0.0.1:{django_port}/health/"):
            self.django_status_var.set("🟢 Running")
        else:
            self.django_status_var.set("🔴 Stopped")

    def open_main_store(self):
        """Open main store in browser"""
        import webbrowser
        flask_port = self.port_config.get_flask_port()
        webbrowser.open(f"http://127.0.0.1:{flask_port}")
        self.log_message("🌐 Opening main store in browser")

    def open_admin(self):
        """Open admin panel in browser"""
        import webbrowser
        flask_port = self.port_config.get_flask_port()
        webbrowser.open(f"http://127.0.0.1:{flask_port}/admin")
        self.log_message("👨‍💼 Opening admin panel in browser")

    def open_chat_api(self):
        """Open chat API in browser"""
        import webbrowser
        django_port = self.port_config.get_django_port()
        webbrowser.open(f"http://127.0.0.1:{django_port}")
        self.log_message("💬 Opening chat API in browser")

    def on_closing(self):
        """Handle window closing event"""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Servers are running. Do you want to stop them and quit?"):
                self.stop_servers()
                time.sleep(1)
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Main function"""
    # Create and run GUI
    root = tk.Tk()
    app = ServerGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down GUI...")
        app.stop_servers()

if __name__ == '__main__':
    main()
