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
from datetime import datetime
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

# Production security configuration
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JS access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
socketio = SocketIO(app, cors_allowed_origins="*")

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
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

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
    query = request.args.get('q', '')
    if query:
        products = models.Product.query.filter(
            models.Product.name.contains(query),
            models.Product.is_active == True
        ).all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'image_url': p.image_url or '/static/images/placeholder.jpg'
        } for p in products])
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
    
    total = sum(item.quantity * item.product.price for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    cart_items = models.CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        return jsonify({'error': 'Keranjang kosong'}), 400
    
    # Build line items for Stripe
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
    
    try:
        YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN') if os.environ.get('REPLIT_DEPLOYMENT') == '' else os.environ.get('REPLIT_DOMAINS').split(',')[0]
        
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=f'https://{YOUR_DOMAIN}/payment-success',
            cancel_url=f'https://{YOUR_DOMAIN}/cart',
            customer_email=current_user.email,
        )
        
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('cart'))

@app.route('/payment-success')
@login_required
def payment_success():
    # Create order from cart items
    cart_items = models.CartItem.query.filter_by(user_id=current_user.id).all()
    
    if cart_items:
        total_amount = sum(item.quantity * item.product.price for item in cart_items)
        
        order = models.Order(
            user_id=current_user.id,
            total_amount=total_amount,
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
    
    return render_template('payment_success.html')

@app.route('/orders')
@login_required
def orders():
    user_orders = models.Order.query.filter_by(user_id=current_user.id).order_by(models.Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

@app.route('/store-info')
def store_info():
    return render_template('store_info.html')

# Chat Routes
@app.route('/chat')
@login_required
def chat():
    # Get or create chat room for user
    chat_room = models.ChatRoom.query.filter_by(user_id=current_user.id).first()
    if not chat_room:
        chat_room = models.ChatRoom(user_id=current_user.id)
        db.session.add(chat_room)
        db.session.commit()
    
    messages = models.ChatMessage.query.filter_by(chat_room_id=chat_room.id).order_by(models.ChatMessage.created_at).all()
    
    # Mark user messages as read
    models.ChatMessage.query.filter_by(chat_room_id=chat_room.id, sender_type='admin', is_read=False).update({'is_read': True})
    db.session.commit()
    
    return render_template('chat.html', messages=messages, chat_room=chat_room)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    message_text = request.form.get('message')
    if not message_text:
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
        message=message_text
    )
    db.session.add(message)
    
    # Update last message time
    chat_room.last_message_at = datetime.utcnow()
    db.session.commit()
    
    # Emit to admin
    socketio.emit('new_message', {
        'room_id': chat_room.id,
        'user_name': current_user.name,
        'message': message_text,
        'timestamp': message.created_at.strftime('%H:%M')
    }, room='admin_room')
    
    return jsonify({'success': True})

# API endpoints for floating chat
@app.route('/api/chat/messages')
@login_required
def api_chat_messages():
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
    
    return jsonify({'success': True, 'messages': message_list})

@app.route('/api/chat/send', methods=['POST'])
@login_required
def api_chat_send():
    data = request.get_json()
    message_text = data.get('message')
    product_id = data.get('product_id')
    
    if not message_text:
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
        message=message_text,
        product_id=product_id
    )
    db.session.add(message)
    
    # Update last message time
    chat_room.last_message_at = datetime.utcnow()
    db.session.commit()
    
    # Emit to admin with product info
    emit_data = {
        'room_id': chat_room.id,
        'user_name': current_user.name,
        'message': message_text,
        'sender_type': 'user',
        'timestamp': message.created_at.strftime('%H:%M'),
        'product_id': product_id
    }
    
    socketio.emit('new_message', emit_data, room='admin_room')
    
    return jsonify({'success': True})

@app.route('/api/chat/clear', methods=['POST'])
@login_required
def api_chat_clear():
    chat_room = models.ChatRoom.query.filter_by(user_id=current_user.id).first()
    if chat_room:
        # Delete all messages in the chat room
        models.ChatMessage.query.filter_by(chat_room_id=chat_room.id).delete()
        db.session.commit()
    
    return jsonify({'success': True})

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
    
    return render_template('admin/dashboard.html', 
                         total_products=total_products,
                         total_orders=total_orders,
                         total_users=total_users,
                         pending_chats=pending_chats,
                         recent_orders=recent_orders)

@app.route('/admin/products')
@login_required
@admin_required
def admin_products():
    products = models.Product.query.all()
    categories = models.Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock_quantity = int(request.form['stock_quantity'])
        brand = request.form['brand']
        model = request.form['model']
        category_id = int(request.form['category_id'])
        is_featured = 'is_featured' in request.form
        
        # Handle multiple image uploads
        uploaded_files = request.files.getlist('images')
        image_urls = []
        
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                file.save(filepath)
                compress_image(filepath)
                image_urls.append(f"/static/images/{filename}")
        
        product = models.Product(
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            brand=brand,
            model=model,
            category_id=category_id,
            is_featured=is_featured,
            image_url=image_urls[0] if image_urls else None
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Produk berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_products'))
    
    categories = models.Category.query.all()
    return render_template('admin/add_product.html', categories=categories)

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
    return render_template('admin/chats.html', chat_rooms=chat_rooms)

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
@staff_required
def admin_send_reply():
    room_id = int(request.form['room_id'])
    message_text = request.form['message']
    
    if not message_text:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    chat_room = models.ChatRoom.query.get_or_404(room_id)
    
    message = models.ChatMessage(
        chat_room_id=room_id,
        sender_type='admin',
        message=message_text
    )
    db.session.add(message)
    
    chat_room.last_message_at = datetime.utcnow()
    db.session.commit()
    
    # Emit to user
    socketio.emit('new_message', {
        'message': message_text,
        'sender_type': 'admin',
        'timestamp': message.created_at.strftime('%H:%M')
    }, room=f'user_{chat_room.user_id}')
    
    return jsonify({'success': True})

@app.route('/admin/chat/clear', methods=['POST'])
@login_required
@admin_required
def admin_clear_chat():
    data = request.get_json()
    room_id = data.get('room_id')
    
    if not room_id:
        return jsonify({'error': 'Room ID required'}), 400
    
    chat_room = models.ChatRoom.query.get_or_404(room_id)
    
    # Delete all messages in the chat room
    models.ChatMessage.query.filter_by(chat_room_id=room_id).delete()
    db.session.commit()
    
    return jsonify({'success': True})

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
    
    # Generate tracking number if not exists
    if not order.tracking_number:
        order.tracking_number = generate_tracking_number()
        db.session.commit()
    
    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "HURTROCK MUSIC STORE")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, "Label Pengiriman Pesanan")
    
    # Order Info
    y_pos = height - 120
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_pos, f"Order #: {order.id}")
    p.drawString(300, y_pos, f"Tracking #: {order.tracking_number}")
    
    y_pos -= 30
    p.setFont("Helvetica", 10)
    p.drawString(50, y_pos, f"Tanggal: {order.created_at.strftime('%d/%m/%Y')}")
    p.drawString(300, y_pos, f"Status: {order.status.upper()}")
    
    # Customer Info
    y_pos -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_pos, "PENERIMA:")
    
    y_pos -= 20
    p.setFont("Helvetica", 10)
    p.drawString(50, y_pos, f"Nama: {order.user.name}")
    
    y_pos -= 15
    p.drawString(50, y_pos, f"Email: {order.user.email}")
    
    if order.user.phone:
        y_pos -= 15
        p.drawString(50, y_pos, f"Telepon: {order.user.phone}")
    
    if order.user.address:
        y_pos -= 15
        p.drawString(50, y_pos, "Alamat:")
        y_pos -= 15
        # Split long address
        address_lines = order.user.address.split('\n')
        for line in address_lines:
            if len(line) > 60:
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line + word) < 60:
                        current_line += word + " "
                    else:
                        p.drawString(50, y_pos, current_line.strip())
                        y_pos -= 15
                        current_line = word + " "
                if current_line.strip():
                    p.drawString(50, y_pos, current_line.strip())
                    y_pos -= 15
            else:
                p.drawString(50, y_pos, line)
                y_pos -= 15
    
    # Items
    y_pos -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_pos, "BARANG:")
    
    y_pos -= 20
    p.setFont("Helvetica", 10)
    for item in order.order_items:
        p.drawString(50, y_pos, f"• {item.product.name} x{item.quantity}")
        y_pos -= 15
    
    # Total
    y_pos -= 10
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_pos, f"TOTAL: {order.formatted_total}")
    
    # Footer
    p.setFont("Helvetica", 8)
    p.drawString(50, 50, "Hurtrock Music Store - Toko Alat Musik Terpercaya")
    p.drawString(50, 40, "Hubungi: 0821-1555-8035")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'label_order_{order.id}.pdf',
        mimetype='application/pdf'
    )

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = models.User.query.all()
    return render_template('admin/users.html', users=users)

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

# Socket.IO Events
@socketio.on('join')
def on_join(data):
    if current_user.is_authenticated:
        if current_user.is_admin or current_user.is_staff:
            join_room('admin_room')
        else:
            join_room(f'user_{current_user.id}')

@socketio.on('disconnect')
def on_disconnect():
    if current_user.is_authenticated:
        if current_user.is_admin or current_user.is_staff:
            leave_room('admin_room')
        else:
            leave_room(f'user_{current_user.id}')

if __name__ == '__main__':
    # For development environment in Replit
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)