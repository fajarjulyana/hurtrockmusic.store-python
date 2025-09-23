
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
        decimal length
        decimal width
        decimal height
        int minimum_stock
        int low_stock_threshold
        datetime created_at
    }
    
    ProductImage {
        int id PK
        int product_id FK
        string image_url
        boolean is_thumbnail
        int display_order
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
        int shipping_service_id FK
        decimal shipping_cost
        text shipping_address
        string payment_method
        int estimated_delivery_days
        datetime created_at
        datetime updated_at
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
        text notes
        boolean is_active
        datetime created_at
    }
    
    ShippingService {
        int id PK
        string name
        string code UK
        decimal base_price
        decimal price_per_kg
        decimal price_per_km
        decimal volume_factor
        int min_days
        int max_days
        boolean is_active
        datetime created_at
    }
    
    ChatRoom {
        int id PK
        string name UK
        int buyer_id FK
        string buyer_name
        string buyer_email
        boolean is_active
        datetime created_at
    }
    
    ChatMessage {
        int id PK
        int room_id FK
        int user_id FK
        string user_name
        string user_email
        text message
        string sender_type
        int product_id FK
        boolean is_read
        boolean is_deleted
        datetime created_at
        datetime updated_at
    }
    
    StoreProfile {
        int id PK
        string store_name
        string store_tagline
        text store_address
        string store_city
        string store_postal_code
        string store_phone
        string store_email
        string store_website
        string branch_name
        string branch_code
        string business_license
        string tax_number
        string logo_url
        string primary_color
        string secondary_color
        text operating_hours
        string facebook_url
        string instagram_url
        string whatsapp_number
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    PaymentConfiguration {
        int id PK
        string provider
        boolean is_active
        boolean is_sandbox
        string midtrans_client_key
        string midtrans_server_key
        string midtrans_merchant_id
        string stripe_publishable_key
        string stripe_secret_key
        string callback_finish_url
        string callback_unfinish_url
        string callback_error_url
        string notification_url
        datetime created_at
        datetime updated_at
    }
    
    RestockOrder {
        int id PK
        int supplier_id FK
        string status
        decimal total_amount
        text notes
        datetime order_date
        datetime expected_date
        datetime received_date
        int created_by FK
        datetime created_at
    }
    
    RestockOrderItem {
        int id PK
        int restock_order_id FK
        int product_id FK
        int quantity_ordered
        int quantity_received
        decimal unit_cost
    }
    
    User ||--o{ CartItem : "has many"
    User ||--o{ Order : "places"
    User ||--o{ ChatMessage : "sends"
    User ||--o{ ChatRoom : "participates"
    User ||--o{ RestockOrder : "creates"
    
    Category ||--o{ Product : "contains"
    Supplier ||--o{ Product : "supplies"
    Supplier ||--o{ RestockOrder : "receives from"
    
    Product ||--o{ ProductImage : "has many"
    Product ||--o{ CartItem : "added to"
    Product ||--o{ OrderItem : "ordered as"
    Product ||--o{ ChatMessage : "referenced in"
    Product ||--o{ RestockOrderItem : "restocked as"
    
    Order ||--o{ OrderItem : "contains"
    Order }o--|| ShippingService : "shipped via"
    
    ChatRoom ||--o{ ChatMessage : "contains"
    
    RestockOrder ||--o{ RestockOrderItem : "contains"
```

### Data Flow Diagram (DFD) Level 0 - Context Diagram

```mermaid
graph TB
    Customer[👤 Customer]
    Admin[👤 Admin/Staff]
    System[🏪 Hurtrock Music Store System]
    PaymentGW[💳 Payment Gateway]
    CourierAPI[🚚 Courier Services]
    EmailSvc[📧 Email Service]
    
    Customer --> |Browse Products, Place Orders, Chat| System
    System --> |Product Info, Order Status, Chat Response| Customer
    Admin --> |Manage Products, Process Orders, Analytics| System
    System --> |Reports, Dashboards, Notifications| Admin
    System --> |Payment Request| PaymentGW
    PaymentGW --> |Payment Confirmation| System
    System --> |Shipping Request| CourierAPI
    CourierAPI --> |Tracking Info| System
    System --> |Email Notifications| EmailSvc
    EmailSvc --> |Delivery Confirmation| System
    
    style Customer fill:#e3f2fd
    style Admin fill:#f3e5f5
    style System fill:#e8f5e8
    style PaymentGW fill:#fff3e0
    style CourierAPI fill:#f1f8e9
    style EmailSvc fill:#fce4ec
```

### Data Flow Diagram (DFD) Level 1 - System Decomposition

```mermaid
graph TB
    subgraph "External Entities"
        Customer[👤 Customer]
        Admin[👤 Admin]
        PaymentGW[💳 Payment Gateway]
        CourierAPI[🚚 Courier API]
    end
    
    subgraph "Hurtrock Music Store System"
        WebInterface[🌐 Web Interface]
        UserMgmt[👥 User Management]
        ProductMgmt[📦 Product Management]
        OrderMgmt[📋 Order Management]
        PaymentProc[💳 Payment Processing]
        ChatSvc[💬 Chat Service]
        InventoryMgmt[📊 Inventory Management]
        ReportGen[📈 Report Generator]
    end
    
    subgraph "Data Stores"
        UserDB[(👥 User Database)]
        ProductDB[(📦 Product Database)]
        OrderDB[(📋 Order Database)]
        ChatDB[(💬 Chat Database)]
        ConfigDB[(⚙️ Configuration Database)]
    end
    
    Customer --> WebInterface
    WebInterface --> UserMgmt
    WebInterface --> ProductMgmt
    WebInterface --> OrderMgmt
    WebInterface --> ChatSvc
    
    Admin --> WebInterface
    WebInterface --> InventoryMgmt
    WebInterface --> ReportGen
    
    UserMgmt <--> UserDB
    ProductMgmt <--> ProductDB
    OrderMgmt <--> OrderDB
    ChatSvc <--> ChatDB
    PaymentProc <--> ConfigDB
    InventoryMgmt <--> ProductDB
    
    OrderMgmt --> PaymentProc
    PaymentProc --> PaymentGW
    PaymentGW --> PaymentProc
    PaymentProc --> OrderMgmt
    
    OrderMgmt --> CourierAPI
    CourierAPI --> OrderMgmt
    
    ReportGen --> OrderDB
    ReportGen --> ProductDB
    ReportGen --> UserDB
```

### Flowchart Customer Journey

```mermaid
flowchart TD
    A[🚀 Kunjungi Website] --> B{🔑 Sudah Login?}
    B -->|Tidak| C[📝 Daftar/Login]
    B -->|Ya| D[🛍️ Jelajahi Produk]
    C --> D
    
    D --> E{💡 Produk Dipilih?}
    E -->|Tidak| D
    E -->|Ya| F[🛒 Tambah ke Keranjang]
    
    F --> G{✅ Siap Checkout?}
    G -->|Tidak| D
    G -->|Ya| H[📋 Isi Info Pengiriman]
    
    H --> I[💳 Pilih Metode Pembayaran]
    I --> J[⏳ Proses Pembayaran]
    
    J --> K{💰 Pembayaran Berhasil?}
    K -->|Gagal| L[❌ Tampil Error & Coba Lagi]
    L --> I
    K -->|Berhasil| M[🎉 Halaman Sukses Bayar]
    
    M --> N[📦 Tracking Pesanan]
    N --> O[💬 Chat Support<br/>Opsional]
    O --> P[🏁 Selesai]
    N --> P
    
    style A fill:#e1f5fe
    style P fill:#c8e6c9
    style K fill:#fff3e0
    style L fill:#ffebee
```

### Flowchart Admin Product Management

```mermaid
flowchart TD
    A[🔐 Login Admin] --> B[📦 Product Management Dashboard]
    B --> C{🎯 Pilih Aksi}
    
    C --> D[➕ Create New Product]
    C --> E[✏️ Edit Product]
    C --> F[👁️ View Product]
    C --> G[🗑️ Delete Product]
    
    D --> H[📝 Fill Product Form]
    H --> I[🖼️ Upload Images]
    I --> J[⚙️ Set Details & Categories]
    J --> K[✅ Validate Data]
    K --> L{📋 Data Valid?}
    L -->|No| M[❌ Show Validation Errors]
    M --> H
    L -->|Yes| N[💾 Save New Product]
    N --> O[🎉 Success Message]
    
    E --> P[🔍 Select Product]
    P --> Q[📄 Load Product Data]
    Q --> R[✏️ Edit Form]
    R --> S[💾 Update Changes]
    S --> T{✅ Update Success?}
    T -->|No| U[❌ Show Error]
    U --> R
    T -->|Yes| V[🎉 Update Success]
    
    F --> W[🔍 Select Product]
    W --> X[👁️ Display Product Details]
    X --> Y[📊 View Analytics]
    
    G --> Z[🔍 Select Product]
    Z --> AA[⚠️ Confirm Deletion]
    AA --> BB{❓ Confirm Delete?}
    BB -->|No| CC[🚫 Cancel Delete]
    BB -->|Yes| DD[🗑️ Delete Product]
    DD --> EE[🎉 Delete Success]
    
    O --> FF[📋 Return to Product List]
    V --> FF
    Y --> FF
    CC --> FF
    EE --> FF
    FF --> B
    
    style A fill:#e3f2fd
    style O fill:#c8e6c9
    style V fill:#c8e6c9
    style EE fill:#c8e6c9
    style M fill:#ffebee
    style U fill:#ffebee
```

### Flowchart Order Processing

```mermaid
flowchart TD
    A[📦 Pesanan Baru Diterima] --> B[✅ Validasi Detail Pesanan]
    B --> C{📋 Pesanan Valid?}
    C -->|Tidak| D[❌ Tolak Pesanan & Kirim Email]
    C -->|Ya| E[📊 Cek Stok Barang]
    
    E --> F{🏪 Stok Tersedia?}
    F -->|Tidak Cukup| G{🤔 Kirim Sebagian?}
    G -->|Tidak| H[📧 Notify Customer - Wait for Restock]
    G -->|Ya| I[📦 Proses Partial Shipment]
    F -->|Ya| J[💰 Konfirmasi Pembayaran]
    
    J --> K{💳 Payment Valid?}
    K -->|Tidak| L[❌ Payment Failed - Notify Customer]
    K -->|Ya| M[✅ Payment Confirmed]
    
    M --> N[📋 Generate Invoice]
    N --> O[📦 Prepare for Packaging]
    O --> P[📄 Print Shipping Label]
    P --> Q[🚚 Assign Courier Service]
    Q --> R[📱 Generate Tracking Number]
    R --> S[📦 Package & Ship]
    
    S --> T[📧 Send Shipping Notification]
    T --> U[📊 Update Order Status: Shipped]
    U --> V[🔄 Monitor Delivery Status]
    
    V --> W{📍 Delivered?}
    W -->|Tidak| X[⏰ Check Delivery Progress]
    X --> V
    W -->|Ya| Y[✅ Mark as Delivered]
    Y --> Z[📧 Send Completion Email]
    Z --> AA[🏁 Order Complete]
    
    I --> J
    H --> BB[⏰ Wait for Restock]
    BB --> E
    L --> CC[🔄 Retry Payment or Cancel]
    
    style A fill:#e1f5fe
    style AA fill:#c8e6c9
    style D fill:#ffebee
    style L fill:#ffebee
```

### Use Case Diagram

```mermaid
graph TB
    Customer[👤 Customer]
    Admin[👤 Admin]
    Staff[👤 Staff]
    
    subgraph "Customer Use Cases"
        UC1[🔍 Browse Products]
        UC2[🛒 Manage Shopping Cart]
        UC3[💳 Checkout & Payment]
        UC4[📦 Track Orders]
        UC5[💬 Chat with Support]
        UC6[👤 Manage Profile]
        UC7[📋 View Order History]
        UC8[⭐ Rate Products]
    end
    
    subgraph "Staff Use Cases"
        UC9[📋 Process Orders]
        UC10[📦 Update Shipping Status]
        UC11[🏷️ Generate Labels]
        UC12[💬 Customer Support Chat]
        UC13[📊 View Order Analytics]
    end
    
    subgraph "Admin Use Cases"
        UC14[📦 Manage Products]
        UC15[📂 Manage Categories]
        UC16[👥 Manage Users]
        UC17[🏪 Manage Suppliers]
        UC18[💳 Configure Payments]
        UC19[⚙️ Store Settings]
        UC20[📈 Analytics & Reports]
        UC21[📊 Inventory Management]
        UC22[🔄 Restock Management]
    end
    
    Customer --> UC1
    Customer --> UC2
    Customer --> UC3
    Customer --> UC4
    Customer --> UC5
    Customer --> UC6
    Customer --> UC7
    Customer --> UC8
    
    Staff --> UC9
    Staff --> UC10
    Staff --> UC11
    Staff --> UC12
    Staff --> UC13
    
    Admin --> UC14
    Admin --> UC15
    Admin --> UC16
    Admin --> UC17
    Admin --> UC18
    Admin --> UC19
    Admin --> UC20
    Admin --> UC21
    Admin --> UC22
```

### Arsitektur Deployment

```mermaid
graph TB
    subgraph "Production Environment"
        LB[⚖️ Load Balancer<br/>nginx/haproxy]
        
        subgraph "Application Layer"
            App1[🐍 Flask App Instance 1<br/>Port 5000]
            App2[🐍 Flask App Instance 2<br/>Port 5001]
            ChatApp[🗨️ Django Chat Service<br/>Port 8000]
        end
        
        subgraph "Database Layer"
            PG_Primary[(🐘 PostgreSQL Primary<br/>Main Database)]
            PG_Replica[(🐘 PostgreSQL Replica<br/>Read Only)]
            Redis_Cache[(⚡ Redis Cache<br/>Sessions & Chat)]
        end
        
        subgraph "Storage Layer"
            FileStorage[📁 File Storage<br/>Images & Documents]
            CDN[🌐 CDN<br/>Static Assets]
        end
        
        subgraph "Monitoring & Logging"
            Logs[📝 Centralized Logging]
            Monitor[📊 Application Monitoring]
            Alerts[🚨 Alert System]
        end
    end
    
    subgraph "External Services"
        StripeAPI[💳 Stripe API]
        MidtransAPI[💰 Midtrans API]
        CourierAPIs[🚚 Courier APIs<br/>JNE, J&T, SiCepat]
        EmailSvc[📧 Email Service<br/>SMTP/SendGrid]
    end
    
    Internet[🌍 Internet Traffic] --> LB
    LB --> App1
    LB --> App2
    LB --> ChatApp
    
    App1 --> PG_Primary
    App2 --> PG_Primary
    ChatApp --> PG_Primary
    
    App1 --> PG_Replica
    App2 --> PG_Replica
    
    App1 --> Redis_Cache
    App2 --> Redis_Cache
    ChatApp --> Redis_Cache
    
    PG_Primary -.-> PG_Replica
    
    App1 --> FileStorage
    App2 --> FileStorage
    FileStorage --> CDN
    
    App1 --> Logs
    App2 --> Logs
    ChatApp --> Logs
    
    App1 --> Monitor
    App2 --> Monitor
    Monitor --> Alerts
    
    App1 --> StripeAPI
    App1 --> MidtransAPI
    App1 --> CourierAPIs
    App1 --> EmailSvc
    
    style LB fill:#FF9800
    style App1 fill:#4CAF50
    style App2 fill:#4CAF50
    style ChatApp fill:#2196F3
    style PG_Primary fill:#336791
    style Redis_Cache fill:#DC382D
```

### Technology Stack Diagram

```mermaid
graph TB
    subgraph "Frontend Technologies"
        HTML[📄 HTML5]
        CSS[🎨 CSS3 + Bootstrap 5]
        JS[⚡ JavaScript ES6+]
        Jinja[🔧 Jinja2 Templates]
        FA[🎯 Font Awesome Icons]
    end
    
    subgraph "Backend Technologies"
        Flask[🐍 Flask 3.1.2]
        Django[🐍 Django 5.2.6]
        SQLAlchemy[🗄️ SQLAlchemy ORM]
        Channels[📡 Django Channels]
        Werkzeug[🔐 Werkzeug Security]
    end
    
    subgraph "Database Technologies"
        PostgreSQL[🐘 PostgreSQL]
        Redis[⚡ Redis]
        Migrations[🔄 Flask-Migrate]
    end
    
    subgraph "Integration Technologies"
        Stripe[💳 Stripe API]
        Midtrans[💰 Midtrans API]
        ReportLab[📄 ReportLab PDF]
        Pillow[🖼️ Pillow Image Processing]
        WebSocket[🔌 WebSocket Real-time]
    end
    
    subgraph "DevOps & Tools"
        Git[📊 Git Version Control]
        Docker[🐳 Docker Containers]
        Nginx[⚖️ Nginx Web Server]
        SSL[🔒 SSL/TLS Security]
    end
    
    HTML --> Flask
    CSS --> Flask
    JS --> Flask
    Jinja --> Flask
    FA --> Flask
    
    Flask --> SQLAlchemy
    Django --> Channels
    SQLAlchemy --> PostgreSQL
    Channels --> Redis
    
    Flask --> Stripe
    Flask --> Midtrans
    Flask --> ReportLab
    Flask --> Pillow
    Django --> WebSocket
    
    Flask --> Git
    Django --> Docker
    Docker --> Nginx
    Nginx --> SSL
    
    style Flask fill:#4CAF50
    style Django fill:#2196F3
    style PostgreSQL fill:#336791
    style Redis fill:#DC382D
```
         │CUKUP                      │
         │                      ┌────▼────┐
    ┌────▼────┐                │Backorder│
    │Reserve  │                │Item     │
    │Stok     │                └────┬────┘
    └────┬────┘                     │
         │                          │
    ┌────▼────┐                     │
    │Proses   │                     │
    │Pembayaran│                    │
    └────┬────┘                     │
         │                          │
    ┌────▼────┐    GAGAL      ┌─────▼──────┐
    │Bayar    │──────────────►│Kembalikan  │
    │Berhasil?│               │Stok        │
    └────┬────┘               │Batal Order │
         │BERHASIL            └────────────┘
         │
    ┌────▼────┐
    │Update   │
    │Jumlah   │
    │Stok     │
    └────┬────┘
         │
    ┌────▼────┐
    │Generate │
    │Invoice  │
    │& Label  │
    └────┬────┘
         │
    ┌────▼────┐
    │Kirim    │
    │Email    │
    │Konfirmasi│
    └────┬────┘
         │
    ┌────▼────┐
    │Update   │
    │Status   │
    │Pesanan  │
    └────┬────┘
         │
    ┌────▼────┐
    │ Pesanan │
    │Selesai  │
    └─────────┘
```

## Fitur Utama

### Sisi Pengguna (Customer)

#### Autentikasi & Profil
- Registrasi akun baru dengan validasi email
- Login/logout sistem dengan session management
- Manajemen profil pengguna dengan update data

#### Katalog Produk
- Browse produk berdasarkan kategori
- Search real-time dengan autocomplete
- Detail produk dengan galeri gambar multi-image
- Filter dan sorting produk (harga, nama, kategori)
- Featured products highlighting

#### Shopping Cart
- Add to cart functionality dengan AJAX
- Update quantity items secara real-time
- Remove items dari cart
- Subtotal calculation otomatis
- Cart persistence dalam session

#### Payment & Checkout
- Integrasi dengan Stripe payment gateway
- Integrasi dengan Midtrans payment gateway
- Checkout process yang aman dengan CSRF protection
- Order confirmation dengan order tracking
- Payment success page dengan order details

#### Live Chat Support
- Real-time chat dengan admin menggunakan WebSocket
- Product tagging dalam chat messages
- Chat history persistence
- Online/offline status indicators
- Floating chat widget

#### Theme & UX
- Light/Dark mode toggle dengan smooth transitions
- Responsive mobile-first design
- Glass morphism UI effects
- Rock/Metal themed fonts dan colors
- Theme preference persistence

### Sisi Admin

#### Dashboard Analytics
- Total products, orders, users statistics
- Today's sales dan monthly sales tracking
- Recent orders overview dengan status
- Best selling products analytics
- Pending chats notification

#### Product Management
- CRUD operations untuk produk dengan multi-image upload
- Drag & drop image upload dengan preview real-time
- Thumbnail selection untuk gambar utama
- Image compression otomatis untuk optimasi storage
- Kategori management dengan hierarki
- Stock quantity tracking dengan alert
- Featured products marking
- Product search dan filtering

#### Order Processing
- View all orders dengan pagination
- Order status management (pending, paid, shipped, delivered)
- Customer information access
- Order details dengan item breakdown
- Thermal label printing untuk shipping dengan barcode/QR code

#### User Management
- User list dengan role management
- Add new users dengan admin privileges
- User activity tracking
- Account activation/deactivation

#### Live Chat Management
- Real-time chat interface dengan customers
- Chat room management
- Message history dan archiving
- Product recommendation dalam chat
- Microservice architecture untuk scalability

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

**Menggunakan Unified Server (Direkomendasikan)**:
```bash
python server.py
```

**Menggunakan Start Script**:
```bash
./start_server.sh
```

**Development Mode (Flask saja)**:
```bash
python main.py
```

### Akses Aplikasi

Aplikasi akan berjalan di:
- **Main App**: `http://0.0.0.0:5000`
- **Chat Service**: `http://0.0.0.0:8000`
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
5. **Chat**: Live chat support dengan admin via WebSocket
6. **Theme**: Toggle light/dark mode sesuai preferensi

### Untuk Admin

1. **Dashboard**: Akses `/admin` untuk overview analytics
2. **Products**: Kelola produk dengan multi-image upload
3. **Orders**: Monitor dan update status orders
4. **Users**: User management dan role assignment
5. **Chat**: Respond ke customer inquiries real-time
6. **Analytics**: Generate reports dan export data

### Untuk Developer

Lihat dokumentasi lengkap di:
- [Developer Guide](dokumentasi/DEVELOPER_GUIDE.md)
- [API Documentation](dokumentasi/DEVELOPER_GUIDE.md#api-documentation)

### Untuk Maintainer

Lihat panduan maintenance di:
- [Maintainer Guide](dokumentasi/MAINTAINER_GUIDE.md)

## Deployment di Replit

### Konfigurasi Replit

File `.replit` sudah dikonfigurasi untuk menjalankan unified server:

```toml
[workflows.workflow]
name = "Hurtrock Server"
mode = "sequential"

[[workflows.workflow.tasks]]
task = "shell.exec"
args = "python server.py"
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
3. **Click Run Button** atau jalankan `python server.py`
4. **Access Application** via Replit's web view

### Publishing di Replit

Untuk mempublikasikan aplikasi:
1. Klik tab "Deployments"
2. Pilih "Deploy from latest commit"
3. Tunggu proses deployment selesai
4. Aplikasi akan tersedia di URL publik

## Packaging untuk Distribusi

### Persiapan untuk PyInstaller

Aplikasi telah didesain untuk dapat di-package sebagai executable:

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
- **CORS Configuration** untuk microservice communication

## Informasi Toko

- **Nama Toko**: Hurtrock Music Store
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
3. Test dengan server.py untuk compatibility
4. Update documentation sesuai perubahan
5. Submit pull request dengan deskripsi lengkap

### Testing
```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=main tests/
```

## Troubleshooting

### Common Issues

**Aplikasi tidak bisa start**:
```bash
# Cek service status
python server.py

# Cek dependencies
pip check

# Cek database connection
python -c "from database import db; print('Database OK')"
```

**Database connection issues**:
```bash
# Test database connection
python migrate_db.py

# Reset database
python migrate_db.py --reset
```

## Lisensi

**MIT License**

Copyright (c) 2025 **Fajar Julyana**

*Made with ❤️ by Fajar Julyana*

## What's New in Latest Version

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

**Hurtrock Music Store** - *Rock Your Music Journey with Modern Technology* 🎸
