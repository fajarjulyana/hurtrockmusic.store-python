
# 🎵 Hurtrock Music Store

Aplikasi e-commerce modern untuk toko alat musik dengan tema Rock/Metal menggunakan font Metal Mania dan Rock Salt, sistem manajemen produk, shopping cart, dan pembayaran terintegrasi Stripe.

## 🚀 Teknologi yang Digunakan

### Backend Framework
- **Flask 3.1.2** - Web framework Python yang ringan dan fleksibel
- **SQLAlchemy 2.0.43** - ORM untuk manajemen database
- **Flask-Login 0.6.3** - Sistem autentikasi dan session management
- **Flask-Migrate 4.1.0** - Database migration tool
- **Flask-WTF 1.2.2** - Form handling dan CSRF protection

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
- **Segoe UI** - Font default untuk admin dashboard (tidak berubah)

### Design Elements
- Glass morphism effects pada navbar
- Orange-Black color scheme dengan tema Rock/Metal
- Responsive mobile-first design
- Light/Dark mode toggle
- Smooth animations dan hover effects

## ✨ Fitur yang Tersedia

### 🛍️ Sisi Pengguna (Customer)
1. **Autentikasi & Profil**
   - ✅ Registrasi akun baru
   - ✅ Login/logout sistem
   - ✅ Manajemen profil pengguna

2. **Katalog Produk**
   - ✅ Browse produk berdasarkan kategori
   - ✅ Search real-time dengan autocomplete
   - ✅ Detail produk dengan galeri gambar
   - ✅ Filter dan sorting produk

3. **Shopping Cart**
   - ✅ Add to cart functionality
   - ✅ Update quantity items
   - ✅ Remove items dari cart
   - ✅ Subtotal calculation otomatis

4. **Payment & Checkout**
   - ✅ Integrasi dengan Stripe payment
   - ✅ Checkout process yang aman
   - ✅ Order confirmation
   - ✅ Payment success page

5. **Theme & UX**
   - ✅ Light/Dark mode toggle
   - ✅ Responsive mobile design
   - ✅ Glass morphism UI effects
   - ✅ Rock/Metal themed fonts dan colors

### 👨‍💼 Sisi Admin
1. **Dashboard Analytics**
   - ✅ Total products, orders, users
   - ✅ Recent orders overview
   - ✅ Quick action buttons

2. **Product Management**
   - ✅ CRUD operations untuk produk
   - ✅ Multi-image upload dengan kompresi otomatis
   - ✅ Kategori management
   - ✅ Stock quantity tracking
   - ✅ Featured products marking

3. **Order Processing**
   - ✅ View all orders
   - ✅ Order status management
   - ✅ Customer information access

## 🚧 Fitur dalam Pengembangan / Bug Fixes Needed

### Known Issues
1. **Image Management**
   - ❌ Hero image tidak ditemukan (404 error pada /static/images/hero-music.jpg)
   - ❌ Perlu implementasi upload gambar untuk hero section

2. **Chat System**
   - ❌ Live chat belum diimplementasi (template ada tapi backend belum)
   - ❌ Socket.IO integration belum aktif

3. **Email System**
   - ❌ Email notification untuk order belum diimplementasi
   - ❌ Password reset via email belum tersedia

### Planned Features
- 📋 Live chat support dengan Socket.IO
- 📧 Email notifications untuk orders
- 📊 Advanced analytics dashboard
- 🔄 Order tracking system
- 📱 PWA (Progressive Web App) support

## 📊 System Architecture

### Entity Relationship Diagram (ERD)
```mermaid
erDiagram
    User ||--o{ CartItem : has
    User ||--o{ Order : places
    Product ||--o{ CartItem : contains
    Product ||--o{ OrderItem : includes
    Category ||--o{ Product : categorizes
    Order ||--o{ OrderItem : contains

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
```

### Data Flow Diagram (DFD) Level 1
```mermaid
graph TD
    A[Customer] --> B[Authentication System]
    A --> C[Product Catalog]
    A --> D[Shopping Cart]
    A --> E[Payment System]
    
    G[Admin] --> H[Product Management]
    G --> I[Order Management]
    G --> J[Analytics Dashboard]
    
    B --> L[(User Database)]
    C --> M[(Product Database)]
    D --> N[(Cart Database)]
    E --> O[Stripe API]
    E --> P[(Order Database)]
    H --> M
    I --> P
    J --> R[(Analytics Data)]
    
    style A fill:#e1f5fe
    style G fill:#fff3e0
    style O fill:#f3e5f5
```

### User Flow - Customer Journey
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
    
    style A fill:#e8f5e8
    style I fill:#fff3e0
    style J fill:#e1f5fe
```

### Admin Workflow
```mermaid
graph LR
    A[Admin Login] --> B[Dashboard]
    B --> C[Product Management]
    B --> D[Order Management]
    B --> E[User Management]
    
    C --> F[Add Product]
    C --> G[Edit Product]
    C --> H[Manage Categories]
    
    D --> I[View Orders]
    I --> J[Update Order Status]
    
    E --> K[View Users]
    K --> L[Manage User Roles]
    
    style A fill:#fff3e0
    style B fill:#e1f5fe
    style J fill:#e8f5e8
```

### Technical Architecture
```mermaid
graph TB
    subgraph "Frontend Layer"
        A[HTML Templates - Rock/Metal Theme]
        B[Bootstrap CSS + Custom Styles]
        C[JavaScript + Font Loading]
    end
    
    subgraph "Application Layer"
        D[Flask Application]
        E[Flask-Login Auth]
        F[Flask-WTF Forms]
        G[Jinja2 Templates]
    end
    
    subgraph "Business Logic"
        H[User Management]
        I[Product Catalog]
        J[Cart Management]
        K[Order Processing]
    end
    
    subgraph "Data Layer"
        L[SQLAlchemy ORM]
        M[(PostgreSQL Database)]
    end
    
    subgraph "External Services"
        N[Stripe Payment API]
        O[Google Fonts API]
        P[Image Processing]
    end
    
    A --> D
    B --> D
    C --> D
    D --> H
    D --> I
    D --> J
    D --> K
    H --> L
    I --> L
    J --> L
    K --> L
    L --> M
    K --> N
    A --> O
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
   python migrate_db.py  # Setup database and create tables
   python sample_data.py # Load sample data (optional)
   ```

5. **Run Application**
   ```bash
   python main.py
   # atau dengan uv:
   uv run python main.py
   ```

   Aplikasi akan berjalan di `http://0.0.0.0:5000`

## 📱 Usage

### Default Admin Access
- **Email**: admin@hurtrock.com
- **Password**: admin123

### Customer Features
1. Registrasi akun baru di `/register`
2. Browse produk di `/products`
3. Add produk ke cart dan checkout
4. Tema Rock/Metal dengan font Metal Mania dan Rock Salt

### Admin Features
1. Login dengan akun admin
2. Access admin panel di `/admin`
3. Kelola produk, kategori, dan orders
4. Monitor analytics di dashboard

## 🔐 Security Features

- CSRF Protection pada semua forms
- Password hashing dengan Werkzeug
- Secure session cookies (HTTPS only)
- SQL injection protection via SQLAlchemy ORM
- Admin role-based access control
- Input validation dan sanitization

## 🌐 Deployment

Aplikasi ini di-deploy di **Replit** dengan konfigurasi:
- Port: 5000 (forwarded to 80/443 in production)
- PostgreSQL database via environment variable
- Static files served via Flask
- Production-ready security settings

### Replit Configuration
```toml
[workflows.workflow]
name = "Hurtrock Music Store"
author = "agent"

[[workflows.workflow.tasks]]
task = "shell.exec"
args = "uv run python main.py"
waitForPort = 5000
```

## 📞 Support & Contact

- **Store Location**: Jl Gegerkalong Girang Complex Darut Tauhid Kav 22, Kota Bandung
- **Phone**: 0821-1555-8035
- **Hours**: Senin–Jumat 09.30–18.00, Sabtu 09.30–17.00
- **Theme**: Rock/Metal dengan nuansa modern vintage

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

**MIT License**

Copyright © 2025 **Fajar Julyana**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**Made with ❤️ by Fajar Julyana**

## 🎸 Design Philosophy

Aplikasi ini menggunakan tema Rock/Metal untuk mencerminkan semangat musik yang energik:

- **Metal Mania Font**: Untuk headings dan brand identity yang bold
- **Rock Salt Font**: Untuk body text yang memberikan karakter Rock
- **Orange-Black Scheme**: Kombinasi warna yang dinamis dan energik
- **Glass Morphism**: Efek modern yang tetap mempertahankan karakter Rock

---

**Hurtrock Music Store** - *Rock Your Music Journey* 🎵🎸

