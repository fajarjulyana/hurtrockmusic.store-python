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

```mermaid
graph TD
    MainApp[main.py<br/>Flask Application]
    
    WebStore[Web Store<br/>Port 5000]
    AdminPanel[Admin Panel<br/>Port 5000]
    StaticFiles[Static Files<br/>Server]
    
    Database[(PostgreSQL<br/>Main Database)]
    
    MainApp --> WebStore
    MainApp --> AdminPanel
    MainApp --> StaticFiles
    
    WebStore --> Database
    AdminPanel --> Database
```

### Component Architecture

- **Flask Application Layer**: main.py mengelola semua routes dan logic
- **Presentation Layer**: Jinja2 Templates + Bootstrap 5 + Vanilla JS
- **Business Logic Layer**: Flask Routes + Service Classes
- **Data Access Layer**: SQLAlchemy ORM + PostgreSQL
- **Integration Layer**: Payment Gateways + Email Services

## 📊 Diagram Sistem Komprehensif

### Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    User {
        int id PK
        string email UK
        string password_hash
        string name
        string phone
        text address
        boolean active
        string role
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
        int supplier_id FK
        decimal weight
        datetime created_at
    }

    CartItem {
        int id PK
        int user_id FK
        int product_id FK
        int quantity
        datetime created_at
    }

    Order {
        int id PK
        int user_id FK
        decimal total_amount
        string status
        string tracking_number
        string courier_service
        decimal shipping_cost
        string payment_method
        datetime created_at
    }

    OrderItem {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }

    Supplier {
        int id PK
        string name
        string contact_person
        string email
        string phone
        text address
        string company
        boolean is_active
        datetime created_at
    }

    StoreProfile {
        int id PK
        string store_name
        string store_tagline
        text store_address
        string store_phone
        string store_email
        string logo_url
        string primary_color
        boolean is_active
    }

    PaymentConfiguration {
        int id PK
        string provider
        boolean is_active
        string stripe_pub_key
        string stripe_sec_key
        string midtrans_key
    }

    ShippingService {
        int id PK
        string name
        string code UK
        decimal base_price
        decimal price_per_kg
        int min_days
        int max_days
        boolean is_active
    }

    User ||--o{ CartItem : has
    User ||--o{ Order : creates
    Category ||--o{ Product : contains
    Product ||--o{ CartItem : added_to
    Product ||--o{ OrderItem : ordered_in
    Order ||--o{ OrderItem : contains
    Supplier ||--o{ Product : supplies
```

### Data Flow Diagram (DFD) Level 0 - Context Diagram

```mermaid
graph TD
    Customer[Customer]
    Admin[Admin]
    System[HURTROCK MUSIC STORE SYSTEM]
    PaymentGateway[Payment Gateway]
    CourierServices[Courier Services]
    EmailService[Email Service]

    Customer -->|Browse Products, Place Orders, Make Payments| System
    Admin -->|Manage Products, Process Orders, View Analytics| System
    
    System -->|Product Info, Order Status, Payment Confirmation| Customer
    System -->|Reports, Dashboards, Notifications| Admin
    
    System -->|Payment Request| PaymentGateway
    System -->|Shipping Request| CourierServices
    System -->|Email Notifications| EmailService
    
    PaymentGateway -->|Payment Response| System
    CourierServices -->|Shipping Status| System
    EmailService -->|Delivery Status| System
```

### Data Flow Diagram (DFD) Level 1 - System Decomposition

```mermaid
graph TD
    Customer[Customer]
    AdminUser[Admin User]
    
    WebInterface[Web Interface]
    UserMgmt[User Management]
    ProductMgmt[Product Management]
    OrderMgmt[Order Management]
    PaymentProc[Payment Processing]
    ReportGen[Report Generator]
    AdminDash[Admin Dashboard]
    
    UserDB[(User Database)]
    ProductDB[(Product Database)]
    CategoryDB[(Category Database)]
    OrderDB[(Order Database)]
    AnalyticsDB[(Analytics Database)]
    PaymentGW[Payment Gateway]
    
    Customer --> WebInterface
    WebInterface --> UserMgmt
    WebInterface --> ProductMgmt
    WebInterface --> OrderMgmt
    
    UserMgmt --> UserDB
    ProductMgmt --> ProductDB
    ProductMgmt --> CategoryDB
    OrderMgmt --> OrderDB
    OrderMgmt --> PaymentProc
    PaymentProc --> PaymentGW
    PaymentProc --> ReportGen
    ReportGen --> AnalyticsDB
    ReportGen --> AdminDash
    AdminUser --> AdminDash
```

### Flowchart Customer Journey

```mermaid
flowchart TD
    Start([START])
    Login{Login?}
    Register[Register/Login]
    Browse[Browse Products]
    ProductSelected{Product Selected?}
    ContinueBrowsing[Continue Browsing]
    AddToCart[Add to Cart]
    ReadyCheckout{Ready to Checkout?}
    FillShipping[Fill Shipping Info]
    SelectPayment[Select Payment Method]
    ProcessPayment[Process Payment]
    PaymentSuccess{Payment Success?}
    ShowError[Show Error & Retry]
    SuccessPage[Success Page]
    TrackOrder[Track Order]
    End([END])

    Start --> Login
    Login -->|NO| Register
    Login -->|YES| Browse
    Register --> Browse
    Browse --> ProductSelected
    ProductSelected -->|NO| ContinueBrowsing
    ProductSelected -->|YES| AddToCart
    ContinueBrowsing --> ProductSelected
    AddToCart --> ReadyCheckout
    ReadyCheckout -->|NO| ContinueBrowsing
    ReadyCheckout -->|YES| FillShipping
    FillShipping --> SelectPayment
    SelectPayment --> ProcessPayment
    ProcessPayment --> PaymentSuccess
    PaymentSuccess -->|FAIL| ShowError
    PaymentSuccess -->|SUCCESS| SuccessPage
    ShowError --> ContinueBrowsing
    SuccessPage --> TrackOrder
    TrackOrder --> End
```

### Flowchart Admin Product Management

```mermaid
flowchart TD
    Start([Admin Login])
    Dashboard[Product Dashboard]
    SelectAction[Select Action]
    
    %% Create Flow
    Create[Create]
    FillForm[Fill Form]
    UploadImages[Upload Images]
    Validate[Validate]
    SaveProduct[Save]
    ShowErrors[Show Errors]
    CreateSuccess[Success]
    
    %% Edit Flow
    Edit[Edit]
    SelectProduct[Select Product]
    LoadData[Load Data]
    EditForm[Edit Form]
    SaveEdit[Save]
    EditSuccess{Success?}
    ShowError[Show Error]
    SuccessMessage[Success Message]
    
    %% View Flow
    View[View]
    SelectViewProduct[Select Product]
    DisplayDetails[Display Details]
    ViewAnalytics[View Analytics]
    
    %% Delete Flow
    Delete[Delete]
    SelectDeleteProduct[Select Product]
    ConfirmDelete{Confirm Delete?}
    DeleteProduct[Delete]
    DeleteSuccess[Success]
    Cancel[Cancel]
    ReturnToList[Return to List]

    Start --> Dashboard
    Dashboard --> SelectAction
    
    SelectAction --> Create
    SelectAction --> Edit
    SelectAction --> View
    SelectAction --> Delete
    
    %% Create Path
    Create --> FillForm
    FillForm --> UploadImages
    UploadImages --> Validate
    Validate --> SaveProduct
    Validate --> ShowErrors
    ShowErrors --> FillForm
    SaveProduct --> CreateSuccess
    
    %% Edit Path
    Edit --> SelectProduct
    SelectProduct --> LoadData
    LoadData --> EditForm
    EditForm --> SaveEdit
    SaveEdit --> EditSuccess
    EditSuccess -->|YES| SuccessMessage
    EditSuccess -->|NO| ShowError
    ShowError --> EditForm
    
    %% View Path
    View --> SelectViewProduct
    SelectViewProduct --> DisplayDetails
    DisplayDetails --> ViewAnalytics
    
    %% Delete Path
    Delete --> SelectDeleteProduct
    SelectDeleteProduct --> ConfirmDelete
    ConfirmDelete -->|YES| DeleteProduct
    ConfirmDelete -->|NO| Cancel
    DeleteProduct --> DeleteSuccess
    Cancel --> ReturnToList
```

### Flowchart Order Processing

```mermaid
flowchart TD
    Start([New Order Received])
    ValidateOrder[Validate Order]
    Valid{Valid?}
    RejectOrder[Reject Order]
    SendEmail[Send Email]
    CheckStock[Check Stock]
    StockAvail{Stock Available?}
    WaitRestock[Wait for Restock]
    NotifyCustomer[Notify Customer]
    ConfirmPayment[Confirm Payment]
    PaymentOK{Payment OK?}
    PaymentFailed[Payment Failed]
    Notify[Notify]
    RetryCancel[Retry/Cancel]
    GenerateInvoice[Generate Invoice]
    PreparePackaging[Prepare Packaging]
    PrintLabel[Print Shipping Label]
    AssignCourier[Assign Courier]
    GenerateTracking[Generate Tracking #]
    PackageShip[Package & Ship]
    SendNotification[Send Notification]
    UpdateStatus[Update Status: Shipped]
    MonitorDelivery[Monitor Delivery]
    Delivered{Delivered?}
    CheckProgress[Check Progress]
    MarkDelivered[Mark as Delivered]
    SendCompletion[Send Completion Email]
    OrderComplete[Order Complete]
    End([END])

    Start --> ValidateOrder
    ValidateOrder --> Valid
    Valid -->|INVALID| RejectOrder
    Valid -->|VALID| CheckStock
    RejectOrder --> SendEmail
    SendEmail --> End
    
    CheckStock --> StockAvail
    StockAvail -->|INSUFFICIENT| WaitRestock
    StockAvail -->|AVAILABLE| ConfirmPayment
    WaitRestock --> NotifyCustomer
    NotifyCustomer --> CheckStock
    
    ConfirmPayment --> PaymentOK
    PaymentOK -->|FAILED| PaymentFailed
    PaymentOK -->|SUCCESS| GenerateInvoice
    PaymentFailed --> Notify
    Notify --> RetryCancel
    RetryCancel --> ConfirmPayment
    
    GenerateInvoice --> PreparePackaging
    PreparePackaging --> PrintLabel
    PrintLabel --> AssignCourier
    AssignCourier --> GenerateTracking
    GenerateTracking --> PackageShip
    PackageShip --> SendNotification
    SendNotification --> UpdateStatus
    UpdateStatus --> MonitorDelivery
    MonitorDelivery --> Delivered
    Delivered -->|NOT YET| CheckProgress
    Delivered -->|YES| MarkDelivered
    CheckProgress --> MonitorDelivery
    MarkDelivered --> SendCompletion
    SendCompletion --> OrderComplete
    OrderComplete --> End
```

### Use Case Diagram

```mermaid
graph TB
    Customer[Customer]
    Admin[Admin]
    System[HURTROCK SYSTEM]
    
    %% Customer Use Cases
    BrowseProducts[Browse Products]
    ManageCart[Manage Shopping Cart]
    Checkout[Checkout & Payment]
    TrackOrders[Track Orders]
    ManageProfile[Manage Profile]
    OrderHistory[View Order History]
    SwitchTheme[Switch Light/Dark Theme]
    
    %% Admin Use Cases
    ManageProducts[Manage Products]
    ManageCategories[Manage Categories]
    ManageUsers[Manage Users]
    ManageSuppliers[Manage Suppliers]
    ConfigurePayments[Configure Payments]
    StoreSettings[Store Settings]
    Analytics[Analytics & Reports]
    Inventory[Inventory Management]
    ProcessOrders[Process Orders]
    UpdateShipping[Update Shipping Status]
    GenerateLabels[Generate Labels]
    OrderAnalytics[View Order Analytics]
    
    %% Customer Connections
    Customer --> BrowseProducts
    Customer --> ManageCart
    Customer --> Checkout
    Customer --> TrackOrders
    Customer --> ManageProfile
    Customer --> OrderHistory
    Customer --> SwitchTheme
    
    %% Admin Connections
    Admin --> ManageProducts
    Admin --> ManageCategories
    Admin --> ManageUsers
    Admin --> ManageSuppliers
    Admin --> ConfigurePayments
    Admin --> StoreSettings
    Admin --> Analytics
    Admin --> Inventory
    Admin --> ProcessOrders
    Admin --> UpdateShipping
    Admin --> GenerateLabels
    Admin --> OrderAnalytics
    
    %% System Connections
    BrowseProducts --> System
    ManageCart --> System
    Checkout --> System
    TrackOrders --> System
    ManageProfile --> System
    OrderHistory --> System
    SwitchTheme --> System
    
    ManageProducts --> System
    ManageCategories --> System
    ManageUsers --> System
    ManageSuppliers --> System
    ConfigurePayments --> System
    StoreSettings --> System
    Analytics --> System
    Inventory --> System
    ProcessOrders --> System
    UpdateShipping --> System
    GenerateLabels --> System
    OrderAnalytics --> System
```

### Arsitektur Deployment di Replit

```mermaid
graph TB
    subgraph ReplitEnv[REPLIT ENVIRONMENT]
        FlaskApp[main.py<br/>Flask Application<br/>Port 5000]
        PostgreSQL[(PostgreSQL Database<br/>Replit Database)]
        StaticFiles[Static Files<br/>CSS, JS, Images]
        EnvVars[Environment Variables<br/>Secrets Management]
    end
    
    subgraph ExtServices[External Services]
        Stripe[Stripe API]
        Midtrans[Midtrans API]
        Email[Email Service]
    end
    
    FlaskApp --> PostgreSQL
    FlaskApp --> StaticFiles
    FlaskApp --> EnvVars
    
    FlaskApp --> Stripe
    FlaskApp --> Midtrans
    FlaskApp --> Email
```

### Technology Stack Diagram

```mermaid
graph TD
    Frontend[Frontend Layer<br/>HTML5 | CSS3/Bootstrap | JavaScript | Font Awesome]
    Template[Template Engine<br/>Jinja2 Templates]
    Backend[Backend Framework<br/>Flask 3.1.2 | Flask-Login | Flask-WTF | Werkzeug]
    Database[Database Layer<br/>SQLAlchemy ORM | PostgreSQL Database]
    Integration[Integration Layer<br/>Stripe API | Midtrans API | Image Processing]
    Deployment[Deployment Platform<br/>Replit Platform]
    
    Frontend --> Template
    Template --> Backend
    Backend --> Database
    Database --> Integration
    Integration --> Deployment
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

### Instalasi Cepat (Sangat Direkomendasikan) 🚀

#### Universal Start Script - Semua Platform
Script `start_arch_server.sh` adalah solusi one-click untuk semua environment:

```bash
# Memberikan permission dan menjalankan
chmod +x start_arch_server.sh
./start_arch_server.sh
```

**Fitur Start Script:**
- ✅ **Auto-Detection Environment** - Deteksi otomatis Linux, macOS, Windows (WSL), Replit
- ✅ **Dependency Installation** - Install semua dependencies yang diperlukan otomatis  
- ✅ **Environment Setup** - Generate .env file dengan konfigurasi aman
- ✅ **Database Setup** - Auto setup PostgreSQL atau SQLite fallback
- ✅ **Service Management** - Start/stop/restart Flask & Django chat service
- ✅ **GUI & CLI Mode** - Pilihan interface sesuai environment
- ✅ **Monitoring** - Live status monitoring dan logging

**Mode Operasi:**
```bash
# Mode otomatis (deteksi terbaik untuk environment)
./start_arch_server.sh

# Mode GUI (jika tersedia)
./start_arch_server.sh gui

# Mode CLI (command line)
./start_arch_server.sh cli

# Install dependencies saja
./start_arch_server.sh install

# Management commands
./start_arch_server.sh start     # Start services
./start_arch_server.sh stop      # Stop services  
./start_arch_server.sh restart   # Restart services
./start_arch_server.sh status    # Cek status
./start_arch_server.sh logs      # Live logs
```

**Replit Environment:**
Untuk environment Replit, script akan otomatis:
- Menggunakan environment variables yang sudah ada (DATABASE_URL, SESSION_SECRET)
- Skip virtual environment setup (menggunakan sistem Replit)
- Konfigurasi optimal untuk cloud hosting
- Auto-start dengan CLI mode

### Instalasi Alternatif

#### Universal Installation (Legacy)
```bash
chmod +x install.sh
./install.sh
```

#### Linux Server Installation (Legacy)
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