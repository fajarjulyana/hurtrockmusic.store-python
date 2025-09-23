from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import String, Text, Numeric, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

# Import db instance from database module
from database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(255), nullable=False)
    name = db.Column(String(100), nullable=False)
    phone = db.Column(String(20))
    address = db.Column(Text)
    active = db.Column(Boolean, default=True)
    role = db.Column(String(20), default='buyer')  # admin, staff, buyer
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items = relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = relationship('Order', backref='user', lazy=True)
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_staff(self):
        return self.role == 'staff'
    
    @property
    def is_buyer(self):
        return self.role == 'buyer'
    
    def __repr__(self):
        return f'<User {self.email}>'

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    description = db.Column(Text)
    image_url = db.Column(String(255))
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(200), nullable=False)
    description = db.Column(Text)
    price = db.Column(Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(Integer, default=0)
    image_url = db.Column(String(255))
    brand = db.Column(String(100))
    model = db.Column(String(100))
    is_active = db.Column(Boolean, default=True)
    is_featured = db.Column(Boolean, default=False)
    category_id = db.Column(Integer, ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Informasi supplier dan dimensi untuk shipping
    supplier_id = db.Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    weight = db.Column(Numeric(8, 2), default=0)  # dalam gram
    length = db.Column(Numeric(8, 2), default=0)  # dalam cm
    width = db.Column(Numeric(8, 2), default=0)   # dalam cm
    height = db.Column(Numeric(8, 2), default=0)  # dalam cm
    
    # Relationships
    cart_items = relationship('CartItem', backref='product', lazy=True)
    order_items = relationship('OrderItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    @property
    def volume_cm3(self):
        """Menghitung volume produk dalam cm3"""
        return float(self.length or 0) * float(self.width or 0) * float(self.height or 0)
    
    @property
    def formatted_price(self):
        return f"Rp {self.price:,.0f}".replace(',', '.')
    
    def to_dict(self):
        """Convert product to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'image_url': self.image_url or '/static/images/placeholder.jpg',
            'brand': self.brand or '',
            'description': self.description or '',
            'category': self.category.name if self.category else '',
            'is_active': self.is_active
        }

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = db.Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = db.Column(Integer, nullable=False, default=1)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CartItem User:{self.user_id} Product:{self.product_id}>'
    
    @property
    def subtotal(self):
        return self.quantity * self.product.price

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(String(50), default='pending')  # pending, paid, shipped, delivered, cancelled
    tracking_number = db.Column(String(100))  # For package tracking
    courier_service = db.Column(String(50))  # JNE, J&T, SiCepat, etc.
    shipping_service_id = db.Column(Integer, ForeignKey('shipping_services.id'), nullable=True)
    shipping_cost = db.Column(Numeric(10, 2), default=0)
    shipping_address = db.Column(Text)
    payment_method = db.Column(String(50))
    estimated_delivery_days = db.Column(Integer, default=0)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id}>'
    
    @property
    def formatted_total(self):
        return f"Rp {self.total_amount:,.0f}".replace(',', '.')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(Integer, primary_key=True)
    order_id = db.Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = db.Column(Integer, nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)  # Price at time of order
    
    def __repr__(self):
        return f'<OrderItem Order:{self.order_id} Product:{self.product_id}>'
    
    @property
    def subtotal(self):
        return self.quantity * self.price
    
    @property
    def formatted_subtotal(self):
        return f"Rp {self.subtotal:,.0f}".replace(',', '.')


class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(200), nullable=False)
    contact_person = db.Column(String(100))
    email = db.Column(String(120))
    phone = db.Column(String(20))
    address = db.Column(Text)
    company = db.Column(String(200))
    notes = db.Column(Text)
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship('Product', backref='supplier', lazy=True)
    
    def __repr__(self):
        return f'<Supplier {self.name}>'

class ShippingService(db.Model):
    __tablename__ = 'shipping_services'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)  # JNE, JNT, SiCepat, etc
    code = db.Column(String(20), unique=True, nullable=False)  # jne, jnt, sicepat
    base_price = db.Column(Numeric(10, 2), nullable=False)  # Harga dasar per kg
    price_per_kg = db.Column(Numeric(10, 2), nullable=False)  # Harga tambahan per kg
    price_per_km = db.Column(Numeric(8, 4), default=0)  # Harga per km jarak
    volume_factor = db.Column(Numeric(8, 4), default=5000)  # Faktor volume divider (cm3 to kg)
    min_days = db.Column(Integer, default=1)  # Estimasi minimum hari
    max_days = db.Column(Integer, default=3)  # Estimasi maksimum hari
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = relationship('Order', backref='shipping_service', lazy=True)
    
    def __repr__(self):
        return f'<ShippingService {self.name}>'
    
    def calculate_shipping_cost(self, weight_gram, volume_cm3, distance_km=50):
        """
        Menghitung biaya shipping berdasarkan berat, volume, dan jarak
        """
        # Convert gram to kg
        weight_kg = float(weight_gram) / 1000
        
        # Calculate volumetric weight
        volumetric_weight_kg = float(volume_cm3) / float(self.volume_factor)
        
        # Use the higher weight (actual or volumetric)
        billable_weight = max(weight_kg, volumetric_weight_kg)
        
        # Calculate cost
        base_cost = float(self.base_price)
        weight_cost = billable_weight * float(self.price_per_kg)
        distance_cost = float(distance_km) * float(self.price_per_km)
        
        total_cost = base_cost + weight_cost + distance_cost
        
        return round(total_cost, 2)

class RestockOrder(db.Model):
    __tablename__ = 'restock_orders'
    
    id = db.Column(Integer, primary_key=True)
    supplier_id = db.Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    status = db.Column(String(50), default='pending')  # pending, ordered, received, cancelled
    total_amount = db.Column(Numeric(12, 2), default=0)
    notes = db.Column(Text)
    order_date = db.Column(DateTime, default=datetime.utcnow)
    expected_date = db.Column(DateTime)
    received_date = db.Column(DateTime)
    created_by = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    supplier = relationship('Supplier', backref='restock_orders', lazy=True)
    created_by_user = relationship('User', backref='created_restock_orders', lazy=True)
    items = relationship('RestockOrderItem', backref='restock_order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<RestockOrder {self.id}>'
    
    @property
    def formatted_total(self):
        return f"Rp {self.total_amount:,.0f}".replace(',', '.')

class RestockOrderItem(db.Model):
    __tablename__ = 'restock_order_items'
    
    id = db.Column(Integer, primary_key=True)
    restock_order_id = db.Column(Integer, ForeignKey('restock_orders.id'), nullable=False)
    product_id = db.Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity_ordered = db.Column(Integer, nullable=False)
    quantity_received = db.Column(Integer, default=0)
    unit_cost = db.Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    product = relationship('Product', backref='restock_items', lazy=True)
    
    def __repr__(self):
        return f'<RestockOrderItem {self.id}>'
    
    @property
    def subtotal(self):
        return self.quantity_ordered * self.unit_cost
    
    @property
    def formatted_subtotal(self):
        return f"Rp {self.subtotal:,.0f}".replace(',', '.')

class PaymentConfiguration(db.Model):
    __tablename__ = 'payment_configurations'
    
    id = db.Column(Integer, primary_key=True)
    provider = db.Column(String(50), nullable=False)  # 'stripe', 'midtrans'
    is_active = db.Column(Boolean, default=False)
    is_sandbox = db.Column(Boolean, default=True)
    
    # Midtrans specific
    midtrans_client_key = db.Column(String(255))
    midtrans_server_key = db.Column(String(255))
    midtrans_merchant_id = db.Column(String(100))
    
    # Stripe specific  
    stripe_publishable_key = db.Column(String(255))
    stripe_secret_key = db.Column(String(255))
    
    # Callback URLs
    callback_finish_url = db.Column(String(255))
    callback_unfinish_url = db.Column(String(255))
    callback_error_url = db.Column(String(255))
    notification_url = db.Column(String(255))
    
    # Additional callback URLs untuk Midtrans
    recurring_notification_url = db.Column(String(255))
    account_linking_url = db.Column(String(255))
    
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PaymentConfiguration {self.provider}>'

class MidtransTransaction(db.Model):
    __tablename__ = 'midtrans_transactions'
    
    id = db.Column(Integer, primary_key=True)
    order_id = db.Column(Integer, ForeignKey('orders.id'), nullable=False)
    transaction_id = db.Column(String(100), unique=True, nullable=False)
    gross_amount = db.Column(Numeric(10, 2), nullable=False)
    payment_type = db.Column(String(50))
    transaction_status = db.Column(String(50))
    fraud_status = db.Column(String(50))
    settlement_time = db.Column(DateTime)
    
    # Midtrans response data
    snap_token = db.Column(String(255))
    snap_redirect_url = db.Column(String(500))
    midtrans_response = db.Column(Text)  # JSON response from Midtrans
    
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = relationship('Order', backref='midtrans_transactions', lazy=True)
    
    def __repr__(self):
        return f'<MidtransTransaction {self.transaction_id}>'

class StoreProfile(db.Model):
    __tablename__ = 'store_profiles'
    
    id = db.Column(Integer, primary_key=True)
    store_name = db.Column(String(200), nullable=False, default='Hurtrock Music Store')
    store_tagline = db.Column(String(255), default='Toko Alat Musik Terpercaya')
    store_address = db.Column(Text, nullable=False)
    store_city = db.Column(String(100), nullable=False)
    store_postal_code = db.Column(String(10))
    store_phone = db.Column(String(20), nullable=False)
    store_email = db.Column(String(120), nullable=False)
    store_website = db.Column(String(255))
    
    # Branch information
    branch_name = db.Column(String(200))
    branch_code = db.Column(String(10))
    branch_manager = db.Column(String(100))
    
    # Business information
    business_license = db.Column(String(100))
    tax_number = db.Column(String(50))
    
    # Logo and branding
    logo_url = db.Column(String(255))
    primary_color = db.Column(String(7), default='#FF6B35')  # Hex color
    secondary_color = db.Column(String(7), default='#FF8C42')  # Hex color
    
    # Operating hours
    operating_hours = db.Column(Text)  # JSON format for flexible hours
    
    # Social media
    facebook_url = db.Column(String(255))
    instagram_url = db.Column(String(255))
    whatsapp_number = db.Column(String(20))
    
    # Settings
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StoreProfile {self.store_name}>'
    
    @classmethod
    def get_active_profile(cls):
        """Get the active store profile"""
        return cls.query.filter_by(is_active=True).first()
    
    @property
    def formatted_address(self):
        """Get formatted address for labels"""
        address_parts = [self.store_address]
        if self.store_city:
            address_parts.append(self.store_city)
        if self.store_postal_code:
            address_parts.append(self.store_postal_code)
        return ', '.join(address_parts)
    
    @property
    def full_contact_info(self):
        """Get full contact information"""
        contact_parts = []
        if self.store_phone:
            contact_parts.append(f"Telp: {self.store_phone}")
        if self.store_email:
            contact_parts.append(f"Email: {self.store_email}")
        if self.whatsapp_number:
            contact_parts.append(f"WA: {self.whatsapp_number}")
        return ' | '.join(contact_parts)

# Chat System Models
class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), unique=True, nullable=False)
    buyer_id = db.Column(Integer, ForeignKey('users.id'), nullable=True)
    buyer_name = db.Column(String(100))
    buyer_email = db.Column(String(120))
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = relationship('ChatMessage', backref='room', lazy=True, cascade='all, delete-orphan')
    sessions = relationship('ChatSession', backref='room', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ChatRoom {self.name}>'

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(Integer, primary_key=True)
    room_id = db.Column(Integer, ForeignKey('chat_rooms.id'), nullable=False)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    user_name = db.Column(String(100), nullable=False)
    user_email = db.Column(String(120), nullable=False)
    message = db.Column(Text, nullable=False)
    sender_type = db.Column(String(10), default='buyer')  # buyer, admin, staff
    product_id = db.Column(Integer, ForeignKey('products.id'), nullable=True)
    is_read = db.Column(Boolean, default=False)
    is_deleted = db.Column(Boolean, default=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sender = relationship('User', backref='chat_messages', lazy=True)
    tagged_product = relationship('Product', backref='chat_tags', lazy=True)
    
    def __repr__(self):
        return f'<ChatMessage {self.user_name}: {self.message[:50]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'message': self.message,
            'sender_type': self.sender_type,
            'product_id': self.product_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'timestamp': self.created_at.strftime('%H:%M'),
            'product_info': self.tagged_product.to_dict() if self.tagged_product else None
        }

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(Integer, primary_key=True)
    room_id = db.Column(Integer, ForeignKey('chat_rooms.id'), nullable=False)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    user_name = db.Column(String(100), nullable=False)
    user_email = db.Column(String(120), nullable=False)
    user_role = db.Column(String(20), default='buyer')
    started_at = db.Column(DateTime, default=datetime.utcnow)
    ended_at = db.Column(DateTime, nullable=True)
    is_active = db.Column(Boolean, default=True)
    
    # Relationships
    user = relationship('User', backref='chat_sessions', lazy=True)
    
    def __repr__(self):
        return f'<ChatSession {self.user_name} in {self.room.name}>'