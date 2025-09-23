
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

## Diagram ERD, DFD, dan Flowchart

### Entity Relationship Diagram (ERD)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     User        │    │    Category     │    │    Supplier    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ email (UNIQUE)  │    │ name            │    │ name            │
│ password_hash   │    │ description     │    │ contact_person  │
│ name            │    │ image_url       │    │ email           │
│ phone           │    │ is_active       │    │ phone           │
│ address         │    │ created_at      │    │ company         │
│ role            │    └─────────────────┘    │ is_active       │
│ active          │                           │ created_at      │
│ created_at      │                           └─────────────────┘
└─────────────────┘                                   │
         │                                            │
         │                                            │
┌─────────────────┐    ┌─────────────────┐            │
│    CartItem     │    │     Product     │◄───────────┘
├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │
│ user_id (FK)    │◄──►│ name            │
│ product_id (FK) │◄──►│ description     │
│ quantity        │    │ price           │
│ created_at      │    │ stock_quantity  │
└─────────────────┘    │ image_url       │
                       │ brand           │
         │             │ model           │
         │             │ category_id (FK)│◄─────────────┐
         │             │ supplier_id (FK)│              │
         │             │ weight          │              │
         │             │ length/width/height           │
         │             │ minimum_stock   │              │
┌─────────────────┐    │ low_stock_threshold           │
│     Order       │    │ is_active       │              │
├─────────────────┤    │ is_featured     │              │
│ id (PK)         │    │ created_at      │              │
│ user_id (FK)    │◄─┐ └─────────────────┘              │
│ order_number    │  │          │                       │
│ total_amount    │  │          │                       │
│ status          │  │          │                       │
│ shipping_address│  │          │                       │
│ payment_method  │  │          │                       │
│ payment_status  │  │          │                       │
│ created_at      │  │          │                       │
└─────────────────┘  │          │                       │
         │           │          │                       │
         │           │          │                       │
┌─────────────────┐  │          │                       │
│   OrderItem     │  │          │                       │
├─────────────────┤  │          │                       │
│ id (PK)         │  │          │                       │
│ order_id (FK)   │◄─┘          │                       │
│ product_id (FK) │◄────────────┘                       │
│ quantity        │                                      │
│ price           │                                      │
│ created_at      │                                      │
└─────────────────┘                                      │
                                                         │
┌─────────────────┐    ┌─────────────────┐              │
│  ProductImage   │    │  StoreProfile   │              │
├─────────────────┤    ├─────────────────┤              │
│ id (PK)         │    │ id (PK)         │              │
│ product_id (FK) │◄───┼─┤ store_name      │              │
│ image_url       │    │ store_tagline   │              │
│ is_thumbnail    │    │ store_address   │              │
│ display_order   │    │ store_phone     │              │
│ created_at      │    │ store_email     │              │
└─────────────────┘    │ whatsapp_number │              │
                       │ operating_hours │              │
┌─────────────────┐    │ branch_name     │              │
│ ShippingService │    │ is_active       │              │
├─────────────────┤    │ created_at      │              │
│ id (PK)         │    └─────────────────┘              │
│ name            │                                      │
│ code            │                                      │
│ base_price      │                                      │
│ price_per_kg    │                                      │
│ min_days        │                                      │
│ max_days        │                                      │
│ is_active       │                                      │
└─────────────────┘                                      │
                                                         │
┌─────────────────┐                                      │
│PaymentConfig    │                                      │
├─────────────────┤                                      │
│ id (PK)         │                                      │
│ gateway_name    │                                      │
│ public_key      │                                      │
│ secret_key      │                                      │
│ is_active       │                                      │
│ environment     │                                      │
│ created_at      │                                      │
└─────────────────┘                                      │
```

### Data Flow Diagram (DFD) Level 0

```
                    ┌─────────────────┐
                    │    Customer     │
                    │   (Browser)     │
                    └─────────┬───────┘
                              │ HTTP/WebSocket
                              │
                    ┌─────────▼───────┐
                    │   Hurtrock      │
                    │ Music Store     │
                    │    System       │
                    └─────────┬───────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼───────┐   ┌─────────▼─────────┐   ┌───────▼───────┐
│   Payment     │   │    Database       │   │    Admin      │
│  Gateways     │   │   PostgreSQL      │   │   Users       │
│(Stripe/Midtrans)│ │    + SQLite       │   │  (Backend)    │
└───────────────┘   └───────────────────┘   └───────────────┘
```

### Data Flow Diagram (DFD) Level 1

```
┌─────────────┐     ┌─────────────────────────────────────────┐     ┌─────────────┐
│  Customer   │────►│            Hurtrock System              │◄────│    Admin    │
│   Browser   │     │                                         │     │   Panel     │
└─────────────┘     │  ┌─────────────┐  ┌─────────────────┐   │     └─────────────┘
                    │  │   Flask     │  │     Django      │   │
┌─────────────┐     │  │ Main App    │  │  Chat Service   │   │     ┌─────────────┐
│  Payment    │────►│  │ :5000       │  │    :8000        │   │◄────│ PostgreSQL  │
│ Gateways    │     │  └─────┬───────┘  └─────────┬───────┘   │     │  Database   │
└─────────────┘     │        │                    │           │     └─────────────┘
                    │        │                    │           │
┌─────────────┐     │  ┌─────▼───────┐  ┌─────────▼───────┐   │     ┌─────────────┐
│ File System │◄────│  │  Business   │  │  Real-time      │   │────►│   SQLite    │
│  (Images)   │     │  │   Logic     │  │   Chat          │   │     │ Chat DB     │
└─────────────┘     │  └─────────────┘  └─────────────────┘   │     └─────────────┘
                    └─────────────────────────────────────────┘
```

### Flowchart Customer Journey

```
    ┌─────────┐
    │  START  │
    └────┬────┘
         │
    ┌────▼────┐
    │ Kunjungi│
    │Website  │
    └────┬────┘
         │
    ┌────▼────┐    TIDAK  ┌─────────────┐
    │Sudah    │──────────►│Daftar/      │
    │Login?   │           │Login        │
    └────┬────┘           └──────┬──────┘
         │YA                     │
         └──────────────┬────────┘
                        │
                   ┌────▼────┐
                   │ Jelajahi│
                   │Produk   │
                   └────┬────┘
                        │
                   ┌────▼────┐    TIDAK  ┌─────────────┐
                   │Produk   │──────────►│Lanjut       │
                   │Dipilih? │           │Browsing     │
                   └────┬────┘           └──────┬──────┘
                        │YA                     │
                        │                       │
                   ┌────▼────┐                 │
                   │Tambah ke│                 │
                   │Keranjang│                 │
                   └────┬────┘                 │
                        │                       │
                   ┌────▼────┐    TIDAK       │
                   │Siap     │─────────────────┘
                   │Checkout?│
                   └────┬────┘
                        │YA
                        │
                   ┌────▼────┐
                   │Isi Info │
                   │Pengiriman│
                   └────┬────┘
                        │
                   ┌────▼────┐
                   │Pilih    │
                   │Metode   │
                   │Bayar    │
                   └────┬────┘
                        │
                   ┌────▼────┐    GAGAL  ┌─────────────┐
                   │Proses   │──────────►│Tampil Error │
                   │Pembayaran│          │Coba Lagi    │
                   └────┬────┘          └──────┬──────┘
                        │BERHASIL              │
                        │                      │
                   ┌────▼────┐                │
                   │Halaman  │                │
                   │Sukses   │                │
                   │Bayar    │                │
                   └────┬────┘                │
                        │                      │
                   ┌────▼────┐                │
                   │Tracking │                │
                   │Pesanan  │                │
                   └────┬────┘                │
                        │                      │
                   ┌────▼────┐                │
                   │ Chat    │←───────────────┘
                   │Support  │
                   │(Opsional)│
                   └────┬────┘
                        │
                   ┌────▼────┐
                   │   END   │
                   └─────────┘
```

### Flowchart Admin Product Management

```
    ┌─────────┐
    │  START  │
    └────┬────┘
         │
    ┌────▼────┐
    │Login    │
    │Admin    │
    └────┬────┘
         │
    ┌────▼────┐
    │Pilih    │
    │Aksi     │
    │Produk   │
    └────┬────┘
         │
    ┌────▼────┐
    │ Jenis   │
    │ Aksi?   │
    └─┬─┬─┬─┬─┘
      │ │ │ │
   ┌──▼─▼─▼─▼──┐
   │BUAT│EDIT│LIHAT│HAPUS│
   └──┬─┬─┬─┬──┘
      │ │ │ │
      │ │ │ └─────────┐
      │ │ │           │
      │ │ └─────────┐ │
      │ │           │ │
      │ └─────────┐ │ │
      │           │ │ │
   ┌──▼──┐     ┌──▼─▼─▼──┐
   │Tambah     │Pilih    │
   │Produk     │Produk   │
   │Baru       │Existing │
   └──┬──┘     └──┬──────┘
      │           │
   ┌──▼──┐     ┌──▼──┐
   │Isi  │     │Muat │
   │Form │     │Data │
   └──┬──┘     └──┬──┘
      │           │
   ┌──▼──┐       │     ┌──────┐
   │Upload       │     │Edit? ├─TIDAK─┐
   │Gambar       │     └──┬───┘       │
   └──┬──┘       │        │YA         │
      │           │        │           │
   ┌──▼──┐     ┌──▼──┐  ┌──▼──┐    ┌──▼──┐
   │Set  │     │Mode │  │Update│    │Konfirmasi│
   │Detail     │Lihat│  │Data │    │Hapus │
   └──┬──┘     └──┬──┘  └──┬──┘    └──┬──┘
      │           │        │           │
   ┌──▼──┐       │     ┌──▼──┐        │
   │Validasi     │     │Simpan       │
   │Data │       │     │Perubahan    │
   └──┬──┘       │     └──┬──┘        │
      │           │        │           │
   ┌──▼──┐    ERROR      │         ┌──▼──┐
   │Simpan├─────┐  │       │         │Hapus│
   │Produk     │  │       │         │Produk
   └──┬──┘     │  │       │         └──┬──┘
      │BERHASIL│  │       │            │
      │        │  │       │            │
   ┌──▼──┐  ┌──▼──▼───────▼────────────▼──┐
   │Tampil│  │     Tampil Pesan             │
   │Sukses│  │  (Sukses/Error/Konfirmasi)   │
   └──┬──┘  └──┬───────────────────────────┘
      │        │
   ┌──▼────────▼──┐
   │Kembali ke    │
   │Daftar Produk │
   └──┬───────────┘
      │
   ┌──▼──┐
   │ END │
   └─────┘
```

### Flowchart Order Processing

```
    ┌─────────┐
    │Pesanan  │
    │Baru     │
    │Diterima │
    └────┬────┘
         │
    ┌────▼────┐
    │Validasi │
    │Detail   │
    │Pesanan  │
    └────┬────┘
         │
    ┌────▼────┐    TIDAK VALID ┌─────────────┐
    │Pesanan  │──────────────►│Tolak Pesanan│
    │Valid?   │               │Kirim Email  │
    └────┬────┘               └─────────────┘
         │VALID
         │
    ┌────▼────┐
    │Cek Stok │
    │Barang   │
    └────┬────┘
         │
    ┌────▼────┐    TIDAK CUKUP ┌──────────────┐
    │Stok     │──────────────►│Kirim Sebagian?│
    │Tersedia?│               └──────┬───────┘
    └────┬────┘                      │
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
