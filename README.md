# Hurtrock Music Store - Sistem E-commerce Alat Musik

Aplikasi e-commerce modern untuk toko alat musik dengan tema Rock/Metal menggunakan font Metal Mania dan Rock Salt, sistem manajemen produk, shopping cart, pembayaran terintegrasi Stripe & Midtrans, dan live chat support dengan arsitektur microservice yang dapat di-package sebagai executable.

## Daftar Isi
- [Teknologi yang Digunakan](#teknologi-yang-digunakan)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Diagram ERD, DFD, dan Flowchart](#diagram-erd-dfd-dan-flowchart)
- [Fitur Utama](#fitur-utama)
- [Instalasi dan Konfigurasi](#instalasi-dan-konfigurasi)
- [Panduan Penggunaan](#panduan-penggunaan)
- [Deployment di Replit](#deployment-di-replit)
- [Packaging untuk Distribusi](#packaging-untuk-distribusi)
- [Kontribusi](#kontribusi)
- [Lisensi](#lisensi)

## Teknologi yang Digunakan

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
- **Python-Barcode 0.15.1** - Generasi barcode untuk label pengiriman
- **QRCode[PIL] 7.4.2** - Generasi QR code untuk tracking

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

## Arsitektur Sistem

### Flask-Only Architecture

Hurtrock Music Store saat ini menggunakan arsitektur **Flask-only** dengan chat service yang disederhanakan untuk stabilitas dan kemudahan deployment.

```
┌─────────────────────────────────────────────────────────┐
│                    main.py                              │
│                 (Flask Application)                     │
└─────────────────────┬───────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼────┐      ┌────▼────┐      ┌────▼────┐
│ Web    │      │ Admin   │      │ Static  │
│ Store  │      │ Panel   │      │ Files   │
│ :5000  │      │ :5000   │      │ Server  │
└───┬────┘      └────┬────┘      └─────────┘
    │                │                
    ▼                ▼                
┌───────────────────────────┐
│      PostgreSQL           │
│     Main Database         │
└───────────────────────────┘
```

### Component Architecture

- **Flask Application Layer**: main.py mengelola semua routes dan logic
- **Presentation Layer**: Jinja2 Templates + Bootstrap 5 + Vanilla JS
- **Business Logic Layer**: Flask Routes + Service Classes
- **Data Access Layer**: SQLAlchemy ORM + PostgreSQL
- **Integration Layer**: Payment Gateways + Email Services

## 📊 Diagram Sistem Komprehensif

### Entity Relationship Diagram (ERD)

```
    ┌─────────────────┐         ┌─────────────────┐
    │      User       │         │    Category     │
    │─────────────────│         │─────────────────│
    │ id (PK)         │         │ id (PK)         │
    │ email (UK)      │         │ name            │
    │ password_hash   │         │ description     │
    │ name            │         │ image_url       │
    │ phone           │         │ is_active       │
    │ address         │         │ created_at      │
    │ active          │         └─────────────────┘
    │ role            │                   │
    │ created_at      │                   │
    └─────────────────┘                   │
            │                             │
            │                             │
    ┌─────────────────┐         ┌─────────────────┐
    │    CartItem     │         │    Product      │
    │─────────────────│         │─────────────────│
    │ id (PK)         │         │ id (PK)         │
    │ user_id (FK)    │◄────────│ name            │
    │ product_id (FK) │────────►│ description     │
    │ quantity        │         │ price           │
    │ created_at      │         │ stock_quantity  │
    └─────────────────┘         │ image_url       │
            │                   │ brand           │
            │                   │ model           │
    ┌─────────────────┐         │ is_active       │
    │     Order       │         │ is_featured     │
    │─────────────────│         │ category_id(FK) │
    │ id (PK)         │         │ supplier_id(FK) │
    │ user_id (FK)    │◄────────│ weight          │
    │ total_amount    │         │ created_at      │
    │ status          │         └─────────────────┘
    │ tracking_number │                   │
    │ courier_service │                   │
    │ shipping_cost   │                   │
    │ payment_method  │                   │
    │ created_at      │         ┌─────────────────┐
    └─────────────────┘         │   OrderItem     │
            │                   │─────────────────│
            │                   │ id (PK)         │
            └───────────────────►│ order_id (FK)   │
                                │ product_id (FK) │◄───┘
                                │ quantity        │
                                │ price           │
                                └─────────────────┘

            ┌─────────────────┐
            │    Supplier     │
            │─────────────────│
            │ id (PK)         │
            │ name            │
            │ contact_person  │
            │ email           │
            │ phone           │
            │ address         │
            │ company         │
            │ is_active       │
            │ created_at      │
            └─────────────────┘
                    │
                    └──────────┐
                              │
            ┌─────────────────┐ │
            │ StoreProfile    │ │
            │─────────────────│ │
            │ id (PK)         │ │
            │ store_name      │ │
            │ store_tagline   │ │
            │ store_address   │ │
            │ store_phone     │ │
            │ store_email     │ │
            │ logo_url        │ │
            │ primary_color   │ │
            │ is_active       │ │
            └─────────────────┘ │
                               │
            ┌─────────────────┐ │
            │PaymentConfig    │ │
            │─────────────────│ │
            │ id (PK)         │ │
            │ provider        │ │
            │ is_active       │ │
            │ stripe_pub_key  │ │
            │ stripe_sec_key  │ │
            │ midtrans_key    │ │
            └─────────────────┘ │
                               │
                               │
            ┌─────────────────┐ │
            │ ShippingService │ │
            │─────────────────│ │
            │ id (PK)         │ │
            │ name            │ │
            │ code (UK)       │ │
            │ base_price      │ │
            │ price_per_kg    │ │
            │ min_days        │ │
            │ max_days        │ │
            │ is_active       │ │
            └─────────────────┘ │
                               │
                               │
                               └─► Connected to Product
```

### Data Flow Diagram (DFD) Level 0 - Context Diagram

```
    ┌─────────────┐                                    ┌─────────────┐
    │   Customer  │                                    │    Admin    │
    │             │                                    │             │
    └─────────────┘                                    └─────────────┘
           │                                                   │
           │ Browse Products,                                  │ Manage Products,
           │ Place Orders,                                     │ Process Orders,
           │ Make Payments                                     │ View Analytics
           │                                                   │
           ▼                                                   ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                                                                 │
    │            HURTROCK MUSIC STORE SYSTEM                         │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
           │                                                   │
           │ Product Info,                                     │ Reports,
           │ Order Status,                                     │ Dashboards,
           │ Payment Confirmation                              │ Notifications
           │                                                   │
           ▼                                                   ▼
    ┌─────────────┐                                    ┌─────────────┐
    │   Customer  │                                    │    Admin    │
    │  Response   │                                    │  Response   │
    └─────────────┘                                    └─────────────┘

           ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
           │  Payment    │         │  Courier    │         │    Email    │
           │  Gateway    │         │  Services   │         │   Service   │
           │             │         │             │         │             │
           └─────────────┘         └─────────────┘         └─────────────┘
                  ▲                        ▲                        ▲
                  │                        │                        │
                  │ Payment Request        │ Shipping Request       │ Email Notifications
                  │                        │                        │
                  └────────────────────────┼────────────────────────┘
                                          │
                                          ▼
                                 ┌─────────────┐
                                 │   SYSTEM    │
                                 │             │
                                 └─────────────┘
```

### Data Flow Diagram (DFD) Level 1 - System Decomposition

```
    Customer ──► Web Interface ──► User Management ──► User Database
       │             │                    │
       │             │                    │
       └─────────────┼──► Product Mgmt ───┼──► Product Database
                     │         │          │
                     │         │          │
                     │         └──────────┼──► Category Database
                     │                    │
                     │                    │
                     └──► Order Management ──► Order Database
                             │          │
                             │          │
                             ▼          ▼
                     Payment Processing ──► Payment Gateway
                             │
                             │
                             ▼
                     Report Generator ──► Analytics Database
                             │
                             │
                             ▼
                     Admin Dashboard ◄── Admin User
```

### Flowchart Customer Journey

```
    START
      │
      ▼
  ┌─────────┐    NO   ┌─────────┐
  │ Login?  │────────►│Register │
  └─────────┘         │ /Login  │
      │YES            └─────────┘
      ▼                    │
  ┌─────────┐             │
  │ Browse  │◄────────────┘
  │Products │
  └─────────┘
      │
      ▼
  ┌─────────┐    NO   ┌─────────┐
  │Product  │────────►│Continue │
  │Selected?│         │Browsing │
  └─────────┘         └─────────┘
      │YES                 │
      ▼                    │
  ┌─────────┐             │
  │Add to   │             │
  │Cart     │             │
  └─────────┘             │
      │                   │
      ▼                   │
  ┌─────────┐    NO      │
  │Ready to │────────────┘
  │Checkout?│
  └─────────┘
      │YES
      ▼
  ┌─────────┐
  │Fill     │
  │Shipping │
  │Info     │
  └─────────┘
      │
      ▼
  ┌─────────┐
  │Select   │
  │Payment  │
  │Method   │
  └─────────┘
      │
      ▼
  ┌─────────┐
  │Process  │
  │Payment  │
  └─────────┘
      │
      ▼
  ┌─────────┐    FAIL   ┌─────────┐
  │Payment  │──────────►│Show     │
  │Success? │           │Error &  │
  └─────────┘           │Retry    │
      │SUCCESS          └─────────┘
      ▼                      │
  ┌─────────┐               │
  │Success  │               │
  │Page     │               │
  └─────────┘               │
      │                     │
      ▼                     │
  ┌─────────┐              │
  │Track    │              │
  │Order    │              │
  └─────────┘              │
      │                    │
      ▼                    │
     END ◄─────────────────┘
```

### Flowchart Admin Product Management

```
    START (Admin Login)
           │
           ▼
    ┌─────────────┐
    │  Product    │
    │ Dashboard   │
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │Select Action│
    └─────────────┘
           │
           ├──── Create ────► Fill Form ────► Upload Images ────► Save ────► Success
           │                     │                │              │
           │                     │                │              │
           │                     └── Validate ◄───┘              │
           │                           │                         │
           │                           └── Show Errors ─────────┘
           │
           ├──── Edit ────► Select Product ────► Load Data ────► Edit Form ────► Update
           │                     │                   │              │
           │                     │                   │              │
           │                     │                   └─── Save ◄────┘
           │                     │                         │
           │                     │                         │
           │                     │                    ┌─────────┐
           │                     │                    │Success? │
           │                     │                    └─────────┘
           │                     │                         │
           │                     │                         │  NO
           │                     │                         │   │
           │                     │                         │   └── Show Error
           │                     │                         │
           │                     │                         └── Success Message
           │                     │
           ├──── View ────► Select Product ────► Display Details ────► View Analytics
           │
           └──── Delete ────► Select Product ────► Confirm Delete ────► Delete ────► Success
                                     │                    │
                                     │               NO   │
                                     │                    │
                                     │                    └── Cancel
                                     │
                                     └── Return to List
```

### Flowchart Order Processing

```
    New Order Received
           │
           ▼
    ┌─────────────┐
    │  Validate   │
    │   Order     │
    └─────────────┘
           │
           ▼
    ┌─────────────┐    INVALID
    │   Valid?    │──────────────► Reject Order ──► Send Email ──► END
    └─────────────┘
           │VALID
           ▼
    ┌─────────────┐
    │ Check Stock │
    └─────────────┘
           │
           ▼
    ┌─────────────┐    INSUFFICIENT
    │Stock Avail? │──────────────► Wait for Restock ──► Notify Customer
    └─────────────┘                        │
           │AVAILABLE                      │
           ▼                               │
    ┌─────────────┐                       │
    │  Confirm    │                       │
    │  Payment    │                       │
    └─────────────┘                       │
           │                               │
           ▼                               │
    ┌─────────────┐    FAILED             │
    │Payment OK?  │──────────────► Payment Failed ──► Notify ──► Retry/Cancel
    └─────────────┘
           │SUCCESS
           ▼
    ┌─────────────┐
    │  Generate   │
    │  Invoice    │
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │  Prepare    │
    │ Packaging   │
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │   Print     │
    │Shipping     │
    │   Label     │
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │   Assign    │
    │  Courier    │
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │  Generate   │
    │ Tracking #  │
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │  Package &  │
    │    Ship     │
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │    Send     │
    │ Notification│
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │   Update    │
    │   Status:   │
    │   Shipped   │
    └─────────────┘
           │
           ▼
    ┌─────────────┐
    │   Monitor   │
    │  Delivery   │
    └─────────────┘
           │
           ▼
    ┌─────────────┐    NOT YET
    │ Delivered?  │──────────────► Check Progress ──┐
    └─────────────┘                                 │
           │YES                                     │
           ▼                                        │
    ┌─────────────┐                                │
    │Mark as      │                                │
    │Delivered    │                                │
    └─────────────┘                                │
           │                                        │
           ▼                                        │
    ┌─────────────┐                                │
    │Send         │                                │
    │Completion   │                                │
    │Email        │                                │
    └─────────────┘                                │
           │                                        │
           ▼                                        │
    ┌─────────────┐                                │
    │ Order       │◄───────────────────────────────┘
    │ Complete    │
    └─────────────┘
           │
           ▼
          END
```

### Use Case Diagram

```
    Customer Use Cases:
    ┌─────────────────────────────────────┐
    │ • Browse Products                   │
    │ • Manage Shopping Cart              │
    │ • Checkout & Payment                │
    │ • Track Orders                      │
    │ • Manage Profile                    │
    │ • View Order History                │
    │ • Switch Light/Dark Theme           │
    └─────────────────────────────────────┘
                        │
                        ▼
    ┌─────────────────────────────────────┐
    │         HURTROCK SYSTEM             │
    └─────────────────────────────────────┘
                        │
                        ▼
    ┌─────────────────────────────────────┐
    │ Admin Use Cases:                    │
    │ • Manage Products                   │
    │ • Manage Categories                 │
    │ • Manage Users                      │
    │ • Manage Suppliers                  │
    │ • Configure Payments                │
    │ • Store Settings                    │
    │ • Analytics & Reports               │
    │ • Inventory Management              │
    │ • Process Orders                    │
    │ • Update Shipping Status            │
    │ • Generate Labels                   │
    │ • View Order Analytics              │
    └─────────────────────────────────────┘
```

### Arsitektur Deployment di Replit

```
    ┌─────────────────────────────────────────────────────┐
    │                 REPLIT ENVIRONMENT                  │
    │                                                     │
    │  ┌─────────────────────────────────────────────────┐│
    │  │               main.py                            ││
    │  │         (Flask Application)                     ││
    │  │              Port 5000                          ││
    │  └─────────────────────────────────────────────────┘│
    │                        │                            │
    │  ┌─────────────────────────────────────────────────┐│
    │  │           PostgreSQL Database                   ││
    │  │          (Replit Database)                      ││
    │  └─────────────────────────────────────────────────┘│
    │                        │                            │
    │  ┌─────────────────────────────────────────────────┐│
    │  │            Static Files                         ││
    │  │        (CSS, JS, Images)                        ││
    │  └─────────────────────────────────────────────────┘│
    │                        │                            │
    │  ┌─────────────────────────────────────────────────┐│
    │  │         Environment Variables                   ││
    │  │       (Secrets Management)                      ││
    │  └─────────────────────────────────────────────────┘│
    └─────────────────────────────────────────────────────┘
                             │
                             ▼
    ┌─────────────────────────────────────────────────────┐
    │              External Services                      │
    │                                                     │
    │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
    │  │   Stripe    │ │  Midtrans   │ │    Email    │    │
    │  │     API     │ │     API     │ │   Service   │    │
    │  └─────────────┘ └─────────────┘ └─────────────┘    │
    └─────────────────────────────────────────────────────┘
```

### Technology Stack Diagram

```
    Frontend Layer:
    ┌─────────────────────────────────────────────────────┐
    │ HTML5 │ CSS3/Bootstrap │ JavaScript │ Font Awesome │
    └─────────────────────────────────────────────────────┘
                             │
                             ▼
    Template Engine:
    ┌─────────────────────────────────────────────────────┐
    │              Jinja2 Templates                       │
    └─────────────────────────────────────────────────────┘
                             │
                             ▼
    Backend Framework:
    ┌─────────────────────────────────────────────────────┐
    │ Flask 3.1.2 │ Flask-Login │ Flask-WTF │ Werkzeug  │
    └─────────────────────────────────────────────────────┘
                             │
                             ▼
    Database Layer:
    ┌─────────────────────────────────────────────────────┐
    │        SQLAlchemy ORM │ PostgreSQL Database        │
    └─────────────────────────────────────────────────────┘
                             │
                             ▼
    Integration Layer:
    ┌─────────────────────────────────────────────────────┐
    │  Stripe API │ Midtrans API │ Image Processing     │
    └─────────────────────────────────────────────────────┘
                             │
                             ▼
    Deployment Platform:
    ┌─────────────────────────────────────────────────────┐
    │                 Replit Platform                     │
    └─────────────────────────────────────────────────────┘
```

## Fitur Utama

### Sisi Pengguna (Customer)

#### Autentikasi & Profil
- ✅ Registrasi akun baru dengan validasi email
- ✅ Login/logout sistem dengan session management
- ✅ Manajemen profil pengguna dengan update data

#### Katalog Produk
- ✅ Browse produk berdasarkan kategori
- ✅ Search real-time dengan autocomplete
- ✅ Detail produk dengan galeri gambar multi-image
- ✅ Filter dan sorting produk (harga, nama, kategori)
- ✅ Featured products highlighting

#### Shopping Cart
- ✅ Add to cart functionality dengan AJAX
- ✅ Update quantity items secara real-time
- ✅ Remove items dari cart
- ✅ Subtotal calculation otomatis
- ✅ Cart persistence dalam session

#### Payment & Checkout
- ✅ Integrasi dengan Stripe payment gateway
- ✅ Integrasi dengan Midtrans payment gateway
- ✅ Checkout process yang aman dengan CSRF protection
- ✅ Order confirmation dengan order tracking
- ✅ Payment success page dengan order details

#### Theme & UX
- ✅ Light/Dark mode toggle dengan smooth transitions
- ✅ Responsive mobile-first design
- ✅ Glass morphism UI effects dengan backdrop blur
- ✅ Rock/Metal themed fonts (Metal Mania & Rock Salt)
- ✅ Dynamic hero images (light/dark mode)
- ✅ Theme preference persistence dalam localStorage

### Sisi Admin

#### Dashboard Analytics
- ✅ Total products, orders, users statistics
- ✅ Today's sales dan monthly sales tracking
- ✅ Recent orders overview dengan status
- ✅ Best selling products analytics
- ✅ Low stock alerts dan notifications

#### Product Management
- ✅ CRUD operations untuk produk dengan multi-image upload
- ✅ Drag & drop image upload dengan preview real-time
- ✅ Thumbnail selection untuk gambar utama
- ✅ Image compression otomatis untuk optimasi storage
- ✅ Kategori management dengan hierarki
- ✅ Stock quantity tracking dengan alert
- ✅ Featured products marking
- ✅ Product search dan filtering

#### Order Processing
- ✅ View all orders dengan pagination
- ✅ Order status management (pending, paid, shipped, delivered)
- ✅ Customer information access
- ✅ Order details dengan item breakdown
- ✅ Thermal label printing untuk shipping dengan barcode/QR code

#### User Management
- ✅ User list dengan role management
- ✅ Add new users dengan admin privileges
- ✅ User activity tracking
- ✅ Account activation/deactivation

#### Store Configuration
- ✅ Store profile management
- ✅ Payment gateway configuration
- ✅ Shipping services setup
- ✅ Supplier management
- ✅ Category management

## Instalasi dan Konfigurasi

### Persyaratan Sistem

**Minimum Requirements**:
- Python 3.11+
- PostgreSQL 12+ atau SQLite
- 4GB RAM
- 2GB disk space

**Recommended**:
- Python 3.12+
- PostgreSQL 15+
- 8GB RAM
- 10GB disk space

### Instalasi Otomatis (Direkomendasikan)

#### Universal Installation (Linux/macOS/Replit)
```bash
chmod +x install.sh
./install.sh
```

#### Linux Server Installation
```bash
chmod +x install-linux.sh
./install-linux.sh
```

### Instalasi Manual

#### 1. Clone Repository
```bash
git clone https://github.com/your-repo/hurtrock-music-store.git
cd hurtrock-music-store
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Setup Environment Variables
```bash
# Buat file .env
cat > .env << EOF
SESSION_SECRET=your_very_secure_secret_key_here
DATABASE_URL=postgresql://user:password@host:port/dbname
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
MIDTRANS_SERVER_KEY=your_midtrans_server_key
MIDTRANS_CLIENT_KEY=your_midtrans_client_key
FLASK_ENV=development
FLASK_DEBUG=1
EOF
```

#### 4. Setup Database
```bash
# Migrasi database
python migrate_db.py

# Load sample data
python sample_data.py
```

#### 5. Jalankan Aplikasi

**Production Mode (Direkomendasikan)**:
```bash
python main.py
```

**Development Mode dengan auto-reload**:
```bash
FLASK_ENV=development python main.py
```

### Akses Aplikasi

Aplikasi akan berjalan di:
- **Main App**: `http://0.0.0.0:5000`
- **Admin Panel**: `http://0.0.0.0:5000/admin`

### Default Admin Access
- **Email**: admin@hurtrock.com
- **Password**: admin123

## Panduan Penggunaan

### Untuk Customer

1. **Registrasi**: Kunjungi `/register` untuk membuat akun baru
2. **Browse Produk**: Jelajahi katalog di `/products`
3. **Add to Cart**: Tambahkan produk ke keranjang dan checkout
4. **Payment**: Gunakan Stripe/Midtrans untuk pembayaran aman
5. **Theme**: Toggle light/dark mode sesuai preferensi
6. **Track Orders**: Monitor status pesanan di `/orders`

### Untuk Admin

1. **Dashboard**: Akses `/admin` untuk overview analytics
2. **Products**: Kelola produk dengan multi-image upload
3. **Orders**: Monitor dan update status orders
4. **Users**: User management dan role assignment
5. **Store Settings**: Konfigurasi toko dan payment gateway
6. **Analytics**: Generate reports dan export data

### Untuk Developer

#### File Structure
```
hurtrock-music-store/
├── main.py              # Main Flask application
├── models.py            # Database models
├── database.py          # Database configuration
├── migrate_db.py        # Database migration script
├── sample_data.py       # Sample data loader
├── static/              # Static assets
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
├── templates/           # Jinja2 templates
│   ├── base.html        # Base template
│   ├── index.html       # Homepage
│   ├── admin/           # Admin templates
│   └── ...
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Deployment di Replit

### Konfigurasi Replit

File `.replit` sudah dikonfigurasi untuk menjalankan Flask application:

```toml
[workflows]
workflow_name = "Flask App"
mode = "sequential"

[[workflows.tasks]]
task = "shell.exec"
args = "python main.py"
```

### Environment Setup di Replit

1. **Buka Secrets Tab** di Replit
2. **Tambahkan Environment Variables**:
   - `SESSION_SECRET`: your_production_secret_key
   - `DATABASE_URL`: postgresql://username:password@host:port/database
   - `STRIPE_SECRET_KEY`: sk_live_your_live_stripe_key
   - `MIDTRANS_SERVER_KEY`: live_server_key
   - `MIDTRANS_CLIENT_KEY`: live_client_key

### Menjalankan di Replit

1. **Import Project** ke Replit
2. **Setup Secrets** dengan environment variables
3. **Click Run Button** atau jalankan `python main.py`
4. **Access Application** via Replit's web view

### Publishing di Replit

Untuk mempublikasikan aplikasi:
1. Klik tab "Deployments"
2. Pilih "Deploy from latest commit"
3. Tunggu proses deployment selesai
4. Aplikasi akan tersedia di URL publik

## Security Features

### Application Security
- **CSRF Protection** pada semua forms dengan Flask-WTF
- **Password Hashing** menggunakan Werkzeug PBKDF2
- **Secure Sessions** dengan HTTPS-only cookies di production
- **SQL Injection Protection** via SQLAlchemy ORM
- **Input Validation** dan sanitization pada semua endpoints
- **Role-based Access Control** untuk admin features

### Production Security
- **HTTPS Enforcement** di production deployment
- **SameSite Cookie** protection untuk CSRF prevention
- **HTTPOnly Cookies** untuk session security
- **Environment Variable** protection untuk sensitive data

## Informasi Toko

- **Nama Toko**: Hurtrock Music Store
- **Tagline**: Merchandise and music instruments store
- **Alamat**: Jl Gegerkalong Girang Complex Darut Tauhid Kav 22, Kota Bandung
- **Telepon**: 0821-1555-8035
- **Jam Operasional**: 
  - Senin–Jumat: 09.30–18.00
  - Sabtu: 09.30–17.00
  - Minggu: Tutup
- **Spesialisasi**: Alat musik Rock/Metal, Gitar, Bass, Drum, Amplifier

## Kontribusi

### Development Guidelines
1. Fork repository dan create feature branch
2. Follow PEP 8 coding standards
3. Test dengan main.py untuk compatibility
4. Update documentation sesuai perubahan
5. Submit pull request dengan deskripsi lengkap

### Testing
```bash
# Run Flask application
python main.py

# Test database connection
python -c "from database import db; print('Database OK')"
```

## Troubleshooting

### Common Issues

**Aplikasi tidak bisa start**:
```bash
# Cek Flask app
python main.py

# Cek dependencies
pip check

# Cek database connection
python migrate_db.py
```

**Database connection issues**:
```bash
# Test database connection
python migrate_db.py

# Reset database dengan sample data
python migrate_db.py && python sample_data.py
```

**Theme/Static files issues**:
```bash
# Cek static files
ls -la static/css/style.css
ls -la static/js/script.js
ls -la static/images/
```

## Lisensi

**MIT License**

Copyright (c) 2025 **Fajar Julyana**

*Made with ❤️ by Fajar Julyana*

## What's New in Latest Version

### Version 2.5.0 - Enhanced Theme & UI Polish

**🎨 Major UI/UX Improvements**:
- **Perfect Light/Dark Theme**: Hero images yang berbeda untuk setiap tema
- **Seamless Transitions**: Smooth color transitions tanpa flickering
- **Professional Glass Effects**: Navbar dengan backdrop blur yang konsisten
- **Typography Harmony**: Font yang selaras dengan tema rock klasik
- **Responsive Hero Section**: No gap, perfect alignment dengan navbar

**🚀 Performance Enhancements**:
- **Optimized Image Loading**: Lazy loading untuk hero images
- **CSS Optimization**: Reduced redundancy dan improved load times
- **Theme Persistence**: LocalStorage untuk user preferences
- **Mobile Optimization**: Perfect responsiveness pada semua device

**🔧 Technical Improvements**:
- **Clean Codebase**: Removed deprecated chat service dependencies
- **Simplified Architecture**: Focus pada Flask-only untuk stability
- **Better Error Handling**: Graceful fallbacks untuk theme switching
- **Enhanced Documentation**: Updated README dengan diagram ASCII art

**🎯 UI Features**:
- **Dynamic Hero Images**: 
  - Light mode: Pop modern bright theme (860.jpeg)
  - Dark mode: Classic rock studio theme (Vintage_music_studio_hero_18c6c600.png)
- **Consistent Color Palette**: Orange (#ff6b35) dan colors yang harmonis
- **Professional Layout**: Clean spacing dan typography hierarchy
- **Enhanced Navbar**: Glass morphism dengan perfect blur effects

---

**Hurtrock Music Store** - *Rock Your Music Journey with Modern Technology* 🎸