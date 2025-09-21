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
    chat_rooms = relationship('ChatRoom', backref='user', lazy=True)
    
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
    
    # Relationships
    cart_items = relationship('CartItem', backref='product', lazy=True)
    order_items = relationship('OrderItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    @property
    def formatted_price(self):
        return f"Rp {self.price:,.0f}".replace(',', '.')

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
    courier_service = db.Column(String(50))  # JNE, JNT, SiCepat, etc
    shipping_address = db.Column(Text)
    payment_method = db.Column(String(50))
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

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    last_message_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = relationship('ChatMessage', backref='chat_room', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ChatRoom {self.id} User:{self.user_id}>'

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(Integer, primary_key=True)
    chat_room_id = db.Column(Integer, ForeignKey('chat_rooms.id'), nullable=False)
    sender_type = db.Column(String(20), nullable=False)  # 'user' or 'admin'
    message = db.Column(Text, nullable=False)
    product_id = db.Column(Integer, ForeignKey('products.id'), nullable=True)  # For product tagging
    is_read = db.Column(Boolean, default=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationship to product
    tagged_product = relationship('Product', backref='chat_messages', lazy=True)
    
    def __repr__(self):
        return f'<ChatMessage {self.id}>'