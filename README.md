
# [MUSIC] Hurtrock Music Store

Aplikasi e-commerce modern untuk toko alat musik dengan tema Rock/Metal menggunakan font Metal Mania dan Rock Salt, sistem manajemen produk, shopping cart, pembayaran terintegrasi Stripe & Midtrans, dan live chat support dengan arsitektur microservice.

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
   - [OK] Detail produk dengan galeri gambar
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
   - [OK] CRUD operations untuk produk
   - [OK] Multi-image upload dengan kompresi otomatis
   - [OK] Kategori management dengan hierarki
   - [OK] Stock quantity tracking
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

6. **Analytics & Reporting**
   - [OK] Sales analytics dengan chart visualization
   - [OK] PDF report generation dengan ReportLab
   - [OK] Excel export untuk data analysis
   - [OK] Product performance metrics

7. **Payment Configuration**
   - [OK] Stripe configuration management
   - [OK] Midtrans configuration management
   - [OK] Sandbox/Production mode switching
   - [OK] Payment callback handling

8. **Shipping Management**
   - [OK] Multiple courier services (JNE, J&T, SiCepat, POS)
   - [OK] Dynamic shipping cost calculation
   - [OK] Weight and volume-based pricing
   - [OK] Delivery time estimation

9. **Supplier Management**
   - [OK] Supplier database dengan contact information
   - [OK] Product assignment ke supplier
   - [OK] Purchase order tracking

10. **Restock Management**
    - [OK] Low stock alerts
    - [OK] Restock order creation
    - [OK] Inventory tracking
    - [OK] Supplier integration

## 🏗️ Arsitektur Sistem

### System Overview

Hurtrock Music Store menggunakan arsitektur **hybrid monolithic-microservice** dengan **Flask** sebagai framework utama dan **Django** untuk chat service.

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
│                      (Nginx)                           │
└─────────────────────┬───────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼────┐      ┌────▼────┐      ┌────▼────┐
│ Flask  │      │ Django  │      │ Static  │
│ Main   │◄────►│ Chat    │      │ Files   │
│ App    │      │ Service │      │ CDN     │
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

- **Presentation Layer**: Jinja2 Templates + Bootstrap 5 + Vanilla JS
- **Business Logic Layer**: Flask Routes + Service Classes
- **Data Access Layer**: SQLAlchemy ORM + PostgreSQL
- **Chat Service Layer**: Django + Django Channels + WebSocket
- **Integration Layer**: Payment Gateways + Email Services
- **Real-time Layer**: WebSocket untuk chat dan notifications

## 📊 Entity Relationship Diagram (ERD)

### Complete Database Schema
```mermaid
erDiagram
    User ||--o{ CartItem : "has many"
    User ||--o{ Order : "places many"
    User ||--o{ ChatRoom : "creates many"
    User ||--o{ PaymentConfiguration : "configures many"
    User ||--o{ RestockOrder : "creates many"
    
    Product ||--o{ CartItem : "contained in many"
    Product ||--o{ OrderItem : "included in many"
    Product ||--o{ ChatMessage : "tagged in many"
    Product ||--o{ RestockOrderItem : "restocked in many"
    Product }|--|| Category : "belongs to one"
    Product }|--o| Supplier : "supplied by"
    
    Category ||--o{ Product : "contains many"
    
    Order ||--o{ OrderItem : "contains many"
    Order }|--o| ShippingService : "uses"
    Order ||--o{ MidtransTransaction : "processed by"
    
    ChatRoom ||--o{ ChatMessage : "contains many"
    ChatRoom ||--o{ ChatSession : "hosts many"
    
    Supplier ||--o{ Product : "supplies many"
    Supplier ||--o{ RestockOrder : "receives many"
    
    ShippingService ||--o{ Order : "ships many"
    
    PaymentConfiguration ||--o{ Order : "processes many"
    
    RestockOrder ||--o{ RestockOrderItem : "contains many"

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
        string courier_service "Courier Name"
        int shipping_service_id FK "Shipping Service"
        decimal shipping_cost "Shipping Cost"
        text shipping_address "Delivery Address"
        string payment_method "Payment Method Used"
        int estimated_delivery_days "Delivery Estimate"
        datetime created_at "Order Date"
        datetime updated_at "Last Update"
    }

    OrderItem {
        int id PK "Primary Key"
        int order_id FK "Order Reference"
        int product_id FK "Product Reference"
        int quantity "Item Quantity"
        decimal price "Price at Purchase"
    }

    ChatRoom {
        int id PK "Primary Key"
        string name "Room Name"
        int buyer_id FK "Buyer Reference"
        string buyer_name "Buyer Name"
        string buyer_email "Buyer Email"
        boolean is_active "Room Status"
        datetime created_at "Creation Date"
    }

    ChatMessage {
        int id PK "Primary Key"
        int room_id FK "Chat Room Reference"
        int user_id FK "User Reference"
        string user_name "User Name"
        string user_email "User Email"
        text message "Message Content"
        string sender_type "buyer|admin|staff"
        int product_id FK "Tagged Product"
        boolean is_read "Read Status"
        boolean is_deleted "Deleted Status"
        datetime created_at "Message Time"
        datetime updated_at "Update Time"
    }

    ChatSession {
        int id PK "Primary Key"
        int room_id FK "Room Reference"
        int user_id FK "User Reference"
        string user_name "User Name"
        string user_email "User Email"
        string user_role "User Role"
        datetime started_at "Session Start"
        datetime ended_at "Session End"
        boolean is_active "Active Status"
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
        string code "Service Code"
        decimal base_price "Base Shipping Cost"
        decimal price_per_kg "Cost per Kilogram"
        decimal price_per_km "Cost per Kilometer"
        decimal volume_factor "Volume Factor"
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

    MidtransTransaction {
        int id PK "Primary Key"
        int order_id FK "Order Reference"
        string transaction_id UK "Transaction ID"
        decimal gross_amount "Transaction Amount"
        string payment_type "Payment Type"
        string transaction_status "Transaction Status"
        string fraud_status "Fraud Status"
        datetime settlement_time "Settlement Time"
        string snap_token "Snap Token"
        string snap_redirect_url "Redirect URL"
        text midtrans_response "Midtrans Response JSON"
        datetime created_at "Creation Date"
        datetime updated_at "Update Date"
    }

    RestockOrder {
        int id PK "Primary Key"
        int supplier_id FK "Supplier Reference"
        string status "pending|ordered|received|cancelled"
        decimal total_amount "Order Total"
        text notes "Order Notes"
        datetime order_date "Order Date"
        datetime expected_date "Expected Date"
        datetime received_date "Received Date"
        int created_by FK "Created By User"
        datetime created_at "Creation Date"
    }

    RestockOrderItem {
        int id PK "Primary Key"
        int restock_order_id FK "Restock Order Reference"
        int product_id FK "Product Reference"
        int quantity_ordered "Ordered Quantity"
        int quantity_received "Received Quantity"
        decimal unit_cost "Unit Cost"
    }

    StoreProfile {
        int id PK "Primary Key"
        string store_name "Store Name"
        string store_tagline "Store Tagline"
        text store_address "Store Address"
        string store_city "Store City"
        string store_postal_code "Postal Code"
        string store_phone "Store Phone"
        string store_email "Store Email"
        string store_website "Store Website"
        string branch_name "Branch Name"
        string branch_code "Branch Code"
        string branch_manager "Branch Manager"
        string business_license "Business License"
        string tax_number "Tax Number"
        string logo_url "Logo URL"
        string primary_color "Primary Color"
        string secondary_color "Secondary Color"
        text operating_hours "Operating Hours"
        string facebook_url "Facebook URL"
        string instagram_url "Instagram URL"
        string whatsapp_number "WhatsApp Number"
        boolean is_active "Active Status"
        datetime created_at "Creation Date"
        datetime updated_at "Update Date"
    }
```

## 🔄 Data Flow Diagram (DFD)

### Level 0 - Context Diagram
```mermaid
graph LR
    subgraph "External Entities"
        U[Customer/User]
        A[Admin/Staff]
        S[Stripe API]
        M[Midtrans API]
        CS[Chat Service]
    end
    
    subgraph "Hurtrock Music Store System"
        HMS[Hurtrock Music Store<br/>E-commerce Platform]
    end
    
    U -->|Browse Products, Place Orders, Chat| HMS
    HMS -->|Product Catalog, Order Status, Chat Response| U
    A -->|Manage Products, Orders, Users, Chat| HMS
    HMS -->|Analytics, Reports, Chat Notifications| A
    HMS -->|Payment Requests| S
    S -->|Payment Confirmation| HMS
    HMS -->|Payment Requests| M
    M -->|Payment Confirmation| HMS
    HMS -->|Chat Messages, User Data| CS
    CS -->|Real-time Messages| HMS
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
        P11[11.0<br/>Payment<br/>Configuration]
        P12[12.0<br/>Shipping<br/>Management]
        P13[13.0<br/>Supplier<br/>Management]
        P14[14.0<br/>Restock<br/>Management]
    end
    
    subgraph "Data Stores"
        D1[(Users Database)]
        D2[(Products Database)]
        D3[(Orders Database)]
        D4[(Chat Database)]
        D5[(Categories Database)]
        D6[(Payment Config)]
        D7[(Shipping Services)]
        D8[(Suppliers Database)]
        D9[(Restock Orders)]
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
    P11 --> D6
    P12 --> D7
    P13 --> D8
    P14 --> D9
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
    
    O --> P[Select payment method<br/>Stripe or Midtrans]
    P --> Q[Process payment via gateway]
    
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
    K --> L[Select courier service]
    L --> M[Input tracking number]
    M --> N[Update order status<br/>to 'Shipped']
    
    N --> O[Send tracking info<br/>to customer]
    O --> P{Order delivered?}
    P -->|No| Q[Track shipment]
    P -->|Yes| R[Update order status<br/>to 'Delivered']
    
    Q --> P
    R --> S[Generate analytics report]
    S --> T[End]
```

### Live Chat Support Flow
```mermaid
flowchart TD
    A[Customer opens chat widget] --> B[Connect to WebSocket]
    B --> C[Join user room]
    C --> D[Load chat history]
    D --> E[Display chat interface]
    
    E --> F[Customer types message]
    F --> G{Include product tag?}
    G -->|Yes| H[Search and select product]
    G -->|No| I[Send message]
    H --> I
    
    I --> J[Message saved to database]
    J --> K[Emit to admin room via WebSocket]
    K --> L[Admin receives notification]
    
    L --> M[Admin opens chat interface]
    M --> N[Admin types reply]
    N --> O{Tag product?}
    O -->|Yes| P[Select product from search]
    O -->|No| Q[Send reply]
    P --> Q
    
    Q --> R[Reply saved to database]
    R --> S[Emit to user room via WebSocket]
    
    S --> T{Customer chat open?}
    T -->|Yes| U[Display message instantly]
    T -->|No| V[Update unread badge]
    
    U --> W[Conversation continues]
    V --> X[Customer opens chat]
    X --> U
    W --> Y{Chat session ends?}
    Y -->|No| F
    Y -->|Yes| Z[Close WebSocket connection]
    Z --> AA[End]
```

### Restock Management Flow
```mermaid
flowchart TD
    A[Low stock alert triggered] --> B[Admin reviews inventory]
    B --> C[Create restock order]
    C --> D[Select supplier]
    D --> E[Add products and quantities]
    E --> F[Set expected delivery date]
    F --> G[Calculate total cost]
    G --> H[Send PO to supplier]
    
    H --> I[Update order status to 'Ordered']
    I --> J[Track delivery]
    J --> K{Goods received?}
    K -->|No| L[Follow up with supplier]
    K -->|Yes| M[Update order status to 'Received']
    
    L --> J
    M --> N[Update product stock quantities]
    N --> O[Generate restock report]
    O --> P[End]
```

## 🛠️ Instalasi & Setup

### Environment Requirements
- Python 3.11+
- PostgreSQL 12+
- Node.js 20+ (untuk dependencies)

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

### 3. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Setup chat service
cd chat_service
pip install django djangorestframework channels channels-redis corsheaders daphne
cd ..
```

### 4. Database Setup
```bash
# Setup main database
python migrate_db.py

# Setup chat service database
cd chat_service
python manage.py migrate
cd ..

# Load sample data (optional)
python sample_data.py
```

### 5. Run Application
```bash
# Development mode - start both services
python main.py  # Main Flask app on port 5000
cd chat_service && python manage.py runserver 0.0.0.0:8000  # Chat service on port 8000

# Or use Replit workflow
# Click Run button to start both services
```

Aplikasi akan berjalan di:
- **Main App**: `http://0.0.0.0:5000`
- **Chat Service**: `http://0.0.0.0:8000`

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
2. **Products**: Kelola produk, kategori, dan inventory
3. **Orders**: Monitor dan update status orders
4. **Users**: User management dan role assignment
5. **Chat**: Respond ke customer inquiries real-time
6. **Analytics**: Generate reports dan export data
7. **Payment Config**: Setup payment gateways
8. **Shipping**: Configure courier services
9. **Suppliers**: Manage supplier database
10. **Restock**: Handle inventory replenishment

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
- **HTTPS Enforcement** di Replit deployment
- **SameSite Cookie** protection untuk CSRF prevention
- **HTTPOnly Cookies** untuk session security
- **Environment Variable** protection untuk sensitive data
- **CORS Configuration** untuk microservice communication

## [WEB] Deployment di Replit

### Architecture Overview
```
Replit Environment
├── Main Flask App (Port 5000 → 80/443)
├── Django Chat Service (Port 8000)
├── PostgreSQL Database
└── Static Files Serving
```

### Configuration
- **Port**: 5000 (auto-forwarded to 80/443)
- **Chat Service**: 8000 (internal communication)
- **Database**: PostgreSQL via environment variable
- **Static Files**: Served via Flask built-in server
- **WebSockets**: Django Channels dengan ASGI server
- **Security**: Production-ready security headers

### Replit Workflow
```toml
[[workflows.workflow]]
name = "Project"
mode = "parallel"

[[workflows.workflow.tasks]]
task = "workflow.run"
args = "Flask Server"

[[workflows.workflow.tasks]]
task = "workflow.run"
args = "Django Chat Service"
```

### Environment Setup
```bash
# Production environment variables di Replit Secrets
SESSION_SECRET=production_secret_key
DATABASE_URL=postgresql://username:password@host:port/database
STRIPE_SECRET_KEY=sk_live_your_live_stripe_key
MIDTRANS_SERVER_KEY=live_server_key
MIDTRANS_CLIENT_KEY=live_client_key
REPLIT_DEPLOYMENT=production
```

## 📊 API Documentation

### Main App Endpoints

**Authentication**:
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

**Products**:
- `GET /products` - List products with filtering
- `GET /product/<id>` - Product details
- `GET /search` - Search products
- `GET /api/products/<id>` - Product API (JSON)

**Cart & Orders**:
- `POST /add_to_cart/<id>` - Add to cart
- `GET /cart` - View cart
- `POST /checkout` - Checkout process
- `GET /orders` - User orders

**Admin**:
- `GET /admin` - Admin dashboard
- `GET /admin/products` - Product management
- `GET /admin/orders` - Order management
- `GET /admin/users` - User management
- `GET /admin/chat` - Chat interface

### Chat Service Endpoints

**Chat Management**:
- `GET /api/admin/buyer-rooms/` - List chat rooms
- `GET /api/rooms/<name>/messages/` - Room messages
- `POST /api/rooms/<name>/mark-read/` - Mark messages read

**WebSocket**:
- `ws://localhost:8000/ws/chat/<room_name>/` - Chat WebSocket

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
├── chat_service/        # Django chat microservice
│   ├── manage.py
│   ├── chat/           # Chat app
│   └── chat_microservice/  # Settings
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
- **Scalability Ready**: Microservice architecture untuk chat, database optimization
- **Real-time Experience**: WebSocket untuk instant communication
- **Modern Standards**: ES6+, HTML5, CSS3, Progressive Enhancement
- **Developer Experience**: Clean code, modular structure, comprehensive docs

### Microservice Architecture Benefits
- **Separation of Concerns**: Chat service isolated dari main business logic
- **Scalability**: Chat service dapat di-scale independent
- **Technology Diversity**: Django untuk real-time, Flask untuk e-commerce
- **Fault Tolerance**: Chat service failure tidak affect main application
- **Development Velocity**: Teams dapat develop secara parallel

---

**Hurtrock Music Store** - *Rock Your Music Journey with Modern Technology* [MUSIC]🎸[START]
