# [MUSIC] Hurtrock Music Store

Aplikasi e-commerce modern untuk toko alat musik dengan tema Rock/Metal menggunakan font Metal Mania dan Rock Salt, sistem manajemen produk, shopping cart, pembayaran terintegrasi Stripe & Midtrans, dan live chat support dengan arsitektur microservice yang dapat di-package sebagai executable.

## [START] Teknologi yang Digunakan

### Backend Framework
- **Flask 3.1.2** - Web framework Python yang ringan dan fleksibel
- **SQLAlchemy 2.0.43** - ORM untuk manajemen database
- **Flask-Login 0.6.3** - Sistem autentikasi dan session management
- **Flask-Migrate 4.1.0** - Database migration tool
- **Flask-WTF 1.2.2** - Form handling dan CSRF protection
- **Django 5.2.6** - Framework untuk chat microservice
- **Django REST Framework** - API untuk chat service

### Database & Storage
- **PostgreSQL** - Database utama untuk data produk, user, dan transaksi
- **Psycopg2-Binary 2.9.10** - PostgreSQL adapter untuk Python
- **SQLite** - Database untuk chat microservice

### Payment Processing
- **Stripe 12.5.1** - Gateway pembayaran internasional yang aman
- **Midtrans** - Gateway pembayaran lokal Indonesia

### Real-time Communication
- **Django Channels** - WebSocket untuk real-time chat
- **Channels Redis** - Channel layer untuk WebSocket
- **ASGI/Daphne** - ASGI server untuk Django

### Image & Document Processing
- **Pillow 11.3.0** - Library untuk kompresi dan manipulasi gambar
- **ReportLab 4.4.4** - PDF generation untuk invoice dan laporan
- **OpenPyXL 3.1.5** - Excel export untuk data analytics

### Frontend & Real-time Features
- **Bootstrap 5.3.0** - CSS framework untuk responsive design
- **Font Awesome 6.0.0** - Icon library
- **WebSocket Client** - Real-time bidirectional communication
- **Metal Mania & Rock Salt Fonts** - Google Fonts untuk tema Rock/Metal

### Security & Utilities
- **Werkzeug 3.1.3** - Password hashing dan security utilities
- **Email-Validator 2.3.0** - Validasi format email
- **Python-Dotenv 1.1.1** - Environment variable management
- **CORS Headers** - Cross-origin resource sharing untuk microservice

## [DESIGN] Tema dan Desain

### Color Scheme
```css
:root {
    --orange-primary: #FF6B35;    /* Orange utama untuk aksen */
    --orange-secondary: #FF8C42;  /* Orange sekunder untuk hover */
    --black-primary: #1A1A1A;     /* Hitam utama untuk teks */
    --black-secondary: #2D2D2D;   /* Hitam sekunder untuk background */
    --white-primary: #FFFFFF;     /* Putih untuk background utama */
    --gray-light: #F8F9FA;        /* Abu-abu terang */
    --gray-medium: #6C757D;       /* Abu-abu medium */
    --glass-bg: rgba(255, 255, 255, 0.15);  /* Efek kaca */
    --glass-border: rgba(255, 255, 255, 0.2); /* Border kaca */
}
```

### Typography
- **Metal Mania** - Font utama untuk headings dan brand (Google Fonts)
- **Rock Salt** - Font sekunder untuk body text dan navigasi (Google Fonts)
- **Segoe UI** - Font default untuk admin dashboard

### Design Elements
- Glass morphism effects pada navbar
- Orange-Black color scheme dengan tema Rock/Metal
- Responsive mobile-first design
- Light/Dark mode toggle dengan CSS custom properties
- Smooth animations dan hover effects
- Theme persistence dengan localStorage

## [FEATURE] Fitur yang Tersedia

### [SHOP] Sisi Pengguna (Customer)
1. **Autentikasi & Profil**
   - [OK] Registrasi akun baru dengan validasi email
   - [OK] Login/logout sistem dengan session management
   - [OK] Manajemen profil pengguna dengan update data

2. **Katalog Produk**
   - [OK] Browse produk berdasarkan kategori
   - [OK] Search real-time dengan autocomplete
   - [OK] Detail produk dengan galeri gambar multi-image
   - [OK] Filter dan sorting produk (harga, nama, kategori)
   - [OK] Featured products highlighting

3. **Shopping Cart**
   - [OK] Add to cart functionality dengan AJAX
   - [OK] Update quantity items secara real-time
   - [OK] Remove items dari cart
   - [OK] Subtotal calculation otomatis
   - [OK] Cart persistence dalam session

4. **Payment & Checkout**
   - [OK] Integrasi dengan Stripe payment gateway
   - [OK] Integrasi dengan Midtrans payment gateway
   - [OK] Checkout process yang aman dengan CSRF protection
   - [OK] Order confirmation dengan order tracking
   - [OK] Payment success page dengan order details

5. **Live Chat Support**
   - [OK] Real-time chat dengan admin menggunakan WebSocket
   - [OK] Product tagging dalam chat messages
   - [OK] Chat history persistence
   - [OK] Online/offline status indicators
   - [OK] Floating chat widget

6. **Theme & UX**
   - [OK] Light/Dark mode toggle dengan smooth transitions
   - [OK] Responsive mobile-first design
   - [OK] Glass morphism UI effects
   - [OK] Rock/Metal themed fonts dan colors
   - [OK] Theme preference persistence

### 👨‍💼 Sisi Admin
1. **Dashboard Analytics**
   - [OK] Total products, orders, users statistics
   - [OK] Today's sales dan monthly sales tracking
   - [OK] Recent orders overview dengan status
   - [OK] Best selling products analytics
   - [OK] Pending chats notification

2. **Product Management**
   - [OK] CRUD operations untuk produk dengan multi-image upload
   - [OK] Drag & drop image upload dengan preview real-time
   - [OK] Thumbnail selection untuk gambar utama
   - [OK] Image compression otomatis untuk optimasi storage
   - [OK] Kategori management dengan hierarki
   - [OK] Stock quantity tracking dengan alert
   - [OK] Featured products marking
   - [OK] Product search dan filtering

3. **Order Processing**
   - [OK] View all orders dengan pagination
   - [OK] Order status management (pending, paid, shipped, delivered)
   - [OK] Customer information access
   - [OK] Order details dengan item breakdown
   - [OK] Thermal label printing untuk shipping

4. **User Management**
   - [OK] User list dengan role management
   - [OK] Add new users dengan admin privileges
   - [OK] User activity tracking
   - [OK] Account activation/deactivation

5. **Live Chat Management**
   - [OK] Real-time chat interface dengan customers
   - [OK] Chat room management
   - [OK] Message history dan archiving
   - [OK] Product recommendation dalam chat
   - [OK] Microservice architecture untuk scalability

## 🏗️ Arsitektur Sistem

### Unified Server Architecture

Hurtrock Music Store menggunakan arsitektur **unified server** dengan **server.py** sebagai launcher utama yang menjalankan Flask dan Django secara bersamaan.

```
┌─────────────────────────────────────────────────────────┐
│                    server.py                           │
│                 (Unified Launcher)                     │
└─────────────────────┬───────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼────┐      ┌────▼────┐      ┌────▼────┐
│ Flask  │      │ Django  │      │ Static  │
│ Main   │◄────►│ Chat    │      │ Files   │
│ App    │      │ Service │      │ Server  │
│ :5000  │      │ :8000   │      │         │
└───┬────┘      └────┬────┘      └─────────┘
    │                │                
    ▼                ▼                
┌───────────┐   ┌───────────┐
│PostgreSQL │   │ SQLite    │
│ Main DB   │   │ Chat DB   │
└───────────┘   └───────────┘
```

### Component Architecture

- **Unified Server Layer**: server.py mengelola semua service
- **Presentation Layer**: Jinja2 Templates + Bootstrap 5 + Vanilla JS
- **Business Logic Layer**: Flask Routes + Service Classes
- **Data Access Layer**: SQLAlchemy ORM + PostgreSQL
- **Chat Service Layer**: Django + Django Channels + WebSocket
- **Integration Layer**: Payment Gateways + Email Services
- **Real-time Layer**: WebSocket untuk chat dan notifications

## 🛠️ Instalasi & Setup

### Environment Requirements
- Python 3.11+
- PostgreSQL 12+

### 1. Clone Repository
```bash
git clone https://github.com/your-repo/hurtrock-music-store.git
cd hurtrock-music-store
```

### 2. Setup Environment Variables
```bash
# Required environment variables
SESSION_SECRET=your_very_secure_secret_key_here
DATABASE_URL=postgresql://user:password@host:port/dbname
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
MIDTRANS_SERVER_KEY=your_midtrans_server_key
MIDTRANS_CLIENT_KEY=your_midtrans_client_key
```

### 3. Auto Installation (Recommended)

**Universal Installation (Linux/macOS/Replit)**:
```bash
chmod +x install.sh
./install.sh
```

**Linux Server Installation**:
```bash
chmod +x install-linux.sh
./install-linux.sh
```

**Manual Installation**:
```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
python migrate_db.py

# Load sample data
python sample_data.py
```

### 4. Run Application

**Using Unified Server (Recommended)**:
```bash
python server.py
```

**Using Start Script**:
```bash
./start_server.sh
```

**Development Mode (Flask only)**:
```bash
python main.py
```

Aplikasi akan berjalan di:
- **Main App**: `http://0.0.0.0:5000`
- **Chat Service**: `http://0.0.0.0:8000`
- **Admin Panel**: `http://0.0.0.0:5000/admin`

## [PACKAGE] Packaging untuk Distribusi

### Persiapan untuk PyInstaller

Aplikasi telah didesain untuk dapat di-package sebagai executable menggunakan PyInstaller:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --add-data "templates:templates" --add-data "static:static" --add-data "chat_service:chat_service" server.py

# Atau untuk GUI application (tanpa console)
pyinstaller --onefile --windowed --add-data "templates:templates" --add-data "static:static" --add-data "chat_service:chat_service" server.py
```

### Distribusi

**Windows (.exe)**:
- Executable akan dibuat di folder `dist/`
- Dapat didistribusikan sebagai standalone application

**Linux (.deb)**:
```bash
# Install fpm
sudo apt install ruby-dev build-essential
gem install fpm

# Create .deb package
fpm -s dir -t deb -n hurtrock-music-store -v 1.0.0 --description "Hurtrock Music Store E-commerce Application" dist/server=/usr/local/bin/
```

## [MOBILE] Usage Guide

### Default Admin Access
- **Email**: admin@hurtrock.com
- **Password**: admin123
- **Admin Panel**: `/admin`

### Customer Flow
1. **Registrasi**: `/register` - Daftar akun baru
2. **Browse**: `/products` - Lihat katalog produk
3. **Cart**: Add produk ke cart dan proceed checkout
4. **Payment**: Integrasi Stripe/Midtrans untuk pembayaran aman
5. **Chat**: Live chat support dengan admin via WebSocket
6. **Theme**: Toggle light/dark mode sesuai preferensi

### Admin Flow
1. **Dashboard**: `/admin` - Overview analytics dan metrics
2. **Products**: Kelola produk dengan multi-image upload
3. **Orders**: Monitor dan update status orders
4. **Users**: User management dan role assignment
5. **Chat**: Respond ke customer inquiries real-time
6. **Analytics**: Generate reports dan export data

## 🔐 Security Features

### Application Security
- **CSRF Protection** pada semua forms dengan Flask-WTF
- **Password Hashing** menggunakan Werkzeug PBKDF2
- **Secure Sessions** dengan HTTPS-only cookies di production
- **SQL Injection Protection** via SQLAlchemy ORM
- **Input Validation** dan sanitization pada semua endpoints
- **Role-based Access Control** untuk admin features
- **JWT Authentication** untuk chat service communication

### Production Security
- **HTTPS Enforcement** di production deployment
- **SameSite Cookie** protection untuk CSRF prevention
- **HTTPOnly Cookies** untuk session security
- **Environment Variable** protection untuk sensitive data
- **CORS Configuration** untuk microservice communication

## [WEB] Deployment di Replit

### Replit Configuration
```toml
# .replit
[workflows.workflow]
name = "Project"
mode = "parallel"

[[workflows.workflow.tasks]]
task = "workflow.run"
args = "Flask Server"
```

### Environment Setup
```bash
# Environment variables di Replit Secrets
SESSION_SECRET=production_secret_key
DATABASE_URL=postgresql://username:password@host:port/database
STRIPE_SECRET_KEY=sk_live_your_live_stripe_key
MIDTRANS_SERVER_KEY=live_server_key
MIDTRANS_CLIENT_KEY=live_client_key
```

### Running on Replit
1. **Import Project** ke Replit
2. **Setup Secrets** dengan environment variables
3. **Click Run Button** atau jalankan `python server.py`
4. **Access Application** via Replit's web view

## 📞 Store Information

- **Nama Toko**: Hurtrock Music Store
- **Alamat**: Jl Gegerkalong Girang Complex Darut Tauhid Kav 22, Kota Bandung
- **Telepon**: 0821-1555-8035
- **Jam Operasional**: 
  - Senin–Jumat: 09.30–18.00
  - Sabtu: 09.30–17.00
  - Minggu: Tutup
- **Spesialisasi**: Alat musik Rock/Metal, Gitar, Bass, Drum, Amplifier

## 🤝 Contributing

### Development Guidelines
1. Fork repository dan create feature branch
2. Follow PEP 8 coding standards
3. Test dengan server.py untuk compatibility
4. Update documentation sesuai perubahan
5. Submit pull request dengan deskripsi lengkap

## 📄 License

**MIT License**

Copyright © 2025 **Fajar Julyana**

*Made with ❤️ by Fajar Julyana*

## 🎸 What's New in Latest Version

### Version 2.0.0 - Unified Server & Enhanced Upload

**🚀 Major Improvements**:
- **Unified Server**: `server.py` menjalankan Flask + Django secara bersamaan
- **Enhanced Product Upload**: Multi-image upload dengan drag & drop
- **Real-time Image Preview**: Preview gambar sebelum upload dengan thumbnail selection
- **Package Ready**: Siap untuk packaging dengan PyInstaller
- **Improved Setup**: Install scripts yang lebih robust dan universal
- **Better Error Handling**: Error handling yang lebih comprehensive

**🎨 UI/UX Enhancements**:
- **Advanced Image Upload Interface**: Drag & drop dengan preview real-time
- **Thumbnail Selection**: Pilih gambar thumbnail dengan radio button
- **Image Management**: Remove, reorder, dan manage multiple gambar
- **Responsive Upload Area**: Interface yang responsif untuk semua device
- **Upload Progress**: Visual feedback untuk proses upload

**⚡ Performance & Stability**:
- **Unified Architecture**: Mengurangi konflik antara Flask dan Django
- **Better Resource Management**: Memory dan CPU usage yang lebih efisien
- **Improved Startup**: Startup time yang lebih cepat
- **Enhanced Error Recovery**: Auto-recovery untuk service failures

---

**Hurtrock Music Store** - *Rock Your Music Journey with Modern Technology* [MUSIC]🎸[START]