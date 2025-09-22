import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import stripe
from datetime import datetime, timedelta
from database import db
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import random
import string
import midtransclient
import json

# Create the Flask app
app = Flask(__name__)

# Configuration
if not os.environ.get("SESSION_SECRET"):
    raise ValueError("SESSION_SECRET environment variable is required")
app.secret_key = os.environ.get("SESSION_SECRET")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Security configuration - Development vs Production
is_production = os.environ.get('REPLIT_ENVIRONMENT') == 'production'
app.config['SESSION_COOKIE_SECURE'] = is_production  # HTTPS only in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JS access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['REMEMBER_COOKIE_SECURE'] = is_production
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
# Configure Socket.IO with proper CORS for production
if is_production:
    # Get all possible domains from environment
    domains = os.environ.get('REPLIT_DOMAINS', '').split(',')
    allowed_origins = [f"https://{domain.strip()}" for domain in domains if domain.strip()]
    if not allowed_origins:
        # Use localhost as fallback for production if no domains set - more secure than "*"
        allowed_origins = ["https://localhost:5000", "http://localhost:5000"]
        print("Warning: REPLIT_DOMAINS not set in production, using localhost fallback")
else:
    allowed_origins = ["*"]  # Allow all origins in development

socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode='threading')

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(image_path, max_size_mb=1):
    """Compress image to be under max_size_mb"""
    img = Image.open(image_path)

    # Convert to RGB if necessary
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    # Start with quality 85
    quality = 85

    while True:
        img.save(image_path, 'JPEG', quality=quality, optimize=True)

        # Check file size
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)

        if file_size_mb <= max_size_mb or quality <= 20:
            break

        quality -= 10

    return image_path

# Login Manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'

# Stripe configuration
if not os.environ.get('STRIPE_SECRET_KEY'):
    print("Warning: STRIPE_SECRET_KEY not set, using placeholder for development")
# Stripe API key will be set dynamically per request from PaymentConfiguration
# stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_placeholder_for_development')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(models.User, int(user_id))

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Akses ditolak. Anda harus admin untuk mengakses halaman ini.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (not current_user.is_admin and not current_user.is_staff):
            flash('Akses ditolak. Anda harus staff atau admin untuk mengakses halaman ini.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Import models before routes
import models

# Create database tables and default admin user
with app.app_context():
    try:
        # Ensure all tables are created with current schema
        db.create_all()

        # Create default admin user if it doesn't exist
        admin_email = "admin@hurtrock.com"

        # Check if admin user exists safely
        try:
            admin_user = models.User.query.filter_by(email=admin_email).first()
        except Exception as e:
            print(f"Database schema mismatch detected. Please run migration.")
            print(f"Error: {e}")
            admin_user = None

        if not admin_user:
            try:
                admin_user = models.User(
                    email=admin_email,
                    password_hash=generate_password_hash("admin123"),
                    name="Administrator",
                    role="admin"
                )
                db.session.add(admin_user)
                db.session.commit()
                print(f"Default admin user created: {admin_email}")
            except Exception as e:
                print(f"Failed to create admin user: {e}")
        else:
            print(f"Admin user already exists: {admin_email}")

        # Create default store profile if it doesn't exist
        try:
            store_profile = models.StoreProfile.get_active_profile()
            if not store_profile:
                store_profile = models.StoreProfile(
                    store_name='Hurtrock Music Store',
                    store_tagline='Toko Alat Musik Terpercaya',
                    store_address='Jl. Musik Raya No. 123, RT/RW 001/002, Kelurahan Musik, Kecamatan Harmoni',
                    store_city='Jakarta Selatan',
                    store_postal_code='12345',
                    store_phone='0821-1555-8035',
                    store_email='info@hurtrock.com',
                    store_website='https://hurtrock.com',
                    whatsapp_number='6282115558035',
                    operating_hours='Senin - Sabtu: 09:00 - 21:00\nMinggu: 10:00 - 18:00',
                    branch_name='Cabang Pusat',
                    branch_code='HRT-001'
                )
                db.session.add(store_profile)
                db.session.commit()
                print("Default store profile created")
            else:
                print("Store profile already exists")
        except Exception as e:
            print(f"Failed to create store profile: {e}")

    except Exception as e:
        print(f"Database initialization error: {e}")

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Halaman yang Anda cari tidak ditemukan."), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Terjadi kesalahan server. Silakan coba lagi nanti."), 500

# Routes
@app.route('/')
def index():
    products = models.Product.query.filter_by(is_active=True).limit(8).all()
    categories = models.Category.query.filter_by(is_active=True).all()
    return render_template('index.html', products=products, categories=categories)

@app.route('/products')
def products():
    category_id = request.args.get('category')
    search_query = request.args.get('search', '')

    query = models.Product.query.filter_by(is_active=True)

    if category_id:
        query = query.filter_by(category_id=category_id)

    if search_query:
        query = query.filter(models.Product.name.contains(search_query))

    products = query.all()
    categories = models.Category.query.filter_by(is_active=True).all()

    return render_template('products.html', products=products, categories=categories, 
                         current_category=int(category_id) if category_id else None,
                         search_query=search_query)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = models.Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if query and len(query) >= 2:
        try:
            # Case-insensitive search across multiple fields (using ILIKE for PostgreSQL performance)
            search_term = f"%{query}%"
            products = models.Product.query.filter(
                db.or_(
                    models.Product.name.ilike(search_term),
                    models.Product.description.ilike(search_term),
                    models.Product.brand.ilike(search_term),
                    models.Product.model.ilike(search_term)
                ),
                models.Product.is_active == True
            ).limit(10).all()  # Limit results for performance

            return jsonify([{
                'id': p.id,
                'name': p.name,
                'price': str(p.price),
                'image_url': p.image_url or '/static/images/placeholder.jpg',
                'brand': p.brand or '',
                'description': p.description[:100] + '...' if p.description and len(p.description) > 100 else p.description or ''
            } for p in products])
        except Exception as e:
            print(f"Search error: {e}")
            return jsonify({'error': 'Search failed'}), 500
    return jsonify([])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        name = request.form['name']

        # Check if user already exists
        if models.User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar. Silakan login.', 'error')
            return redirect(url_for('register'))

        # Create new user
        hashed_password = generate_password_hash(password)
        user = models.User(email=email, password_hash=hashed_password, name=name)

        db.session.add(user)
        db.session.commit()

        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = models.User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Email atau password salah.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    cart_items = models.CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.quantity * item.product.price for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = models.Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))

    # Check if item already in cart
    cart_item = models.CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = models.CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()
    flash(f'{product.name} ditambahkan ke keranjang!', 'success')

    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = models.CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()

    quantity = int(request.form.get('quantity', 1))

    if quantity > 0:
        cart_item.quantity = quantity
    else:
        db.session.delete(cart_item)

    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart_item = models.CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(cart_item)
    db.session.commit()
    flash('Item dihapus dari keranjang.', 'info')

    return redirect(url_for('cart'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.phone = request.form['phone']
        current_user.address = request.form['address']

        db.session.commit()
        flash('Profile berhasil diperbarui!', 'success')

        # Redirect to checkout if came from there
        next_url = request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(url_for('profile'))

    return render_template('profile.html')

@app.route('/checkout')
@login_required
def checkout():
    # Check if buyer has complete profile (for buyers only)
    if current_user.is_buyer and (not current_user.address or not current_user.phone):
        flash('Silakan lengkapi profile Anda terlebih dahulu sebelum melakukan pembelian.', 'warning')
        return redirect(url_for('profile', next=url_for('checkout')))

    cart_items = models.CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash('Keranjang kosong!', 'error')
        return redirect(url_for('cart'))

    subtotal = sum(item.quantity * item.product.price for item in cart_items)

    # Calculate shipping weight and volume
    total_weight = sum(item.quantity * (item.product.weight or 0) for item in cart_items)
    total_volume = sum(item.quantity * (item.product.volume_cm3 or 0) for item in cart_items)

    # Get available shipping services
    shipping_services = models.ShippingService.query.filter_by(is_active=True).all()

    # Calculate shipping costs for each service
    shipping_options = []
    for service in shipping_services:
        cost = service.calculate_shipping_cost(total_weight, total_volume)
        shipping_options.append({
            'service': service,
            'cost': cost,
            'delivery_estimate': f"{service.min_days}-{service.max_days} hari"
        })

    # Get active payment configurations
    payment_configs = models.PaymentConfiguration.query.filter_by(is_active=True).all()

    # If no active payment config, show error
    if not payment_configs:
        flash('Tidak ada metode pembayaran yang tersedia. Silakan hubungi admin.', 'error')
        return redirect(url_for('cart'))

    return render_template('checkout.html', 
                         cart_items=cart_items, 
                         subtotal=subtotal,
                         total=subtotal,  # Add total variable (will be updated by JS when shipping is selected)
                         total_weight=total_weight,
                         total_volume=total_volume,
                         shipping_options=shipping_options,
                         payment_configs=payment_configs)

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    cart_items = models.CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        return jsonify({'error': 'Keranjang kosong'}), 400

    # Get selected payment configuration
    payment_config_id = request.form.get('payment_config_id')
    if not payment_config_id:
        flash('Silakan pilih metode pembayaran!', 'error')
        return redirect(url_for('checkout'))

    payment_config = models.PaymentConfiguration.query.get_or_404(int(payment_config_id))

    if not payment_config.is_active:
        flash('Metode pembayaran yang dipilih tidak aktif!', 'error')
        return redirect(url_for('checkout'))

    # Get selected shipping service
    shipping_service_id = request.form.get('shipping_service_id')
    if not shipping_service_id:
        flash('Silakan pilih jasa kirim!', 'error')
        return redirect(url_for('checkout'))

    shipping_service = models.ShippingService.query.get_or_404(int(shipping_service_id))

    # Calculate costs
    subtotal = sum(item.quantity * item.product.price for item in cart_items)
    total_weight = sum(item.quantity * (item.product.weight or 0) for item in cart_items)
    total_volume = sum(item.quantity * (item.product.volume_cm3 or 0) for item in cart_items)
    shipping_cost = shipping_service.calculate_shipping_cost(total_weight, total_volume)
    total_amount = float(subtotal) + float(shipping_cost)

    # Store order info in session
    session['shipping_service_id'] = shipping_service_id
    session['shipping_cost'] = float(shipping_cost)
    session['payment_config_id'] = payment_config_id

    try:
        YOUR_DOMAIN = os.environ.get('REPLIT_DOMAINS', 'localhost:5000')

        if payment_config.provider == 'stripe':
            return _create_stripe_checkout(cart_items, shipping_service, shipping_cost, total_amount, YOUR_DOMAIN, payment_config)
        elif payment_config.provider == 'midtrans':
            return _create_midtrans_checkout(cart_items, shipping_service, shipping_cost, total_amount, YOUR_DOMAIN, payment_config)
        else:
            flash('Metode pembayaran tidak didukung!', 'error')
            return redirect(url_for('checkout'))

    except Exception as e:
        flash(f'Error dalam memproses pembayaran: {str(e)}', 'error')
        return redirect(url_for('cart'))

def _create_stripe_checkout(cart_items, shipping_service, shipping_cost, total_amount, domain, payment_config):
    """Create Stripe checkout session"""

    # Set Stripe API key from config with fallback
    api_key = payment_config.stripe_secret_key or os.environ.get('STRIPE_SECRET_KEY')
    if not api_key:
        raise ValueError("No Stripe API key configured. Please configure payment settings in admin panel.")

    stripe.api_key = api_key

    # Build line items
    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'idr',
                'product_data': {
                    'name': item.product.name,
                },
                'unit_amount': int(item.product.price * 100),  # Convert to cents
            },
            'quantity': item.quantity,
        })

    # Add shipping as line item
    line_items.append({
        'price_data': {
            'currency': 'idr',
            'product_data': {
                'name': f'Ongkos Kirim - {shipping_service.name}',
            },
            'unit_amount': int(shipping_cost * 100),  # Convert to cents
        },
        'quantity': 1,
    })

    checkout_session = stripe.checkout.Session.create(
        line_items=line_items,
        mode='payment',
        success_url=f'https://{domain}/payment-success',
        cancel_url=f'https://{domain}/cart',
        customer_email=current_user.email,
    )

    return redirect(checkout_session.url, code=303)

def _create_midtrans_checkout(cart_items, shipping_service, shipping_cost, total_amount, domain, payment_config):
    """Create Midtrans checkout session"""
    import uuid

    # Create Snap API instance
    snap = midtransclient.Snap(
        is_production=not payment_config.is_sandbox,
        server_key=payment_config.midtrans_server_key,
        client_key=payment_config.midtrans_client_key
    )

    # Generate unique order ID
    order_id = f"ORDER-{current_user.id}-{int(datetime.utcnow().timestamp())}-{str(uuid.uuid4())[:8]}"

    # Build item details
    item_details = []
    for item in cart_items:
        item_details.append({
            'id': str(item.product.id),
            'price': int(item.product.price),
            'quantity': item.quantity,
            'name': item.product.name[:50]  # Midtrans has character limit
        })

    # Add shipping cost
    item_details.append({
        'id': 'shipping',
        'price': int(shipping_cost),
        'quantity': 1,
        'name': f'Ongkir {shipping_service.name}'
    })

    # Customer details
    customer_details = {
        'first_name': current_user.name.split()[0] if current_user.name else 'Customer',
        'last_name': ' '.join(current_user.name.split()[1:]) if current_user.name and len(current_user.name.split()) > 1 else '',
        'email': current_user.email,
        'phone': current_user.phone or '081234567890',
        'billing_address': {
            'address': current_user.address or 'Jakarta',
            'city': 'Jakarta',
            'postal_code': '12345',
            'country_code': 'IDN'
        },
        'shipping_address': {
            'address': current_user.address or 'Jakarta',
            'city': 'Jakarta',
            'postal_code': '12345',
            'country_code': 'IDN'
        }
    }

    # Transaction details
    transaction_details = {
        'order_id': order_id,
        'gross_amount': int(total_amount)
    }

    # Parameter for Snap API
    param = {
        'transaction_details': transaction_details,
        'item_details': item_details,
        'customer_details': customer_details,
        'callbacks': {
            'finish': payment_config.callback_finish_url or f'https://{domain}/payment/finish',
            'unfinish': payment_config.callback_unfinish_url or f'https://{domain}/payment/unfinish',
            'error': payment_config.callback_error_url or f'https://{domain}/payment/error'
        }
    }

    # Create transaction
    transaction = snap.create_transaction(param)

    # Store order ID in session for callback handling
    session['midtrans_order_id'] = order_id

    # Redirect to Snap payment page
    return redirect(transaction['redirect_url'], code=303)

@app.route('/payment-success')
@login_required
def payment_success():
    # Create order from cart items
    cart_items = models.CartItem.query.filter_by(user_id=current_user.id).all()

    if cart_items:
        subtotal = sum(item.quantity * item.product.price for item in cart_items)

        # Get shipping info from session
        shipping_service_id = session.get('shipping_service_id')
        shipping_cost = session.get('shipping_cost', 0)

        total_amount = float(subtotal) + float(shipping_cost)

        # Calculate estimated delivery days
        estimated_delivery_days = 0
        if shipping_service_id:
            shipping_service = models.ShippingService.query.get(int(shipping_service_id))
            if shipping_service:
                estimated_delivery_days = shipping_service.max_days

        order = models.Order(
            user_id=current_user.id,
            total_amount=total_amount,
            shipping_cost=shipping_cost,
            shipping_service_id=int(shipping_service_id) if shipping_service_id else None,
            estimated_delivery_days=estimated_delivery_days,
            shipping_address=current_user.address,
            status='paid',
            created_at=datetime.utcnow()
        )
        db.session.add(order)
        db.session.flush()  # To get the order ID

        # Add order items
        for cart_item in cart_items:
            order_item = models.OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)

        # Clear cart
        for cart_item in cart_items:
            db.session.delete(cart_item)

        db.session.commit()

        flash('Pembayaran berhasil! Terima kasih atas pesanan Anda.', 'success')

    return render_template('payment_success.html', current_datetime=datetime.utcnow())

@app.route('/orders')
@login_required
def orders():
    user_orders = models.Order.query.filter_by(user_id=current_user.id).order_by(models.Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

@app.route('/store-info')
def store_info():
    return render_template('store_info.html')

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')



# API endpoints for floating chat
@app.route('/api/chat/messages')
@login_required
@csrf.exempt
def api_chat_messages():
    try:
        chat_room = models.ChatRoom.query.filter_by(user_id=current_user.id).first()
        if not chat_room:
            return jsonify({'success': True, 'messages': []})

        messages = models.ChatMessage.query.filter_by(chat_room_id=chat_room.id).order_by(models.ChatMessage.created_at).all()

        message_list = []
        for message in messages:
            message_list.append({
                'id': message.id,
                'message': message.message,
                'sender_type': message.sender_type,
                'timestamp': message.created_at.strftime('%H:%M'),
                'product_id': message.product_id
            })

        # Mark unread messages as read
        models.ChatMessage.query.filter_by(
            chat_room_id=chat_room.id, 
            sender_type='admin', 
            is_read=False
        ).update({'is_read': True})
        db.session.commit()

        return jsonify({'success': True, 'messages': message_list})

    except Exception as e:
        print(f"Error in api_chat_messages: {str(e)}")
        return jsonify({'error': 'Failed to load messages'}), 500

@app.route('/api/chat/send', methods=['POST'])
@login_required
@csrf.exempt
def api_chat_send():
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            message_text = data.get('message')
            product_id = data.get('product_id')
        else:
            message_text = request.form.get('message')
            product_id = request.form.get('product_id')

        if not message_text or message_text.strip() == '':
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Get or create chat room
        chat_room = models.ChatRoom.query.filter_by(user_id=current_user.id).first()
        if not chat_room:
            chat_room = models.ChatRoom(user_id=current_user.id)
            db.session.add(chat_room)
            db.session.flush()

        # Create message
        message = models.ChatMessage(
            chat_room_id=chat_room.id,
            sender_type='user',
            message=message_text.strip(),
            product_id=int(product_id) if product_id and product_id != '' else None
        )
        db.session.add(message)

        # Update last message time
        chat_room.last_message_at = datetime.utcnow()
        db.session.commit()

        # Emit to admin with product info
        emit_data = {
            'room_id': chat_room.id,
            'user_name': current_user.name,
            'message': message_text.strip(),
            'sender_type': 'user',
            'timestamp': message.created_at.strftime('%H:%M'),
            'product_id': product_id
        }

        socketio.emit('new_message', emit_data, room='admin_room')

        return jsonify({'success': True, 'message_id': message.id})

    except Exception as e:
        print(f"Error in api_chat_send: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to send message'}), 500

@app.route('/api/chat/clear', methods=['POST'])
@login_required
@csrf.exempt
def api_chat_clear():
    try:
        chat_room = models.ChatRoom.query.filter_by(user_id=current_user.id).first()
        if chat_room:
            # Delete all messages in the chat room
            models.ChatMessage.query.filter_by(chat_room_id=chat_room.id).delete()
            db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        print(f"Error in api_chat_clear: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to clear chat'}), 500

@app.route('/api/chat/pending_count')
@login_required
@staff_required
@csrf.exempt
def api_chat_pending_count():
    try:
        pending_count = models.ChatRoom.query.join(models.ChatMessage).filter(
            models.ChatMessage.sender_type == 'user',
            models.ChatMessage.is_read == False
        ).distinct().count()

        return jsonify({'count': pending_count})

    except Exception as e:
        print(f"Error in api_chat_pending_count: {str(e)}")
        return jsonify({'error': 'Failed to get pending count'}), 500

# Admin Routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_products = models.Product.query.count()
    total_orders = models.Order.query.count()
    total_users = models.User.query.filter(models.User.role != 'admin').count()
    pending_chats = models.ChatRoom.query.join(models.ChatMessage).filter(
        models.ChatMessage.sender_type == 'user',
        models.ChatMessage.is_read == False
    ).distinct().count()

    recent_orders = models.Order.query.order_by(models.Order.created_at.desc()).limit(5).all()

    # Analisis penjualan
    from sqlalchemy import func, extract
    from decimal import Decimal

    # Total penjualan hari ini
    today = datetime.utcnow().date()
    today_sales = db.session.query(func.sum(models.Order.total_amount)).filter(
        func.date(models.Order.created_at) == today,
        models.Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or Decimal('0')

    # Total penjualan bulan ini
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    monthly_sales = db.session.query(func.sum(models.Order.total_amount)).filter(
        extract('month', models.Order.created_at) == current_month,
        extract('year', models.Order.created_at) == current_year,
        models.Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or Decimal('0')

    # Produk terlaris dengan explicit join
    best_selling_products = db.session.query(
        models.Product.name,
        func.sum(models.OrderItem.quantity).label('total_sold')
    ).select_from(models.Product)\
    .join(models.OrderItem, models.OrderItem.product_id == models.Product.id)\
    .join(models.Order, models.Order.id == models.OrderItem.order_id)\
    .filter(
        models.Order.status.in_(['paid', 'shipped', 'delivered'])
    ).group_by(models.Product.id, models.Product.name).order_by(
        func.sum(models.OrderItem.quantity).desc()
    ).limit(5).all()

    return render_template('admin/dashboard.html', 
                         total_products=total_products,
                         total_orders=total_orders,
                         total_users=total_users,
                         pending_chats=pending_chats,
                         recent_orders=recent_orders,
                         current_date=datetime.utcnow(),
                         today_sales=today_sales,
                         monthly_sales=monthly_sales,
                         best_selling_products=best_selling_products)

@app.route('/admin/products')
@login_required
@admin_required
def admin_products():
    products = models.Product.query.all()
    categories = models.Category.query.all()
    suppliers = models.Supplier.query.filter_by(is_active=True).all()

    # Get low stock products (stock <= 5)
    low_stock_products = models.Product.query.filter(
        models.Product.stock_quantity <= 5,
        models.Product.is_active == True
    ).order_by(models.Product.stock_quantity.asc()).all()

    return render_template('admin/products.html', 
                         products=products, 
                         categories=categories,
                         suppliers=suppliers,
                         low_stock_products=low_stock_products)

@app.route('/admin/products/<int:product_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_product(product_id):
    product = models.Product.query.get_or_404(product_id)

    try:
        product.name = request.form['name']
        product.description = request.form.get('description', '')
        product.price = float(request.form['price'])
        product.stock_quantity = int(request.form['stock_quantity'])
        product.brand = request.form.get('brand', '')
        product.model = request.form.get('model', '')
        product.category_id = int(request.form['category_id'])
        product.supplier_id = int(request.form['supplier_id']) if request.form.get('supplier_id') else None
        product.is_featured = 'is_featured' in request.form
        product.is_active = 'is_active' in request.form

        # Handle dimensions and weight
        product.weight = float(request.form.get('weight', 0)) if request.form.get('weight') else 0
        product.length = float(request.form.get('length', 0)) if request.form.get('length') else 0
        product.width = float(request.form.get('width', 0)) if request.form.get('width') else 0
        product.height = float(request.form.get('height', 0)) if request.form.get('height') else 0

        # Handle image upload if new image is provided
        if 'image' in request.files and request.files['image'].filename:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                file.save(filepath)
                compress_image(filepath)
                product.image_url = f"/static/images/{filename}"

        db.session.commit()
        flash(f'Produk {product.name} berhasil diperbarui!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('admin_products'))

@app.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_product(product_id):
    product = models.Product.query.get_or_404(product_id)

    # Check if product has been ordered
    if product.order_items:
        flash('Tidak bisa menghapus produk yang sudah pernah dipesan!', 'error')
        return redirect(url_for('admin_products'))

    # Check if product is in cart
    if product.cart_items:
        # Remove from all carts
        for cart_item in product.cart_items:
            db.session.delete(cart_item)

    product_name = product.name
    db.session.delete(product)
    db.session.commit()

    flash(f'Produk {product_name} berhasil dihapus!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/product/<int:product_id>/edit', methods=['GET'])
@login_required
@admin_required
def admin_get_product(product_id):
    """Get product data for editing"""
    product = models.Product.query.get_or_404(product_id)

    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description or '',
        'price': float(product.price),
        'stock_quantity': product.stock_quantity,
        'brand': product.brand or '',
        'model': product.model or '',
        'category_id': product.category_id,
        'supplier_id': product.supplier_id,
        'is_active': product.is_active,
        'is_featured': product.is_featured,
        'image_url': product.image_url or '',
        'weight': float(product.weight or 0),
        'length': float(product.length or 0),
        'width': float(product.width or 0),
        'height': float(product.height or 0)
    })

@app.route('/admin/categories/<int:category_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_category(category_id):
    category = models.Category.query.get_or_404(category_id)

    try:
        category.name = request.form['name']
        category.description = request.form.get('description', '')
        category.is_active = 'is_active' in request.form

        db.session.commit()
        flash(f'Kategori {category.name} berhasil diperbarui!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_category(category_id):
    category = models.Category.query.get_or_404(category_id)

    # Check if category has products
    if category.products:
        flash('Tidak bisa menghapus kategori yang memiliki produk!', 'error')
        return redirect(url_for('admin_categories'))

    category_name = category.name
    db.session.delete(category)
    db.session.commit()

    flash(f'Kategori {category_name} berhasil dihapus!', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories')
@login_required
@admin_required
def admin_categories():
    categories = models.Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['POST'])
@login_required
@admin_required
def admin_add_category():
    name = request.form['name']
    description = request.form['description']

    category = models.Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()

    flash('Kategori berhasil ditambahkan!', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/chats')
@login_required
@staff_required
def admin_chats():
    chat_rooms = models.ChatRoom.query.filter_by(is_active=True).order_by(models.ChatRoom.last_message_at.desc()).all()

    # Calculate today start for filtering today's active chats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today = datetime.utcnow()

    return render_template('admin/chats.html', 
                          chat_rooms=chat_rooms, 
                          today_start=today_start, 
                          today=today)

@app.route('/admin/chat/<int:room_id>')
@login_required
@staff_required
def admin_chat_detail(room_id):
    chat_room = models.ChatRoom.query.get_or_404(room_id)
    messages = models.ChatMessage.query.filter_by(chat_room_id=room_id).order_by(models.ChatMessage.created_at).all()

    # Mark admin messages as read
    models.ChatMessage.query.filter_by(chat_room_id=room_id, sender_type='user', is_read=False).update({'is_read': True})
    db.session.commit()

    return render_template('admin/chat_detail.html', chat_room=chat_room, messages=messages)

@app.route('/admin/send_reply', methods=['POST'])
@login_required
@admin_required
def admin_send_reply():
    print("=" * 60)
    print("🚀 ADMIN SEND REPLY - REQUEST STARTED")
    print("=" * 60)
    
    try:
        # Log current user info
        print(f"👤 Current User: {current_user.name} (ID: {current_user.id}, Role: {current_user.role})")
        print(f"🔐 Is Admin: {current_user.is_admin}")
        print(f"🔐 Is Staff: {current_user.is_staff}")
        
        # Log request details
        print(f"📨 Request Method: {request.method}")
        print(f"📨 Content-Type: {request.headers.get('Content-Type', 'Not set')}")
        print(f"📨 User-Agent: {request.headers.get('User-Agent', 'Not set')}")
        print(f"📨 Remote Address: {request.remote_addr}")
        print(f"📨 Request Path: {request.path}")
        
        # Log all headers (for debugging)
        print("📋 All Headers:")
        for key, value in request.headers.items():
            print(f"   {key}: {value}")
        
        # Get data from request
        room_id = None
        message_text = None
        
        print(f"🔍 Is JSON Request: {request.is_json}")
        print(f"🔍 Has Form Data: {bool(request.form)}")
        print(f"🔍 Content Length: {request.content_length}")
        
        if request.is_json:
            print("📦 Processing JSON data...")
            try:
                data = request.get_json()
                print(f"📦 JSON Data: {data}")
                room_id = data.get('room_id') if data else None
                message_text = data.get('message') if data else None
            except Exception as json_error:
                print(f"❌ JSON Parse Error: {json_error}")
                return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400
        else:
            print("📦 Processing Form data...")
            try:
                print(f"📦 Form Data: {dict(request.form)}")
                room_id = request.form.get('room_id')
                message_text = request.form.get('message')
            except Exception as form_error:
                print(f"❌ Form Parse Error: {form_error}")
                return jsonify({'success': False, 'error': 'Invalid form data'}), 400

        print(f"📝 Extracted Data:")
        print(f"   Room ID: '{room_id}' (type: {type(room_id)})")
        print(f"   Message: '{message_text}' (type: {type(message_text)}, length: {len(message_text) if message_text else 0})")

        # Validate input with detailed logging
        if not room_id:
            print("❌ Validation Failed: Room ID is empty or None")
            return jsonify({'success': False, 'error': 'Room ID is required'}), 400

        if not message_text or not message_text.strip():
            print("❌ Validation Failed: Message is empty or None")
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        message_text = message_text.strip()
        print(f"✅ Validation Passed - Cleaned message: '{message_text}'")

        # Convert room_id to int and validate
        try:
            room_id_int = int(room_id)
            print(f"✅ Room ID converted to integer: {room_id_int}")
        except (ValueError, TypeError) as conv_error:
            print(f"❌ Room ID Conversion Error: {conv_error}")
            return jsonify({'success': False, 'error': 'Invalid room ID format'}), 400

        # Get chat room with detailed logging
        print(f"🔍 Looking for chat room with ID: {room_id_int}")
        try:
            chat_room = models.ChatRoom.query.get(room_id_int)
            if chat_room:
                print(f"✅ Chat room found:")
                print(f"   Room ID: {chat_room.id}")
                print(f"   User ID: {chat_room.user_id}")
                print(f"   User Name: {chat_room.user.name}")
                print(f"   User Email: {chat_room.user.email}")
                print(f"   Is Active: {chat_room.is_active}")
                print(f"   Created: {chat_room.created_at}")
                print(f"   Last Message: {chat_room.last_message_at}")
            else:
                print(f"❌ Chat room not found with ID: {room_id_int}")
                return jsonify({'success': False, 'error': 'Chat room not found'}), 404
        except Exception as db_error:
            print(f"❌ Database Error while getting chat room: {db_error}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': 'Database error'}), 500

        # Create admin message with detailed logging
        print(f"💾 Creating admin message...")
        try:
            admin_message = models.ChatMessage(
                chat_room_id=room_id_int,
                sender_type='admin',
                message=message_text
            )
            print(f"✅ Admin message object created")
            
            db.session.add(admin_message)
            print(f"✅ Admin message added to session")
            
            # Update chat room last message time
            chat_room.last_message_at = datetime.utcnow()
            print(f"✅ Chat room last_message_at updated")
            
            # Commit to database
            db.session.commit()
            print(f"✅ Database commit successful")
            print(f"💾 Message saved with:")
            print(f"   Message ID: {admin_message.id}")
            print(f"   Created At: {admin_message.created_at}")
            print(f"   Room ID: {admin_message.chat_room_id}")
            print(f"   Sender Type: {admin_message.sender_type}")
            print(f"   Message Text: '{admin_message.message}'")
            
        except Exception as save_error:
            print(f"❌ Database Save Error: {save_error}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Failed to save message: {str(save_error)}'}), 500

        # Emit real-time message to user with detailed logging
        print(f"📡 Attempting to emit real-time message...")
        try:
            emit_data = {
                'room_id': room_id_int,
                'message': message_text,
                'sender_type': 'admin',
                'timestamp': admin_message.created_at.strftime('%H:%M')
            }
            target_room = f'user_{chat_room.user_id}'
            
            print(f"📡 Emit Data: {emit_data}")
            print(f"📡 Target Room: {target_room}")
            
            socketio.emit('new_message', emit_data, room=target_room)
            print("✅ Real-time message emitted successfully")
            
        except Exception as emit_error:
            print(f"⚠️ Socket emit failed (non-critical): {emit_error}")
            import traceback
            traceback.print_exc()

        # Prepare success response
        response_data = {
            'success': True,
            'message': 'Reply sent successfully',
            'timestamp': admin_message.created_at.strftime('%H:%M'),
            'message_id': admin_message.id
        }
        
        print(f"✅ Success Response: {response_data}")
        print("=" * 60)
        print("🎉 ADMIN SEND REPLY - REQUEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return jsonify(response_data)

    except Exception as e:
        print("=" * 60)
        print("❌ ADMIN SEND REPLY - CRITICAL ERROR")
        print("=" * 60)
        print(f"❌ Error Type: {type(e).__name__}")
        print(f"❌ Error Message: {str(e)}")
        print(f"❌ Error Args: {e.args}")
        
        # Print full stack trace
        print("🔍 Full Stack Trace:")
        import traceback
        traceback.print_exc()
        
        # Rollback database session
        try:
            db.session.rollback()
            print("✅ Database session rolled back")
        except Exception as rollback_error:
            print(f"❌ Rollback Error: {rollback_error}")
        
        error_response = {
            'success': False, 
            'error': f'Server error: {str(e)}',
            'error_type': type(e).__name__
        }
        
        print(f"❌ Error Response: {error_response}")
        print("=" * 60)
        
        return jsonify(error_response), 500


@app.route('/admin/chat/clear', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def admin_clear_chat():
    try:
        print(f"Admin clear chat called")

        # Handle both JSON and form data - sama seperti floating chat
        if request.is_json:
            data = request.get_json()
            room_id = data.get('room_id')
        else:
            room_id = request.form.get('room_id')

        if not room_id:
            return jsonify({'error': 'Room ID required'}), 400

        try:
            room_id = int(room_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid room ID'}), 400

        chat_room = models.ChatRoom.query.get(room_id)
        if not chat_room:
            return jsonify({'error': 'Chat room not found'}), 404

        # Delete all messages in the chat room - sama seperti api_chat_clear
        deleted_count = models.ChatMessage.query.filter_by(chat_room_id=room_id).delete()
        db.session.commit()

        print(f"Deleted {deleted_count} messages from room {room_id}")

        return jsonify({'success': True})

    except Exception as e:
        print(f"Error in admin_clear_chat: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': 'Failed to clear chat'}), 500

# Payment Configuration Routes
@app.route('/admin/payment-config')
@login_required
@admin_required
def admin_payment_config():
    configurations = models.PaymentConfiguration.query.all()
    return render_template('admin/payment_config.html', configurations=configurations)

@app.route('/admin/payment-config/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_payment_config():
    if request.method == 'POST':
        try:
            provider = request.form.get('provider')
            is_sandbox = request.form.get('is_sandbox') == 'true'

            # Validasi provider
            if not provider or provider not in ['midtrans', 'stripe']:
                flash('Provider pembayaran tidak valid!', 'error')
                return render_template('admin/create_payment_config.html')

            # Cek apakah sudah ada konfigurasi aktif untuk provider ini
            existing_config = models.PaymentConfiguration.query.filter_by(
                provider=provider, 
                is_active=True
            ).first()

            if existing_config:
                flash(f'Sudah ada konfigurasi {provider} yang aktif! Nonaktifkan terlebih dahulu sebelum menambah yang baru.', 'warning')
                return render_template('admin/create_payment_config.html')

            config = models.PaymentConfiguration(
                provider=provider,
                is_sandbox=is_sandbox,
                is_active=False  # Start as inactive
            )

            if provider == 'midtrans':
                client_key = request.form.get('midtrans_client_key', '').strip()
                server_key = request.form.get('midtrans_server_key', '').strip()
                merchant_id = request.form.get('midtrans_merchant_id', '').strip()

                if not client_key or not server_key:
                    flash('Client Key dan Server Key harus diisi untuk Midtrans!', 'error')
                    return render_template('admin/create_payment_config.html')

                config.midtrans_client_key = client_key
                config.midtrans_server_key = server_key
                config.midtrans_merchant_id = merchant_id if merchant_id else None

            elif provider == 'stripe':
                publishable_key = request.form.get('stripe_publishable_key', '').strip()
                secret_key = request.form.get('stripe_secret_key', '').strip()

                if not publishable_key or not secret_key:
                    flash('Publishable Key dan Secret Key harus diisi untuk Stripe!', 'error')
                    return render_template('admin/create_payment_config.html')

                config.stripe_publishable_key = publishable_key
                config.stripe_secret_key = secret_key

            # Set callback URLs
            base_url = request.host_url.rstrip('/')
            config.callback_finish_url = f"{base_url}/payment/finish"
            config.callback_unfinish_url = f"{base_url}/payment/unfinish"
            config.callback_error_url = f"{base_url}/payment/error"
            config.notification_url = f"{base_url}/notification/handling"

            # Set additional URLs for Midtrans
            if provider == 'midtrans':
                config.recurring_notification_url = f"{base_url}/notification/recurring"
                config.account_linking_url = f"{base_url}/notification/account-linking"

            db.session.add(config)
            db.session.commit()

            environment_text = "Sandbox" if is_sandbox else "Production"
            flash(f'Konfigurasi pembayaran {provider.title()} ({environment_text}) berhasil ditambahkan!', 'success')
            return redirect(url_for('admin_payment_config'))

        except Exception as e:
            db.session.rollback()
            print(f"Error creating payment config: {str(e)}")
            flash(f'Terjadi kesalahan saat menyimpan konfigurasi: {str(e)}', 'error')
            return render_template('admin/create_payment_config.html')

    return render_template('admin/create_payment_config.html')

@app.route('/admin/payment-config/<int:config_id>/toggle', methods=['POST'])
@login_required
@admin_required
def admin_toggle_payment_config(config_id):
    config = models.PaymentConfiguration.query.get_or_404(config_id)

    # Deactivate all other configs of the same provider
    if not config.is_active:
        models.PaymentConfiguration.query.filter_by(provider=config.provider).update({'is_active': False})

    config.is_active = not config.is_active
    config.updated_at = datetime.utcnow()

    db.session.commit()

    status = 'diaktifkan' if config.is_active else 'dinonaktifkan'
    flash(f'Konfigurasi {config.provider} berhasil {status}!', 'success')
    return redirect(url_for('admin_payment_config'))

# Midtrans Payment Callback Endpoints
@app.route('/payment/finish')
def payment_finish():
    order_id = request.args.get('order_id')
    status_code = request.args.get('status_code')
    transaction_status = request.args.get('transaction_status')

    if status_code == '200' and transaction_status == 'settlement':
        flash('Pembayaran berhasil! Terima kasih atas pesanan Anda.', 'success')
        return redirect(url_for('payment_success'))
    else:
        flash('Pembayaran gagal atau dibatalkan.', 'error')
        return redirect(url_for('cart'))

@app.route('/payment/unfinish')
def payment_unfinish():
    flash('Pembayaran belum diselesaikan. Silakan coba lagi.', 'warning')
    return redirect(url_for('cart'))

@app.route('/payment/error')
def payment_error():
    flash('Terjadi kesalahan dalam pembayaran. Silakan coba lagi.', 'error')
    return redirect(url_for('cart'))

@app.route('/payment/notification', methods=['POST'])
@csrf.exempt
def payment_notification():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        # Get active Midtrans configuration
        midtrans_config = models.PaymentConfiguration.query.filter_by(
            provider='midtrans', 
            is_active=True
        ).first()

        if not midtrans_config:
            return jsonify({'status': 'error', 'message': 'Midtrans not configured'}), 400

        # Verify signature here (implementation depends on your requirements)
        order_id = data.get('order_id')
        transaction_status = data.get('transaction_status')
        fraud_status = data.get('fraud_status')

        if order_id:
            # Find the transaction
            midtrans_transaction = models.MidtransTransaction.query.filter_by(
                transaction_id=order_id
            ).first()

            if midtrans_transaction:
                midtrans_transaction.transaction_status = transaction_status
                midtrans_transaction.fraud_status = fraud_status
                midtrans_transaction.midtrans_response = json.dumps(data)
                midtrans_transaction.updated_at = datetime.utcnow()

                # Update order status based on transaction status
                if transaction_status == 'settlement' and fraud_status == 'accept':
                    midtrans_transaction.order.status = 'paid'
                elif transaction_status in ['deny', 'cancel', 'expire']:
                    midtrans_transaction.order.status = 'cancelled'

                db.session.commit()

        return jsonify({'status': 'ok'})

    except Exception as e:
        print(f"Payment notification error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal error'}), 500

@app.route('/notification/handling', methods=['POST'])
@csrf.exempt
def notification_handling():
    """
    URL Callback utama untuk notifikasi pembayaran Midtrans
    Menangani semua jenis notifikasi dari Midtrans
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        # Log notifikasi untuk debugging
        print(f"Midtrans notification received: {json.dumps(data)}")

        # Get active Midtrans configuration
        midtrans_config = models.PaymentConfiguration.query.filter_by(
            provider='midtrans', 
            is_active=True
        ).first()

        if not midtrans_config:
            return jsonify({'status': 'error', 'message': 'Midtrans not configured'}), 400

        # Extract data from notification
        order_id = data.get('order_id')
        transaction_status = data.get('transaction_status')
        fraud_status = data.get('fraud_status')
        payment_type = data.get('payment_type')
        gross_amount = data.get('gross_amount')
        settlement_time = data.get('settlement_time')

        if order_id:
            # Find or create the transaction record
            midtrans_transaction = models.MidtransTransaction.query.filter_by(
                transaction_id=order_id
            ).first()

            if not midtrans_transaction:
                # Create new transaction record if not exists
                # Try to find order by order_id pattern
                try:
                    # Extract order ID from transaction ID if it follows pattern ORDER-{user_id}-{timestamp}-{uuid}
                    order_parts = order_id.split('-')
                    if len(order_parts) >= 3 and order_parts[0] == 'ORDER':
                        user_id = int(order_parts[1])
                        # Find recent order for this user
                        recent_order = models.Order.query.filter_by(
                            user_id=user_id,
                            status='pending'
                        ).order_by(models.Order.created_at.desc()).first()

                        if recent_order:
                            midtrans_transaction = models.MidtransTransaction(
                                order_id=recent_order.id,
                                transaction_id=order_id,
                                gross_amount=float(gross_amount) if gross_amount else 0,
                                payment_type=payment_type,
                                transaction_status=transaction_status,
                                fraud_status=fraud_status
                            )
                            db.session.add(midtrans_transaction)
                            db.session.flush()
                except:
                    pass

            if midtrans_transaction:
                # Update transaction details
                midtrans_transaction.transaction_status = transaction_status
                midtrans_transaction.fraud_status = fraud_status
                midtrans_transaction.payment_type = payment_type
                midtrans_transaction.midtrans_response = json.dumps(data)
                midtrans_transaction.updated_at = datetime.utcnow()

                if settlement_time:
                    try:
                        midtrans_transaction.settlement_time = datetime.strptime(
                            settlement_time, '%Y-%m-%d %H:%M:%S'
                        )
                    except:
                        pass

                # Update order status based on transaction status
                order = midtrans_transaction.order
                if transaction_status == 'settlement' and fraud_status == 'accept':
                    order.status = 'paid'
                elif transaction_status in ['deny', 'cancel', 'expire', 'failure']:
                    order.status = 'cancelled'
                elif transaction_status == 'pending':
                    order.status = 'pending'

                db.session.commit()

                print(f"Transaction {order_id} updated with status: {transaction_status}")

        return jsonify({'status': 'ok'})

    except Exception as e:
        print(f"Notification handling error: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Internal error'}), 500

@app.route('/notification/recurring', methods=['POST'])
@csrf.exempt
def notification_recurring():
    """
    URL untuk notifikasi pembayaran berulang (subscription)
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        print(f"Recurring payment notification: {json.dumps(data)}")

        # Handle recurring payment logic here
        # This can be extended based on your subscription needs

        return jsonify({'status': 'ok'})

    except Exception as e:
        print(f"Recurring notification error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal error'}), 500

@app.route('/notification/account-linking', methods=['POST'])
@csrf.exempt
def notification_account_linking():
    """
    URL untuk notifikasi menghubungkan akun (account linking)
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        print(f"Account linking notification: {json.dumps(data)}")

        # Handle account linking logic here
        # This can be extended based on your account linking needs

        return jsonify({'status': 'ok'})

    except Exception as e:
        print(f"Account linking notification error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal error'}), 500

# API endpoint for cart count
@app.route('/api/cart/count')
@login_required
def api_cart_count():
    try:
        cart_count = models.CartItem.query.filter_by(user_id=current_user.id).count()
        return jsonify({'count': cart_count})
    except Exception as e:
        print(f"Error getting cart count: {str(e)}")
        return jsonify({'count': 0})

@app.route('/admin/orders')
@login_required
@staff_required
def admin_orders():
    orders = models.Order.query.order_by(models.Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/order/<int:order_id>/update', methods=['POST'])
@login_required
@staff_required
def admin_update_order(order_id):
    order = models.Order.query.get_or_404(order_id)

    new_status = request.form.get('status')
    tracking_number = request.form.get('tracking_number', '').strip()
    courier_service = request.form.get('courier_service', '').strip()

    if new_status not in ['pending', 'paid', 'shipped', 'delivered', 'cancelled']:
        flash('Status tidak valid!', 'error')
        return redirect(url_for('admin_orders'))

    order.status = new_status
    order.tracking_number = tracking_number if tracking_number else None
    order.courier_service = courier_service if courier_service else None
    order.updated_at = datetime.utcnow()

    db.session.commit()

    flash(f'Pesanan #{order.id} berhasil diperbarui!', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/order/<int:order_id>/quick-ship', methods=['POST'])
@login_required
@staff_required
def admin_quick_ship_order(order_id):
    order = models.Order.query.get_or_404(order_id)

    # Pastikan order masih dalam status paid
    if order.status != 'paid':
        flash(f'Pesanan #{order.id} tidak dalam status yang dapat dikirim!', 'error')
        return redirect(url_for('admin_orders'))

    tracking_number = request.form.get('tracking_number', '').strip()
    courier_service = request.form.get('courier_service', '').strip()

    if not tracking_number:
        flash('Nomor resi harus diisi!', 'error')
        return redirect(url_for('admin_orders'))

    # Check if tracking number already exists
    existing_order = models.Order.query.filter_by(tracking_number=tracking_number).first()
    if existing_order and existing_order.id != order.id:
        flash(f'Nomor resi {tracking_number} sudah digunakan untuk pesanan #{existing_order.id}!', 'error')
        return redirect(url_for('admin_orders'))

    # Update order
    order.status = 'shipped'
    order.tracking_number = tracking_number
    order.courier_service = courier_service if courier_service else None
    order.updated_at = datetime.utcnow()

    db.session.commit()

    flash(f'Pesanan #{order.id} berhasil dikirim dengan resi {tracking_number}!', 'success')
    return redirect(url_for('admin_orders'))

def generate_tracking_number():
    """Generate a unique tracking number"""
    prefix = "HRT"
    numbers = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}{numbers}"

@app.route('/admin/order/<int:order_id>/print_label')
@login_required
@staff_required
def print_order_label(order_id):
    order = models.Order.query.get_or_404(order_id)
    store_profile = models.StoreProfile.get_active_profile()

    # Generate tracking number if not exists
    if not order.tracking_number:
        order.tracking_number = generate_tracking_number()
        db.session.commit()

    # Create PDF for thermal printer (120mm width)
    # 120mm = 340 points (at 72 DPI)
    # Height depends on content

    buffer = io.BytesIO()

    # Calculate content height first
    content_lines = []

    # Store header
    content_lines.extend([
        ('header', store_profile.store_name if store_profile else 'HURTROCK MUSIC STORE'),
        ('subheader', store_profile.store_tagline if store_profile else 'Toko Alat Musik Terpercaya'),
        ('divider', '=' * 35),
        ('label', 'LABEL PENGIRIMAN'),
        ('divider', '=' * 35),
    ])

    # Order info
    content_lines.extend([
        ('order', f"Order #{order.id}"),
        ('tracking', f"Resi: {order.tracking_number}"),
        ('date', f"Tanggal: {order.created_at.strftime('%d/%m/%Y %H:%M')}"),
        ('courier', f"Kurir: {order.courier_service or 'Reguler'}"),
        ('divider', '-' * 35),
    ])

    # Store address (sender)
    content_lines.extend([
        ('section', 'PENGIRIM:'),
        ('sender_name', store_profile.store_name if store_profile else 'Hurtrock Music Store'),
    ])

    if store_profile:
        content_lines.append(('sender_address', store_profile.formatted_address))
        if store_profile.store_phone:
            content_lines.append(('sender_phone', f"Telp: {store_profile.store_phone}"))
    else:
        content_lines.extend([
            ('sender_address', 'Jl. Musik Raya No. 123, Jakarta'),
            ('sender_phone', 'Telp: 0821-1555-8035')
        ])

    content_lines.append(('divider', '-' * 35))

    # Recipient info
    content_lines.extend([
        ('section', 'PENERIMA:'),
        ('recipient_name', order.user.name),
    ])

    if order.user.phone:
        content_lines.append(('recipient_phone', f"Telp: {order.user.phone}"))

    if order.user.address:
        # Split long address into multiple lines
        address = order.user.address.replace('\n', ' ')
        if len(address) > 32:
            words = address.split(' ')
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + word) <= 32:
                    current_line += word + " "
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())

            for i, line in enumerate(lines):
                content_lines.append(('recipient_address', line))
        else:
            content_lines.append(('recipient_address', address))

    content_lines.append(('divider', '-' * 35))

    # Items
    content_lines.append(('section', 'BARANG:'))
    for item in order.order_items:
        item_text = f"{item.product.name[:25]}{'...' if len(item.product.name) > 25 else ''}"
        content_lines.append(('item', f"{item_text} x{item.quantity}"))

    content_lines.extend([
        ('divider', '-' * 35),
        ('total', f"TOTAL: {order.formatted_total}"),
        ('divider', '=' * 35),
    ])

    # Footer
    if store_profile and store_profile.store_website:
        content_lines.append(('footer', store_profile.store_website))

    content_lines.append(('footer_note', 'Terima kasih atas kepercayaan Anda'))

    # Calculate page height based on content
    line_height = 14
    header_height = 20
    margin = 20
    total_height = margin * 2 + (len(content_lines) * line_height) + header_height

    # Set minimum height
    if total_height < 400:
        total_height = 400

    # Create PDF with calculated dimensions
    width = 340  # 120mm
    height = total_height

    p = canvas.Canvas(buffer, pagesize=(width, height))

    # Set fonts
    y_pos = height - margin

    for line_type, text in content_lines:
        if line_type == 'header':
            p.setFont("Helvetica-Bold", 16)
            text_width = p.stringWidth(text, "Helvetica-Bold", 16)
            x_center = (width - text_width) / 2
            p.drawString(x_center, y_pos, text)
            y_pos -= 20
        elif line_type == 'subheader':
            p.setFont("Helvetica", 10)
            text_width = p.stringWidth(text, "Helvetica", 10)
            x_center = (width - text_width) / 2
            p.drawString(x_center, y_pos, text)
            y_pos -= 15
        elif line_type == 'label':
            p.setFont("Helvetica-Bold", 12)
            text_width = p.stringWidth(text, "Helvetica-Bold", 12)
            x_center = (width - text_width) / 2
            p.drawString(x_center, y_pos, text)
            y_pos -= 15
        elif line_type == 'divider':
            p.setFont("Helvetica", 10)
            text_width = p.stringWidth(text, "Helvetica", 10)
            x_center = (width - text_width) / 2
            p.drawString(x_center, y_pos, text)
            y_pos -= 12
        elif line_type in ['order', 'tracking', 'date', 'courier']:
            p.setFont("Helvetica-Bold", 10)
            p.drawString(margin, y_pos, text)
            y_pos -= 12
        elif line_type == 'section':
            p.setFont("Helvetica-Bold", 11)
            p.drawString(margin, y_pos, text)
            y_pos -= 13
        elif line_type in ['sender_name', 'recipient_name']:
            p.setFont("Helvetica-Bold", 10)
            p.drawString(margin + 10, y_pos, text)
            y_pos -= 12
        elif line_type in ['sender_address', 'sender_phone', 'recipient_address', 'recipient_phone']:
            p.setFont("Helvetica", 9)
            p.drawString(margin + 10, y_pos, text)
            y_pos -= 11
        elif line_type == 'item':
            p.setFont("Helvetica", 9)
            p.drawString(margin + 10, y_pos, text)
            y_pos -= 11
        elif line_type == 'total':
            p.setFont("Helvetica-Bold", 12)
            text_width = p.stringWidth(text, "Helvetica-Bold", 12)
            x_center = (width - text_width) / 2
            p.drawString(x_center, y_pos, text)
            y_pos -= 15
        elif line_type in ['footer', 'footer_note']:
            p.setFont("Helvetica", 8)
            text_width = p.stringWidth(text, "Helvetica", 8)
            x_center = (width - text_width) / 2
            p.drawString(x_center, y_pos, text)
            y_pos -= 10
        else:
            p.setFont("Helvetica", 9)
            p.drawString(margin, y_pos, text)
            y_pos -= 11

    p.showPage()
    p.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'thermal_label_{order.id}.pdf',
        mimetype='application/pdf'
    )

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = models.User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/analytics')
@login_required
@staff_required
def admin_analytics():
    from sqlalchemy import func, extract
    from decimal import Decimal

    # Penjualan 7 hari terakhir
    seven_days_ago = datetime.utcnow().date() - timedelta(days=6)
    daily_sales = db.session.query(
        func.date(models.Order.created_at).label('date'),
        func.sum(models.Order.total_amount).label('total'),
        func.count(models.Order.id).label('orders_count')
    ).filter(
        func.date(models.Order.created_at) >= seven_days_ago,
        models.Order.status.in_(['paid', 'shipped', 'delivered'])
    ).group_by(func.date(models.Order.created_at)).order_by(
        func.date(models.Order.created_at)
    ).all()

    # Penjualan per kategori dengan explicit join
    category_sales = db.session.query(
        models.Category.name,
        func.sum(models.OrderItem.quantity * models.OrderItem.price).label('total_sales'),
        func.sum(models.OrderItem.quantity).label('total_quantity')
    ).select_from(models.Category)\
    .join(models.Product, models.Product.category_id == models.Category.id)\
    .join(models.OrderItem, models.OrderItem.product_id == models.Product.id)\
    .join(models.Order, models.Order.id == models.OrderItem.order_id)\
    .filter(
        models.Order.status.in_(['paid', 'shipped', 'delivered'])
    ).group_by(models.Category.id, models.Category.name).order_by(
        func.sum(models.OrderItem.quantity * models.OrderItem.price).desc()
    ).all()

    # Pelanggan terbaik dengan explicit join
    top_customers = db.session.query(
        models.User.name,
        models.User.email,
        func.sum(models.Order.total_amount).label('total_spent'),
        func.count(models.Order.id).label('orders_count')
    ).select_from(models.User)\
    .join(models.Order, models.Order.user_id == models.User.id)\
    .filter(
        models.Order.status.in_(['paid', 'shipped', 'delivered'])
    ).group_by(models.User.id, models.User.name, models.User.email).order_by(
        func.sum(models.Order.total_amount).desc()
    ).limit(10).all()

    return render_template('admin/analytics.html',
                         daily_sales=daily_sales,
                         category_sales=category_sales,
                         top_customers=top_customers)

@app.route('/admin/user/<int:user_id>/change_role', methods=['POST'])
@login_required
@admin_required
def admin_change_user_role(user_id):
    user = models.User.query.get_or_404(user_id)
    new_role = request.form.get('role')

    if new_role not in ['admin', 'staff', 'buyer']:
        flash('Role tidak valid!', 'error')
        return redirect(url_for('admin_users'))

    # Prevent changing own role
    if user.id == current_user.id:
        flash('Tidak bisa mengubah role sendiri!', 'error')
        return redirect(url_for('admin_users'))

    user.role = new_role
    db.session.commit()

    flash(f'Role {user.name} berhasil diubah menjadi {new_role}!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    user = models.User.query.get_or_404(user_id)

    # Prevent deleting own account
    if user.id == current_user.id:
        flash('Tidak bisa menghapus akun sendiri!', 'error')
        return redirect(url_for('admin_users'))

    # Check if user has orders
    if user.orders:
        flash('Tidak bisa menghapus user yang memiliki riwayat pesanan!', 'error')
        return redirect(url_for('admin_users'))

    user_name = user.name
    db.session.delete(user)
    db.session.commit()

    flash(f'User {user_name} berhasil dihapus!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Validate role
        if role not in ['admin', 'staff', 'buyer']:
            flash('Role tidak valid!', 'error')
            return render_template('admin/add_user.html')

        # Check if email already exists
        if models.User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar!', 'error')
            return render_template('admin/add_user.html')

        # Create new user
        hashed_password = generate_password_hash(password)
        user = models.User(
            name=name,
            email=email,
            password_hash=hashed_password,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        flash(f'User {name} berhasil ditambahkan dengan role {role}!', 'success')
        return redirect(url_for('admin_users'))

    return render_template('admin/add_user.html')

@app.route('/admin/user/<int:user_id>/reset_password', methods=['POST'])
@login_required
@admin_required
def admin_reset_password(user_id):
    user = models.User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')

    if not new_password or len(new_password) < 6:
        flash('Password harus minimal 6 karakter!', 'error')
        return redirect(url_for('admin_users'))

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    flash(f'Password {user.name} berhasil direset!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/export/daily_sales')
@login_required
@staff_required
def export_daily_sales():
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment
    except ImportError:
        flash('Package openpyxl diperlukan untuk export Excel. Silakan install terlebih dahulu.', 'error')
        return redirect(url_for('admin_analytics'))

    from sqlalchemy import func
    import io

    # Ambil data 30 hari terakhir
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=29)

    daily_sales = db.session.query(
        func.date(models.Order.created_at).label('date'),
        func.sum(models.Order.total_amount).label('total_sales'),
        func.count(models.Order.id).label('orders_count'),
        func.avg(models.Order.total_amount).label('avg_order_value')
    ).filter(
        func.date(models.Order.created_at) >= thirty_days_ago,
        models.Order.status.in_(['paid', 'shipped', 'delivered'])
    ).group_by(func.date(models.Order.created_at)).order_by(
        func.date(models.Order.created_at)
    ).all()

    # Buat workbook Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Laporan Penjualan Harian"

    # Header
    headers = ['Tanggal', 'Total Penjualan (Rp)', 'Jumlah Pesanan', 'Rata-rata Order (Rp)']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    # Data
    for row, sale in enumerate(daily_sales, 2):
        ws.cell(row=row, column=1, value=sale.date.strftime('%d/%m/%Y'))
        ws.cell(row=row, column=2, value=float(sale.total_sales or 0))
        ws.cell(row=row, column=3, value=sale.orders_count)
        ws.cell(row=row, column=4, value=float(sale.avg_order_value or 0))

    # Format kolom
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 20

    # Simpan ke buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'laporan_penjualan_harian_{datetime.utcnow().strftime("%Y%m%d")}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/admin/order/<int:order_id>/print_address')
@login_required
@staff_required
def print_order_address(order_id):
    order = models.Order.query.get_or_404(order_id)
    store_profile = models.StoreProfile.get_active_profile()

    # Create PDF untuk alamat pengiriman thermal (120mm width)
    buffer = io.BytesIO()

    # Calculate content
    content_lines = []

    # Header
    content_lines.extend([
        ('header', 'ALAMAT PENGIRIMAN'),
        ('divider', '=' * 35),
    ])

    # Store info (sender)
    content_lines.append(('section', 'DARI:'))
    if store_profile:
        content_lines.extend([
            ('store_name', store_profile.store_name),
            ('store_address', store_profile.formatted_address),
        ])
        if store_profile.store_phone:
            content_lines.append(('store_contact', f"Telp: {store_profile.store_phone}"))
        if store_profile.store_email:
            content_lines.append(('store_contact', f"Email: {store_profile.store_email}"))
    else:
        content_lines.extend([
            ('store_name', 'Hurtrock Music Store'),
            ('store_address', 'Jl. Musik Raya No. 123, Jakarta'),
            ('store_contact', 'Telp: 0821-1555-8035'),
        ])

    content_lines.append(('divider', '-' * 35))

    # Recipient info
    content_lines.extend([
        ('section', 'KEPADA:'),
        ('recipient_name', order.user.name.upper()),
    ])

    if order.user.phone:
        content_lines.append(('recipient_contact', f"Telp: {order.user.phone}"))

    if order.user.address:
        # Split long address
        address = order.user.address.replace('\n', ' ')
        if len(address) > 32:
            words = address.split(' ')
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + word) <= 32:
                    current_line += word + " "
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())

            for line in lines:
                content_lines.append(('recipient_address', line))
        else:
            content_lines.append(('recipient_address', address))

    content_lines.append(('divider', '-' * 35))

    # Order info
    content_lines.extend([
        ('order_info', f"Order #{order.id}"),
        ('order_date', f"Tanggal: {order.created_at.strftime('%d/%m/%Y %H:%M')}"),
    ])

    if order.tracking_number:
        content_lines.append(('tracking', f"Resi: {order.tracking_number}"))

    if order.courier_service:
        content_lines.append(('courier', f"Kurir: {order.courier_service}"))

    content_lines.extend([
        ('total', f"Total: {order.formatted_total}"),
        ('divider', '=' * 35),
        ('footer', 'Terima kasih atas kepercayaan Anda'),
    ])

    # Calculate dimensions
    width = 340  # 120mm
    line_height = 12
    margin = 20
    total_height = margin * 2 + (len(content_lines) * line_height) + 40

    if total_height < 400:
        total_height = 400

    p = canvas.Canvas(buffer, pagesize=(width, total_height))

    y_pos = total_height - margin

    for line_type, text in content_lines:
        if line_type == 'header':
            p.setFont("Helvetica-Bold", 14)
            text_width = p.stringWidth(text, "Helvetica-Bold", 14)
            x_center = (width - text_width) / 2
            p.drawString(x_center, y_pos, text)
            y_pos -= 18
        elif line_type == 'divider':
            p.setFont("Helvetica", 10)
            text_width = p.stringWidth(text, "Helvetica", 10)
            x_center = (width - text_width) / 2
            p.drawString(x_center, y_pos, text)
            y_pos -= 12
        elif line_type == 'section':
            p.setFont("Helvetica-Bold", 12)
            p.drawString(margin, y_pos, text)
            y_pos -= 14
        elif line_type in ['store_name', 'recipient_name']:
            p.setFont("Helvetica-Bold", 11)
            p.drawString(margin + 5, y_pos, text)
            y_pos -= 13
        elif line_type in ['store_address', 'store_contact', 'recipient_address', 'recipient_contact']:
            p.setFont("Helvetica", 9)
            p.drawString(margin + 5, y_pos, text)
            y_pos -= 11
        elif line_type in ['order_info', 'order_date', 'tracking', 'courier']:
            p.setFont("Helvetica-Bold", 10)
            p.drawString(margin, y_pos, text)
            y_pos -= 12
        elif line_type == 'total':
            p.setFont("Helvetica-Bold", 12)
            text_width = p.stringWidth(text, "Helvetica-Bold", 12)
            x_center = (width - text_width) / 2
            p.drawString(x_center, y_pos, text)
            y_pos -= 15
        elif line_type == 'footer':
            p.setFont("Helvetica", 8)
            text_width = p.stringWidth(text, "Helvetica", 8)
            x_center = (width - text_width) / 2
            p.drawString(x_center, y_pos, text)
            y_pos -= 10
        else:
            p.setFont("Helvetica", 9)
            p.drawString(margin, y_pos, text)
            y_pos -= 11

    p.showPage()
    p.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'thermal_address_{order.id}.pdf',
        mimetype='application/pdf'
    )

# Shipping Services Management
@app.route('/admin/shipping')
@login_required
@admin_required
def admin_shipping_services():
    services = models.ShippingService.query.all()
    # Convert to dict for JSON serialization
    services_data = []
    for service in services:
        services_data.append({
            'id': service.id,
            'name': service.name,
            'code': service.code,
            'base_price': float(service.base_price),
            'price_per_kg': float(service.price_per_kg),
            'price_per_km': float(service.price_per_km),
            'volume_factor': float(service.volume_factor),
            'min_days': service.min_days,
            'max_days': service.max_days,
            'is_active': service.is_active
        })
    return render_template('admin/shipping.html', services=services, services_data=services_data)

@app.route('/admin/shipping/add', methods=['POST'])
@login_required
@admin_required
def admin_add_shipping_service():
    try:
        name = request.form['name']
        code = request.form['code']
        base_price = float(request.form['base_price'])
        price_per_kg = float(request.form['price_per_kg'])
        price_per_km = float(request.form.get('price_per_km', 0))
        volume_factor = float(request.form.get('volume_factor', 5000))
        min_days = int(request.form.get('min_days', 1))
        max_days = int(request.form.get('max_days', 3))

        service = models.ShippingService(
            name=name,
            code=code,
            base_price=base_price,
            price_per_kg=price_per_kg,
            price_per_km=price_per_km,
            volume_factor=volume_factor,
            min_days=min_days,
            max_days=max_days
        )

        db.session.add(service)
        db.session.commit()

        flash(f'Jasa kirim {name} berhasil ditambahkan!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('admin_shipping_services'))

@app.route('/admin/shipping/<int:service_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_shipping_service(service_id):
    service = models.ShippingService.query.get_or_404(service_id)

    try:
        service.name = request.form['name']
        service.code = request.form['code']
        service.base_price = float(request.form['base_price'])
        service.price_per_kg = float(request.form['price_per_kg'])
        service.price_per_km = float(request.form.get('price_per_km', 0))
        service.volume_factor = float(request.form.get('volume_factor', 5000))
        service.min_days = int(request.form.get('min_days', 1))
        service.max_days = int(request.form.get('max_days', 3))
        service.is_active = request.form.get('is_active') == 'on'

        db.session.commit()

        flash(f'Jasa kirim {service.name} berhasil diperbarui!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('admin_shipping_services'))

@app.route('/admin/shipping/<int:service_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_shipping_service(service_id):
    service = models.ShippingService.query.get_or_404(service_id)

    # Check if service is used in orders
    if service.orders:
        flash('Tidak bisa menghapus jasa kirim yang sedang digunakan di pesanan!', 'error')
        return redirect(url_for('admin_shipping_services'))

    service_name = service.name
    db.session.delete(service)
    db.session.commit()

    flash(f'Jasa kirim {service_name} berhasil dihapus!', 'success')
    return redirect(url_for('admin_shipping_services'))

# Supplier Management
@app.route('/admin/suppliers')
@login_required
@admin_required
def admin_suppliers():
    suppliers = models.Supplier.query.all()
    # Convert to dict for JSON serialization
    suppliers_data = []
    for supplier in suppliers:
        suppliers_data.append({
            'id': supplier.id,
            'name': supplier.name,
            'contact_person': supplier.contact_person,
            'email': supplier.email,
            'phone': supplier.phone,
            'address': supplier.address,
            'company': supplier.company,
            'notes': supplier.notes,
            'is_active': supplier.is_active
        })
    return render_template('admin/suppliers.html', suppliers=suppliers, suppliers_data=suppliers_data)

@app.route('/admin/suppliers/add', methods=['POST'])
@login_required
@admin_required
def admin_add_supplier():
    try:
        name = request.form['name']
        contact_person = request.form.get('contact_person', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        company = request.form.get('company', '')
        notes = request.form.get('notes', '')

        supplier = models.Supplier(
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address,
            company=company,
            notes=notes
        )

        db.session.add(supplier)
        db.session.commit()

        flash(f'Supplier {name} berhasil ditambahkan!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('admin_suppliers'))

@app.route('/admin/suppliers/<int:supplier_id>/edit', methods=['POST'])
@login_required
@admin_required
def admin_edit_supplier(supplier_id):
    supplier = models.Supplier.query.get_or_404(supplier_id)

    try:
        supplier.name = request.form['name']
        supplier.contact_person = request.form.get('contact_person', '')
        supplier.email = request.form.get('email', '')
        supplier.phone = request.form.get('phone', '')
        supplier.address = request.form.get('address', '')
        supplier.company = request.form.get('company', '')
        supplier.notes = request.form.get('notes', '')
        supplier.is_active = request.form.get('is_active') == 'on'

        db.session.commit()

        flash(f'Supplier {supplier.name} berhasil diperbarui!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('admin_suppliers'))

@app.route('/admin/suppliers/<int:supplier_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_supplier(supplier_id):
    supplier = models.Supplier.query.get_or_404(supplier_id)

    # Check if supplier has products
    if supplier.products:
        flash('Tidak bisa menghapus supplier yang memiliki produk!', 'error')
        return redirect(url_for('admin_suppliers'))

    supplier_name = supplier.name
    db.session.delete(supplier)
    db.session.commit()

    flash(f'Supplier {supplier_name} berhasil dihapus!', 'success')
    return redirect(url_for('admin_suppliers'))

# Store Profile Management
@app.route('/admin/store-profile')
@login_required
@admin_required
def admin_store_profile():
    profile = models.StoreProfile.get_active_profile()
    if not profile:
        # Create default profile if none exists
        profile = models.StoreProfile(
            store_name='Hurtrock Music Store',
            store_tagline='Toko Alat Musik Terpercaya',
            store_address='Jl. Musik Raya No. 123',
            store_city='Jakarta',
            store_postal_code='12345',
            store_phone='0821-1555-8035',
            store_email='info@hurtrock.com'
        )
        db.session.add(profile)
        db.session.commit()

    return render_template('admin/store_profile.html', profile=profile)

@app.route('/admin/store-profile/update', methods=['POST'])
@login_required
@admin_required
def admin_update_store_profile():
    profile = models.StoreProfile.get_active_profile()
    if not profile:
        profile = models.StoreProfile()
        db.session.add(profile)

    try:
        # Basic store information
        profile.store_name = request.form.get('store_name', '').strip()
        profile.store_tagline = request.form.get('store_tagline', '').strip()
        profile.store_address = request.form.get('store_address', '').strip()
        profile.store_city = request.form.get('store_city', '').strip()
        profile.store_postal_code = request.form.get('store_postal_code', '').strip()
        profile.store_phone = request.form.get('store_phone', '').strip()
        profile.store_email = request.form.get('store_email', '').strip()
        profile.store_website = request.form.get('store_website', '').strip()

        # Branch information
        profile.branch_name = request.form.get('branch_name', '').strip()
        profile.branch_code = request.form.get('branch_code', '').strip()
        profile.branch_manager = request.form.get('branch_manager', '').strip()

        # Business information
        profile.business_license = request.form.get('business_license', '').strip()
        profile.tax_number = request.form.get('tax_number', '').strip()

        # Operating hours
        profile.operating_hours = request.form.get('operating_hours', '').strip()

        # Social media
        profile.facebook_url = request.form.get('facebook_url', '').strip()
        profile.instagram_url = request.form.get('instagram_url', '').strip()
        profile.whatsapp_number = request.form.get('whatsapp_number', '').strip()

        # Colors
        profile.primary_color = request.form.get('primary_color', '#FF6B35')
        profile.secondary_color = request.form.get('secondary_color', '#FF8C42')

        # Handle logo upload
        if 'logo' in request.files and request.files['logo'].filename:
            file = request.files['logo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"logo_{uuid.uuid4()}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                file.save(filepath)
                compress_image(filepath)
                profile.logo_url = f"/static/images/{filename}"

        profile.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Profil toko berhasil diperbarui!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('admin_store_profile'))

# Restock Order Management
@app.route('/admin/restock')
@login_required
@admin_required
def admin_restock_orders():
    restock_orders = models.RestockOrder.query.order_by(models.RestockOrder.created_at.desc()).all()
    suppliers = models.Supplier.query.filter_by(is_active=True).all()
    products = models.Product.query.filter_by(is_active=True).all()

    # Convert to dict for JSON serialization
    restock_orders_data = []
    for order in restock_orders:
        order_data = {
            'id': order.id,
            'supplier': {
                'name': order.supplier.name,
                'contact_person': order.supplier.contact_person
            },
            'status': order.status,
            'total_amount': float(order.total_amount),
            'formatted_total': order.formatted_total,
            'created_at': order.created_at.isoformat(),
            'expected_date': order.expected_date.isoformat() if order.expected_date else None,
            'received_date': order.received_date.isoformat() if order.received_date else None,
            'notes': order.notes,
            'items': []
        }
        for item in order.items:
            order_data['items'].append({
                'product': {'name': item.product.name},
                'quantity_ordered': item.quantity_ordered,
                'unit_cost': float(item.unit_cost)
            })
        restock_orders_data.append(order_data)

    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'stock_quantity': product.stock_quantity
        })

    return render_template('admin/restock.html', 
                         restock_orders=restock_orders, 
                         suppliers=suppliers, 
                         products=products,
                         restock_orders_data=restock_orders_data,
                         products_data=products_data)

@app.route('/admin/restock/create', methods=['POST'])
@login_required
@admin_required
def admin_create_restock_order():
    try:
        supplier_id = int(request.form['supplier_id'])
        notes = request.form.get('notes', '')
        expected_date_str = request.form.get('expected_date', '')

        expected_date = None
        if expected_date_str:
            expected_date = datetime.strptime(expected_date_str, '%Y-%m-%d')

        restock_order = models.RestockOrder(
            supplier_id=supplier_id,
            notes=notes,
            expected_date=expected_date,
            created_by=current_user.id
        )

        db.session.add(restock_order)
        db.session.flush()  # Get the order ID

        # Add items
        product_ids = request.form.getlist('product_ids[]')
        quantities = request.form.getlist('quantities[]')
        unit_costs = request.form.getlist('unit_costs[]')

        total_amount = 0
        for i, product_id in enumerate(product_ids):
            if product_id and quantities[i] and unit_costs[i]:
                quantity = int(quantities[i])
                unit_cost = float(unit_costs[i])

                item = models.RestockOrderItem(
                    restock_order_id=restock_order.id,
                    product_id=int(product_id),
                    quantity_ordered=quantity,
                    unit_cost=unit_cost
                )
                db.session.add(item)
                total_amount += quantity * unit_cost

        restock_order.total_amount = total_amount
        db.session.commit()

        flash(f'Order restock #{restock_order.id} berhasil dibuat!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('admin_restock_orders'))

@app.route('/admin/restock/<int:order_id>/update_status', methods=['POST'])
@login_required
@admin_required
def admin_update_restock_status(order_id):
    restock_order = models.RestockOrder.query.get_or_404(order_id)

    try:
        new_status = request.form.get('status')
        if new_status not in ['pending', 'ordered', 'received', 'cancelled']:
            flash('Status tidak valid!', 'error')
            return redirect(url_for('admin_restock_orders'))

        restock_order.status = new_status

        if new_status == 'received':
            restock_order.received_date = datetime.utcnow()

            # Update product stock quantities
            for item in restock_order.items:
                item.quantity_received = item.quantity_ordered
                product = item.product
                product.stock_quantity += item.quantity_ordered

        db.session.commit()

        flash(f'Status restock order #{restock_order.id} berhasil diperbarui!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('admin_restock_orders'))

@app.route('/admin/restock/<int:order_id>/invoice')
@login_required
@admin_required
def admin_generate_restock_invoice(order_id):
    restock_order = models.RestockOrder.query.get_or_404(order_id)

    # Create PDF invoice
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 50, "INVOICE RESTOCK ORDER")

    # Store info
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 80, "DARI: Hurtrock Music Store")
    p.drawString(50, height - 95, "Jl. Musik Raya No. 123, Jakarta")
    p.drawString(50, height - 110, "Telp: 0821-1555-8035")

    # Invoice info
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 140, f"Invoice #: RESTOCK-{restock_order.id:05d}")
    p.drawString(50, height - 160, f"Tanggal: {restock_order.created_at.strftime('%d/%m/%Y')}")
    p.drawString(50, height - 180, f"Status: {restock_order.status.upper()}")

    # Supplier info
    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, height - 140, "KEPADA:")
    p.setFont("Helvetica", 10)
    p.drawString(350, height - 160, f"{restock_order.supplier.name}")
    if restock_order.supplier.contact_person:
        p.drawString(350, height - 175, f"PIC: {restock_order.supplier.contact_person}")
    if restock_order.supplier.phone:
        p.drawString(350, height - 190, f"Telp: {restock_order.supplier.phone}")

    # Table header
    y_pos = height - 230
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y_pos, "Produk")
    p.drawString(300, y_pos, "Qty")
    p.drawString(350, y_pos, "Harga Satuan")
    p.drawString(450, y_pos, "Total")

    # Draw line
    p.line(50, y_pos - 5, width - 50, y_pos - 5)

    # Items
    y_pos -= 25
    p.setFont("Helvetica", 9)
    total_amount = 0

    for item in restock_order.items:
        p.drawString(50, y_pos, item.product.name[:30])
        p.drawString(300, y_pos, str(item.quantity_ordered))
        p.drawString(350, y_pos, f"Rp {item.unit_cost:,.0f}".replace(',', '.'))
        p.drawString(450, y_pos, f"Rp {item.subtotal:,.0f}".replace(',', '.'))
        y_pos -= 15
        total_amount += item.subtotal

    # Total
    p.line(50, y_pos - 5, width - 50, y_pos - 5)
    y_pos -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, y_pos, "TOTAL:")
    p.drawString(450, y_pos, f"Rp {total_amount:,.0f}".replace(',', '.'))

    # Notes
    if restock_order.notes:
        y_pos -= 40
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y_pos, "Catatan:")
        y_pos -= 15
        p.setFont("Helvetica", 9)
        p.drawString(50, y_pos, restock_order.notes)

    p.showPage()
    p.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'invoice_restock_{restock_order.id:05d}.pdf',
        mimetype='application/pdf'
    )

# Socket.IO Events
@socketio.on('connect')
def on_connect():
    print("🔌 ===== SOCKET.IO CONNECTION =====")
    if current_user.is_authenticated:
        print(f"✅ Authenticated User Connected:")
        print(f"   Name: {current_user.name}")
        print(f"   ID: {current_user.id}")
        print(f"   Email: {current_user.email}")
        print(f"   Role: {current_user.role}")
        print(f"   Is Admin: {current_user.is_admin}")
        print(f"   Is Staff: {current_user.is_staff}")
        print(f"   Session ID: {request.sid}")
    else:
        print("⚠️ Anonymous user connected via Socket.IO")
        print(f"   Session ID: {request.sid}")
    print("=" * 35)

@socketio.on('join')
def on_join(data):
    print("🚪 ===== SOCKET.IO JOIN EVENT =====")
    print(f"📦 Join Data: {data}")
    
    if current_user.is_authenticated:
        if current_user.is_admin or current_user.is_staff:
            join_room('admin_room')
            print(f"👑 Admin/Staff joined admin_room:")
            print(f"   User: {current_user.name}")
            print(f"   Role: {current_user.role}")
            print(f"   Room: admin_room")
            print(f"   Session ID: {request.sid}")
        else:
            user_room = f'user_{current_user.id}'
            join_room(user_room)
            print(f"👤 User joined user room:")
            print(f"   User: {current_user.name}")
            print(f"   User ID: {current_user.id}")
            print(f"   Room: {user_room}")
            print(f"   Session ID: {request.sid}")
    else:
        print("❌ Unauthenticated user tried to join")
    print("=" * 35)

@socketio.on('disconnect')
def on_disconnect():
    print("🚪 ===== SOCKET.IO DISCONNECT EVENT =====")
    
    if current_user.is_authenticated:
        if current_user.is_admin or current_user.is_staff:
            leave_room('admin_room')
            print(f"👑 Admin/Staff left admin_room:")
            print(f"   User: {current_user.name}")
            print(f"   Role: {current_user.role}")
            print(f"   Room: admin_room")
            print(f"   Session ID: {request.sid}")
        else:
            user_room = f'user_{current_user.id}'
            leave_room(user_room)
            print(f"👤 User left user room:")
            print(f"   User: {current_user.name}")
            print(f"   User ID: {current_user.id}")
            print(f"   Room: {user_room}")
            print(f"   Session ID: {request.sid}")
    else:
        print("⚠️ Anonymous user disconnected")
        print(f"   Session ID: {request.sid}")
    print("=" * 35)

@socketio.on_error()
def error_handler(e):
    print("❌ ===== SOCKET.IO ERROR =====")
    print(f"❌ Error Type: {type(e).__name__}")
    print(f"❌ Error Message: {str(e)}")
    print(f"❌ Session ID: {request.sid}")
    if current_user.is_authenticated:
        print(f"❌ User: {current_user.name} (ID: {current_user.id})")
    
    import traceback
    traceback.print_exc()
    print("=" * 30)

@socketio.on('new_message')
def handle_message_event(data):
    print("📨 ===== SOCKET.IO MESSAGE EVENT =====")
    print(f"📦 Message Data: {data}")
    print(f"📦 Session ID: {request.sid}")
    if current_user.is_authenticated:
        print(f"📦 From User: {current_user.name} (ID: {current_user.id})")
    print("=" * 38)

if __name__ == '__main__':
    # For development environment in Replit
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True, use_reloader=False, log_output=True)