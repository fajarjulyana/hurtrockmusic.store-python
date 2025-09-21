
# 🎵 Hurtrock Music Store

Aplikasi e-commerce modern untuk toko alat musik dengan sistem chat live, manajemen produk, dan pembayaran terintegrasi.

## 🚀 Teknologi yang Digunakan

### Backend Framework
- **Flask 3.1.2** - Web framework Python yang ringan dan fleksibel
- **SQLAlchemy 2.0.43** - ORM untuk manajemen database
- **Flask-Login 0.6.3** - Sistem autentikasi dan session management
- **Flask-Migrate 4.1.0** - Database migration tool
- **Flask-WTF 1.2.2** - Form handling dan CSRF protection
- **Flask-SocketIO 5.5.1** - Real-time communication untuk chat system

### Database & Storage
- **PostgreSQL** - Database utama untuk data produk, user, dan transaksi
- **Psycopg2-Binary 2.9.10** - PostgreSQL adapter untuk Python

### Payment Processing
- **Stripe 12.5.1** - Gateway pembayaran internasional yang aman

### Image Processing
- **Pillow 11.3.0** - Library untuk kompresi dan manipulasi gambar

### Frontend
- **Bootstrap 5.3.0** - CSS framework untuk responsive design
- **Font Awesome 6.0.0** - Icon library
- **Socket.IO Client** - Real-time communication di frontend

### Security & Utilities
- **Werkzeug 3.1.3** - Password hashing dan security utilities
- **Email-Validator 2.3.0** - Validasi format email
- **Python-Dotenv 1.1.1** - Environment variable management

## ✨ Fitur Utama

### 🛍️ Sisi Pengguna (Customer)
1. **Autentikasi & Profil**
   - Registrasi akun baru
   - Login/logout sistem
   - Manajemen profil pengguna

2. **Katalog Produk**
   - Browse produk berdasarkan kategori
   - Search real-time dengan autocomplete
   - Detail produk dengan galeri gambar
   - Filter dan sorting produk

3. **Shopping Cart**
   - Add to cart functionality
   - Update quantity items
   - Remove items dari cart
   - Subtotal calculation otomatis

4. **Payment & Checkout**
   - Integrasi dengan Stripe payment
   - Checkout process yang aman
   - Order confirmation
   - Payment success page

5. **Live Chat Support**
   - Floating chat widget
   - Real-time messaging dengan admin
   - Chat history tersimpan
   - Notifikasi pesan baru

6. **Theme & UX**
   - Light/Dark mode toggle
   - Responsive mobile design
   - Glass morphism UI effects
   - Smooth animations

### 👨‍💼 Sisi Admin
1. **Dashboard Analytics**
   - Total products, orders, users
   - Pending chats counter
   - Recent orders overview
   - Quick action buttons

2. **Product Management**
   - CRUD operations untuk produk
   - Multi-image upload dengan kompresi otomatis
   - Kategori management
   - Stock quantity tracking
   - Featured products marking

3. **Chat Management**
   - List semua chat rooms
   - Chat detail dengan history
   - Quick reply templates
   - Real-time message notifications
   - Unread message indicators

4. **Order Processing**
   - View all orders
   - Order status management
   - Customer information access

### 🔧 Sisi Developer
1. **Database Management**
   - SQLAlchemy models dengan relationships
   - Database migrations dengan Flask-Migrate
   - Connection pooling dan optimization

2. **Security Implementation**
   - CSRF protection
   - Secure session cookies
   - Password hashing
   - Admin role-based access

3. **Real-time Features**
   - Socket.IO implementation
   - Room-based messaging
   - Event-driven architecture

## 📊 System Architecture

### Entity Relationship Diagram (ERD)
```mermaid
erDiagram
    User ||--o{ CartItem : has
    User ||--o{ Order : places
    User ||--o{ ChatRoom : creates
    Product ||--o{ CartItem : contains
    Product ||--o{ OrderItem : includes
    Category ||--o{ Product : categorizes
    Order ||--o{ OrderItem : contains
    ChatRoom ||--o{ ChatMessage : has

    User {
        int id PK
        string email UK
        string password_hash
        string name
        string phone
        text address
        boolean active
        boolean is_admin
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
        text shipping_address
        string payment_method
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
        boolean is_read
        datetime created_at
    }
```

### Data Flow Diagram (DFD) Level 1
```mermaid
graph TD
    A[Customer] --> B[Authentication System]
    A --> C[Product Catalog]
    A --> D[Shopping Cart]
    A --> E[Payment System]
    A --> F[Chat System]
    
    G[Admin] --> H[Product Management]
    G --> I[Order Management]
    G --> J[Chat Management]
    G --> K[Analytics Dashboard]
    
    B --> L[(User Database)]
    C --> M[(Product Database)]
    D --> N[(Cart Database)]
    E --> O[Stripe API]
    E --> P[(Order Database)]
    F --> Q[(Chat Database)]
    H --> M
    I --> P
    J --> Q
    K --> R[(Analytics Data)]
    
    style A fill:#e1f5fe
    style G fill:#fff3e0
    style O fill:#f3e5f5
```

### System Flow - User Journey
```mermaid
graph LR
    A[Landing Page] --> B{User Login?}
    B -->|No| C[Register/Login]
    B -->|Yes| D[Browse Products]
    C --> D
    D --> E[Product Detail]
    E --> F[Add to Cart]
    F --> G[Shopping Cart]
    G --> H[Checkout]
    H --> I[Payment with Stripe]
    I --> J[Order Confirmation]
    
    D --> K[Live Chat]
    K --> L[Chat with Admin]
    
    style A fill:#e8f5e8
    style I fill:#fff3e0
    style J fill:#e1f5fe
```

### Admin Workflow
```mermaid
graph LR
    A[Admin Login] --> B[Dashboard]
    B --> C[Product Management]
    B --> D[Chat Management]
    B --> E[Order Management]
    
    C --> F[Add Product]
    C --> G[Edit Product]
    C --> H[Manage Categories]
    
    D --> I[View Chat Rooms]
    I --> J[Reply to Customers]
    
    E --> K[View Orders]
    K --> L[Update Order Status]
    
    style A fill:#fff3e0
    style B fill:#e1f5fe
    style J fill:#e8f5e8
```

### Technical Architecture
```mermaid
graph TB
    subgraph "Frontend Layer"
        A[HTML Templates]
        B[Bootstrap CSS]
        C[JavaScript/Socket.IO]
    end
    
    subgraph "Application Layer"
        D[Flask Application]
        E[Flask-Login Auth]
        F[Flask-SocketIO]
        G[Flask-WTF Forms]
    end
    
    subgraph "Business Logic"
        H[User Management]
        I[Product Catalog]
        J[Cart Management]
        K[Order Processing]
        L[Chat System]
    end
    
    subgraph "Data Layer"
        M[SQLAlchemy ORM]
        N[(PostgreSQL Database)]
    end
    
    subgraph "External Services"
        O[Stripe Payment API]
        P[Image Processing]
    end
    
    A --> D
    B --> D
    C --> F
    D --> H
    D --> I
    D --> J
    D --> K
    D --> L
    H --> M
    I --> M
    J --> M
    K --> M
    L --> M
    M --> N
    K --> O
    I --> P
```

## 🛠️ Instalasi & Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-repo/hurtrock-music-store.git
   cd hurtrock-music-store
   ```

2. **Setup Environment Variables**
   ```bash
   # Required environment variables
   SESSION_SECRET=your_secret_key
   DATABASE_URL=postgresql://user:password@host:port/dbname
   STRIPE_SECRET_KEY=sk_test_your_stripe_key
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Run Application**
   ```bash
   python main.py
   ```

## 📱 Usage

### Default Admin Access
- **Email**: admin@hurtrock.com
- **Password**: admin123

### Customer Features
1. Registrasi akun baru di `/register`
2. Browse produk di `/products`
3. Add produk ke cart dan checkout
4. Gunakan live chat untuk bertanya tentang produk

### Admin Features
1. Login dengan akun admin
2. Access admin panel di `/admin`
3. Kelola produk, kategori, dan chat customer
4. Monitor analytics di dashboard

## 🔐 Security Features

- CSRF Protection pada semua forms
- Password hashing dengan Werkzeug
- Secure session cookies (HTTPS only)
- SQL injection protection via SQLAlchemy ORM
- Admin role-based access control

## 🌐 Deployment

Aplikasi ini di-deploy di **Replit** dengan konfigurasi:
- Port: 5000 (forwarded to 80/443 in production)
- PostgreSQL database via environment variable
- Static files served via Flask
- Real-time chat via Socket.IO

## 📞 Support & Contact

- **Store Location**: Jl Gegerkalong Girang Complex Darut Tauhid Kav 22, Kota Bandung
- **Phone**: 0821-1555-8035
- **Hours**: Senin–Jumat 09.30–18.00, Sabtu 09.30–17.00
- **Live Chat**: Available in-app for logged-in users

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Hurtrock Music Store** - *Your trusted partner in music* 🎵
