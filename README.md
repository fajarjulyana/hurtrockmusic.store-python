
# 🎵 Hurtrock Music Store

Aplikasi e-commerce modern untuk toko alat musik dengan tema Rock/Metal menggunakan font Metal Mania dan Rock Salt, sistem manajemen produk, shopping cart, pembayaran terintegrasi Stripe, dan live chat support.

## 🚀 Teknologi yang Digunakan

### Backend Framework
- **Flask 3.1.2** - Web framework Python yang ringan dan fleksibel
- **SQLAlchemy 2.0.43** - ORM untuk manajemen database
- **Flask-Login 0.6.3** - Sistem autentikasi dan session management
- **Flask-Migrate 4.1.0** - Database migration tool
- **Flask-WTF 1.2.2** - Form handling dan CSRF protection
- **Flask-SocketIO 5.5.1** - Real-time WebSocket communication untuk live chat

### Database & Storage
- **PostgreSQL** - Database utama untuk data produk, user, dan transaksi
- **Psycopg2-Binary 2.9.10** - PostgreSQL adapter untuk Python

### Payment Processing
- **Stripe 12.5.1** - Gateway pembayaran internasional yang aman

### Image & Document Processing
- **Pillow 11.3.0** - Library untuk kompresi dan manipulasi gambar
- **ReportLab 4.4.4** - PDF generation untuk invoice dan laporan
- **OpenPyXL 3.1.5** - Excel export untuk data analytics

### Frontend & Real-time Features
- **Bootstrap 5.3.0** - CSS framework untuk responsive design
- **Font Awesome 6.0.0** - Icon library
- **Socket.IO Client** - Real-time bidirectional communication
- **Metal Mania & Rock Salt Fonts** - Google Fonts untuk tema Rock/Metal

### Security & Utilities
- **Werkzeug 3.1.3** - Password hashing dan security utilities
- **Email-Validator 2.3.0** - Validasi format email
- **Python-Dotenv 1.1.1** - Environment variable management

## 🎨 Tema dan Desain

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

## ✨ Fitur yang Tersedia

### 🛍️ Sisi Pengguna (Customer)
1. **Autentikasi & Profil**
   - ✅ Registrasi akun baru dengan validasi email
   - ✅ Login/logout sistem dengan session management
   - ✅ Manajemen profil pengguna dengan update data

2. **Katalog Produk**
   - ✅ Browse produk berdasarkan kategori
   - ✅ Search real-time dengan autocomplete
   - ✅ Detail produk dengan galeri gambar
   - ✅ Filter dan sorting produk (harga, nama, kategori)
   - ✅ Featured products highlighting

3. **Shopping Cart**
   - ✅ Add to cart functionality dengan AJAX
   - ✅ Update quantity items secara real-time
   - ✅ Remove items dari cart
   - ✅ Subtotal calculation otomatis
   - ✅ Cart persistence dalam session

4. **Payment & Checkout**
   - ✅ Integrasi dengan Stripe payment gateway
   - ✅ Checkout process yang aman dengan CSRF protection
   - ✅ Order confirmation dengan order tracking
   - ✅ Payment success page dengan order details

5. **Live Chat Support**
   - ✅ Real-time chat dengan admin menggunakan Socket.IO
   - ✅ Product tagging dalam chat messages
   - ✅ Chat history persistence
   - ✅ Online/offline status indicators

6. **Theme & UX**
   - ✅ Light/Dark mode toggle dengan smooth transitions
   - ✅ Responsive mobile-first design
   - ✅ Glass morphism UI effects
   - ✅ Rock/Metal themed fonts dan colors
   - ✅ Theme preference persistence

### 👨‍💼 Sisi Admin
1. **Dashboard Analytics**
   - ✅ Total products, orders, users statistics
   - ✅ Today's sales dan monthly sales tracking
   - ✅ Recent orders overview dengan status
   - ✅ Best selling products analytics
   - ✅ Pending chats notification

2. **Product Management**
   - ✅ CRUD operations untuk produk
   - ✅ Multi-image upload dengan kompresi otomatis
   - ✅ Kategori management dengan hierarki
   - ✅ Stock quantity tracking
   - ✅ Featured products marking
   - ✅ Product search dan filtering

3. **Order Processing**
   - ✅ View all orders dengan pagination
   - ✅ Order status management (pending, paid, shipped, delivered)
   - ✅ Customer information access
   - ✅ Order details dengan item breakdown

4. **User Management**
   - ✅ User list dengan role management
   - ✅ Add new users dengan admin privileges
   - ✅ User activity tracking
   - ✅ Account activation/deactivation

5. **Live Chat Management**
   - ✅ Real-time chat interface dengan customers
   - ✅ Chat room management
   - ✅ Message history dan archiving
   - ✅ Product recommendation dalam chat

6. **Analytics & Reporting**
   - ✅ Sales analytics dengan chart visualization
   - ✅ PDF report generation dengan ReportLab
   - ✅ Excel export untuk data analysis
   - ✅ Product performance metrics

## 🚧 Fitur dalam Pengembangan / Bug Fixes Needed

### Known Issues
1. **Image Management**
   - ❌ Hero image tidak ditemukan (404 error pada /static/images/hero-music.jpg)
   - ❌ Image upload validation perlu ditingkatkan

2. **Socket.IO CORS Issues**
   - ❌ Origin validation errors untuk Replit domains
   - ❌ WebSocket connection failures pada production

3. **Email System**
   - ❌ Email notification untuk order belum diimplementasi
   - ❌ Password reset via email belum tersedia

### Planned Features
- 📧 Email notifications dengan template HTML
- 📊 Advanced analytics dengan chart.js integration
- 🔄 Order tracking system dengan status updates
- 📱 PWA (Progressive Web App) support
- 🔍 Elasticsearch integration untuk advanced search
- 📦 Inventory management dengan low stock alerts

## 📊 System Architecture

### Technology Stack
```mermaid
graph TB
    subgraph "Frontend Layer"
        A[HTML5/Jinja2 Templates]
        B[Bootstrap 5 + Custom CSS]
        C[JavaScript ES6 + Socket.IO Client]
    end
    
    subgraph "Application Layer"
        D[Flask 3.1.2 Application]
        E[Flask-Login Authentication]
        F[Flask-WTF Forms & CSRF]
        G[Flask-SocketIO WebSockets]
    end
    
    subgraph "Business Logic"
        H[User Management System]
        I[Product Catalog Engine]
        J[Shopping Cart Logic]
        K[Order Processing Pipeline]
        L[Live Chat System]
    end
    
    subgraph "Data Layer"
        M[SQLAlchemy 2.0.43 ORM]
        N[(PostgreSQL Database)]
    end
    
    subgraph "External Services"
        O[Stripe Payment API]
        P[Google Fonts CDN]
        Q[Image Compression Engine]
    end
    
    A --> D
    B --> D
    C --> G
    D --> H
    D --> I
    D --> J
    D --> K
    G --> L
    H --> M
    I --> M
    J --> M
    K --> M
    L --> M
    M --> N
    K --> O
    A --> P
    I --> Q
```

### Database Schema
```mermaid
erDiagram
    User ||--o{ CartItem : has
    User ||--o{ Order : places
    User ||--o{ ChatRoom : creates
    Product ||--o{ CartItem : contains
    Product ||--o{ OrderItem : includes
    Product ||--o{ ChatMessage : tagged_in
    Category ||--o{ Product : categorizes
    Order ||--o{ OrderItem : contains
    ChatRoom ||--o{ ChatMessage : contains

    User {
        int id PK
        string email UK
        string password_hash
        string name
        string phone
        text address
        boolean active
        boolean is_admin
        boolean is_staff
        datetime created_at
    }

    Category {
        int id PK
        string name
        text description
        string image_url
        boolean is_active
        datetime created_at
    }

    Product {
        int id PK
        string name
        text description
        decimal price
        int stock_quantity
        string image_url
        string brand
        string model
        boolean is_active
        boolean is_featured
        int category_id FK
        datetime created_at
    }

    Order {
        int id PK
        int user_id FK
        decimal total_amount
        string status
        text shipping_address
        string payment_method
        datetime created_at
        datetime updated_at
    }

    ChatRoom {
        int id PK
        int user_id FK
        boolean is_active
        datetime created_at
        datetime last_message_at
    }

    ChatMessage {
        int id PK
        int chat_room_id FK
        string sender_type
        text message
        int product_id FK
        boolean is_read
        datetime created_at
    }
```

## 🛠️ Instalasi & Setup

### Environment Requirements
- Python 3.11+
- PostgreSQL 12+
- UV package manager (recommended) atau pip

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
```

### 3. Install Dependencies
```bash
# Menggunakan UV (recommended)
uv sync

# Atau menggunakan pip
pip install -e .
```

### 4. Database Setup
```bash
# Setup database dan create tables
python migrate_db.py

# Load sample data (optional)
python sample_data.py
```

### 5. Run Application
```bash
# Development mode
python main.py

# Atau dengan UV
uv run python main.py

# Production mode (di Replit)
# Gunakan workflow "Flask Server" yang sudah dikonfigurasi
```

Aplikasi akan berjalan di `http://0.0.0.0:5000`

## 📱 Usage Guide

### Default Admin Access
- **Email**: admin@hurtrock.com
- **Password**: admin123
- **Admin Panel**: `/admin`

### Customer Flow
1. **Registrasi**: `/register` - Daftar akun baru
2. **Browse**: `/products` - Lihat katalog produk
3. **Cart**: Add produk ke cart dan proceed checkout
4. **Payment**: Integrasi Stripe untuk pembayaran aman
5. **Chat**: Live chat support dengan admin
6. **Theme**: Toggle light/dark mode sesuai preferensi

### Admin Flow
1. **Dashboard**: `/admin` - Overview analytics dan metrics
2. **Products**: Kelola produk, kategori, dan inventory
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

### Production Security
- **HTTPS Enforcement** di Replit deployment
- **SameSite Cookie** protection untuk CSRF prevention
- **HTTPOnly Cookies** untuk session security
- **Environment Variable** protection untuk sensitive data

## 🌐 Deployment di Replit

### Configuration
- **Port**: 5000 (auto-forwarded to 80/443)
- **Database**: PostgreSQL via environment variable
- **Static Files**: Served via Flask built-in server
- **WebSockets**: Socket.IO dengan CORS configuration
- **Security**: Production-ready security headers

### Replit Workflow
```toml
[workflows.workflow]
name = "Flask Server"
author = "agent"

[[workflows.workflow.tasks]]
task = "shell.exec"
args = "python3 main.py"
waitForPort = 5000
```

### Environment Setup
```bash
# Production environment variables di Replit Secrets
SESSION_SECRET=production_secret_key
DATABASE_URL=postgresql://username:password@host:port/database
STRIPE_SECRET_KEY=sk_live_your_live_stripe_key
REPLIT_DEPLOYMENT=production
```

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
3. Tambahkan tests untuk fitur baru
4. Update documentation sesuai perubahan
5. Submit pull request dengan deskripsi lengkap

### Code Structure
```
├── main.py              # Application entry point
├── models.py            # SQLAlchemy database models
├── database.py          # Database configuration
├── migrate_db.py        # Database migration script
├── sample_data.py       # Sample data loader
├── templates/           # Jinja2 HTML templates
├── static/             # CSS, JS, dan static assets
└── pyproject.toml      # Python dependencies
```

## 📄 License

**MIT License**

Copyright © 2025 **Fajar Julyana**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**Made with ❤️ by Fajar Julyana**

## 🎸 Design Philosophy

Hurtrock Music Store menggabungkan semangat musik Rock/Metal dengan teknologi web modern:

### Design Principles
- **Rock Aesthetics**: Metal Mania dan Rock Salt fonts untuk karakter yang kuat
- **Orange-Black Harmony**: Skema warna yang energik dan bold
- **Glass Morphism**: Efek modern yang tetap mempertahankan edge
- **Responsive First**: Mobile-friendly tanpa mengorbankan desktop experience
- **Performance Focused**: Image optimization dan lazy loading
- **Accessibility**: WCAG 2.1 compliance untuk semua user

### Technical Philosophy
- **Security First**: Semua input divalidasi, CSRF protected, secure sessions
- **Scalability Ready**: Database optimization, connection pooling, caching strategy
- **Real-time Experience**: WebSocket untuk instant communication
- **Modern Standards**: ES6+, HTML5, CSS3, Progressive Enhancement
- **Developer Experience**: Clean code, modular structure, comprehensive docs

---

**Hurtrock Music Store** - *Rock Your Music Journey with Modern Technology* 🎵🎸🚀
