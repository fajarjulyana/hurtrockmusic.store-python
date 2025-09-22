
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

### Recent Bug Fixes ✅
1. **Database Schema Issues**
   - ✅ **FIXED**: Payment configurations database column errors (recurring_notification_url)
   - ✅ **FIXED**: Database migration and schema synchronization

2. **Real-time Chat Issues**
   - ✅ **FIXED**: Socket.IO CORS configuration for Replit domains
   - ✅ **FIXED**: Real-time chat refresh - buyers no longer need manual refresh when admin sends messages
   - ✅ **FIXED**: WebSocket connection stability in production environment

### Remaining Known Issues
1. **Image Management**
   - ❌ Hero image tidak ditemukan (404 error pada /static/images/hero-music.jpg)
   - ❌ Image upload validation perlu ditingkatkan

2. **Email System**
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

## 📊 Data Flow Diagram (DFD)

### Level 0 - Context Diagram
```mermaid
graph LR
    subgraph "External Entities"
        U[Customer/User]
        A[Admin/Staff]
        S[Stripe API]
        P[Payment Gateway]
    end
    
    subgraph "Hurtrock Music Store System"
        HMS[Hurtrock Music Store<br/>E-commerce Platform]
    end
    
    U -->|Browse Products, Place Orders, Chat| HMS
    HMS -->|Product Catalog, Order Status, Chat Response| U
    A -->|Manage Products, Orders, Users| HMS
    HMS -->|Analytics, Reports, Chat Notifications| A
    HMS -->|Payment Requests| S
    S -->|Payment Confirmation| HMS
    HMS -->|Transaction Data| P
    P -->|Payment Status| HMS
```

### Level 1 - System Processes
```mermaid
graph TB
    subgraph "User Processes"
        P1[1.0<br/>User Authentication<br/>& Registration]
        P2[2.0<br/>Product Catalog<br/>Management]
        P3[3.0<br/>Shopping Cart<br/>& Checkout]
        P4[4.0<br/>Order Processing<br/>& Tracking]
        P5[5.0<br/>Live Chat<br/>Support]
    end
    
    subgraph "Admin Processes"
        P6[6.0<br/>Admin Dashboard<br/>& Analytics]
        P7[7.0<br/>Product<br/>Management]
        P8[8.0<br/>Order<br/>Management]
        P9[9.0<br/>User<br/>Management]
        P10[10.0<br/>Chat<br/>Management]
    end
    
    subgraph "Data Stores"
        D1[(Users Database)]
        D2[(Products Database)]
        D3[(Orders Database)]
        D4[(Chat Database)]
        D5[(Categories Database)]
    end
    
    P1 --> D1
    P2 --> D2
    P2 --> D5
    P3 --> D2
    P3 --> D3
    P4 --> D3
    P5 --> D4
    P6 --> D1
    P6 --> D2
    P6 --> D3
    P7 --> D2
    P7 --> D5
    P8 --> D3
    P9 --> D1
    P10 --> D4
```

## 🔄 Business Process Flow Diagram

### Customer Purchase Flow
```mermaid
flowchart TD
    A[Customer visits website] --> B{User registered?}
    B -->|No| C[Register new account]
    B -->|Yes| D[Browse products]
    C --> D
    
    D --> E[Select product]
    E --> F[View product details]
    F --> G{Add to cart?}
    G -->|No| D
    G -->|Yes| H[Add to shopping cart]
    
    H --> I{Continue shopping?}
    I -->|Yes| D
    I -->|No| J[View cart]
    
    J --> K{Items in cart?}
    K -->|No| D
    K -->|Yes| L[Proceed to checkout]
    
    L --> M{Profile complete?}
    M -->|No| N[Complete profile<br/>address & phone]
    M -->|Yes| O[Select shipping method]
    N --> O
    
    O --> P[Select payment method]
    P --> Q[Process payment via Stripe]
    
    Q --> R{Payment successful?}
    R -->|No| S[Payment failed<br/>return to cart]
    R -->|Yes| T[Order confirmation]
    
    S --> J
    T --> U[Email confirmation]
    U --> V[Order tracking]
    V --> W[End]
```

### Admin Order Management Flow
```mermaid
flowchart TD
    A[New order received] --> B[Admin dashboard notification]
    B --> C[View order details]
    C --> D[Verify payment status]
    
    D --> E{Payment confirmed?}
    E -->|No| F[Contact customer<br/>via chat]
    E -->|Yes| G[Update order status<br/>to 'Processing']
    
    F --> H[Resolve payment issue]
    H --> G
    
    G --> I[Prepare order<br/>for shipping]
    I --> J[Update inventory]
    J --> K[Generate shipping label]
    K --> L[Update order status<br/>to 'Shipped']
    
    L --> M[Send tracking info<br/>to customer]
    M --> N{Order delivered?}
    N -->|No| O[Track shipment]
    N -->|Yes| P[Update order status<br/>to 'Delivered']
    
    O --> N
    P --> Q[Generate analytics report]
    Q --> R[End]
```

### Live Chat Support Flow
```mermaid
flowchart TD
    A[Customer opens chat widget] --> B[Connect to Socket.IO]
    B --> C[Join user room]
    C --> D[Load chat history]
    D --> E[Display chat interface]
    
    E --> F[Customer types message]
    F --> G{Include product tag?}
    G -->|Yes| H[Search and select product]
    G -->|No| I[Send message]
    H --> I
    
    I --> J[Message saved to database]
    J --> K[Emit to admin room via Socket.IO]
    K --> L[Admin receives notification]
    
    L --> M[Admin opens chat interface]
    M --> N[Admin types reply]
    N --> O[Reply saved to database]
    O --> P[Emit to user room via Socket.IO]
    
    P --> Q{Customer chat open?}
    Q -->|Yes| R[Display message instantly]
    Q -->|No| S[Update unread badge]
    
    R --> T[Conversation continues]
    S --> U[Customer opens chat]
    U --> R
    T --> V{Chat session ends?}
    V -->|No| F
    V -->|Yes| W[Close Socket.IO connection]
    W --> X[End]
```

## 🗃️ Enhanced Entity Relationship Diagram (ERD)

### Complete Database Schema
```mermaid
erDiagram
    User ||--o{ CartItem : "has many"
    User ||--o{ Order : "places many"
    User ||--o{ ChatRoom : "creates many"
    User ||--o{ PaymentConfiguration : "configures many"
    
    Product ||--o{ CartItem : "contained in many"
    Product ||--o{ OrderItem : "included in many"
    Product ||--o{ ChatMessage : "tagged in many"
    Product }|--|| Category : "belongs to one"
    Product }|--o| Supplier : "supplied by"
    
    Category ||--o{ Product : "contains many"
    
    Order ||--o{ OrderItem : "contains many"
    Order }|--o| ShippingService : "uses"
    
    ChatRoom ||--o{ ChatMessage : "contains many"
    
    Supplier ||--o{ Product : "supplies many"
    
    ShippingService ||--o{ Order : "ships many"
    
    PaymentConfiguration ||--o{ Order : "processes many"

    User {
        int id PK "Primary Key"
        string email UK "Unique Email"
        string password_hash "Hashed Password"
        string name "Full Name"
        string phone "Phone Number"
        text address "Full Address"
        boolean active "Account Status"
        string role "admin|staff|buyer"
        datetime created_at "Registration Date"
    }

    Category {
        int id PK "Primary Key"
        string name "Category Name"
        text description "Category Description"
        string image_url "Category Image"
        boolean is_active "Active Status"
        datetime created_at "Creation Date"
    }

    Product {
        int id PK "Primary Key"
        string name "Product Name"
        text description "Product Description"
        decimal price "Product Price"
        int stock_quantity "Available Stock"
        string image_url "Product Image"
        string brand "Brand Name"
        string model "Product Model"
        boolean is_active "Active Status"
        boolean is_featured "Featured Product"
        int category_id FK "Category Reference"
        int supplier_id FK "Supplier Reference"
        decimal weight "Weight in grams"
        decimal length "Length in cm"
        decimal width "Width in cm"
        decimal height "Height in cm"
        datetime created_at "Creation Date"
    }

    CartItem {
        int id PK "Primary Key"
        int user_id FK "User Reference"
        int product_id FK "Product Reference"
        int quantity "Item Quantity"
        datetime created_at "Added Date"
    }

    Order {
        int id PK "Primary Key"
        int user_id FK "User Reference"
        decimal total_amount "Order Total"
        string status "pending|paid|shipped|delivered|cancelled"
        string tracking_number "Shipment Tracking"
        int shipping_service_id FK "Shipping Service"
        decimal shipping_cost "Shipping Cost"
        text shipping_address "Delivery Address"
        string payment_method "Payment Method Used"
        datetime created_at "Order Date"
        datetime updated_at "Last Update"
    }

    OrderItem {
        int id PK "Primary Key"
        int order_id FK "Order Reference"
        int product_id FK "Product Reference"
        int quantity "Item Quantity"
        decimal price "Price at Purchase"
        datetime created_at "Creation Date"
    }

    ChatRoom {
        int id PK "Primary Key"
        int user_id FK "User Reference"
        boolean is_active "Room Status"
        datetime created_at "Creation Date"
        datetime last_message_at "Last Activity"
    }

    ChatMessage {
        int id PK "Primary Key"
        int chat_room_id FK "Chat Room Reference"
        string sender_type "user|admin"
        text message "Message Content"
        int product_id FK "Tagged Product"
        boolean is_read "Read Status"
        datetime created_at "Message Time"
    }

    Supplier {
        int id PK "Primary Key"
        string name "Supplier Name"
        string contact_person "Contact Person"
        string email "Contact Email"
        string phone "Contact Phone"
        text address "Supplier Address"
        string company "Company Name"
        text notes "Additional Notes"
        boolean is_active "Active Status"
        datetime created_at "Registration Date"
    }

    ShippingService {
        int id PK "Primary Key"
        string name "Service Name"
        string provider "Shipping Provider"
        decimal base_cost "Base Shipping Cost"
        decimal cost_per_kg "Cost per Kilogram"
        decimal cost_per_km "Cost per Kilometer"
        int min_days "Minimum Delivery Days"
        int max_days "Maximum Delivery Days"
        boolean is_active "Service Status"
        datetime created_at "Creation Date"
    }

    PaymentConfiguration {
        int id PK "Primary Key"
        string provider "stripe|midtrans"
        boolean is_active "Configuration Status"
        boolean is_sandbox "Sandbox Mode"
        string midtrans_client_key "Midtrans Client Key"
        string midtrans_server_key "Midtrans Server Key"
        string midtrans_merchant_id "Midtrans Merchant ID"
        string stripe_publishable_key "Stripe Public Key"
        string stripe_secret_key "Stripe Secret Key"
        string callback_finish_url "Finish Callback URL"
        string callback_unfinish_url "Unfinish Callback URL"
        string callback_error_url "Error Callback URL"
        string notification_url "Notification URL"
        string recurring_notification_url "Recurring Notification URL"
        string account_linking_url "Account Linking URL"
        datetime created_at "Creation Date"
        datetime updated_at "Last Update"
    }
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
