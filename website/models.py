from . import db                                           
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func



class TimestampMixin(object):
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())



class Customer(db.Model, UserMixin, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(100))  # Optional field

    # Relationships
    cart_items = db.relationship('Cart', backref='customer', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='customer', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)
    reviews = db.relationship('Review', backref='customer', lazy=True)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)

    def __str__(self):
        return f'<Customer {self.username}>'
    

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)

    product = db.relationship('Product', back_populates='images')


class Product(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    category = db.Column(db.String(150), nullable=False)
    product_picture = db.Column(db.String(255))
    quantity = db.Column(db.Integer, nullable=False)



    # Relationships
    images = db.relationship('ProductImage', back_populates='product', cascade="all, delete-orphan")
    carts = db.relationship('Cart', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', back_populates='product', lazy=True)
    wishlists = db.relationship('Wishlist', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)

    def __str__(self):
        return f'<Product {self.product_name}>'
    
class Order(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120))  # 🆕
    phone = db.Column(db.String(20))   # 🆕
    shipping_address = db.Column(db.String(500), nullable=False)
    notes = db.Column(db.Text)         # 🆕

    tracking_url = db.Column(db.String(500))  # Optional
    status = db.Column(db.String(100), default='pending', nullable=False)
    payment_id = db.Column(db.String(1000))  # Optional until payment added
    total = db.Column(db.Float, nullable=False)

    # Relationships
    items = db.relationship('OrderItem', back_populates='order', lazy=True)

    def __str__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', name='fk_orderitem_order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_each = db.Column(db.Float, nullable=False)
    size = db.Column(db.String(5), nullable=True)

    # Fixed relationships
    product = db.relationship("Product", back_populates="order_items")
    order = db.relationship("Order", back_populates="items")

    def __str__(self):
        return f'<OrderItem Order#{self.order_id} - Product#{self.product_id}>'


    

class Review(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.String(1000), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __str__(self):
        return f'<Review {self.id}>'
    


class Cart(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    size = db.Column(db.String(5), nullable=True)
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __str__(self):
        return f'<Cart {self.id}>'
    

class Wishlist(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    def __str__(self):
        return f'<Wishlist {self.id}>'