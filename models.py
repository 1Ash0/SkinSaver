from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json
from flask_login import UserMixin

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model for account management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)  # Make nullable for OAuth users
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade="all, delete-orphan")
    has_password = db.Column(db.Boolean, default=True)  # Flag to identify OAuth users
    profile_picture = db.Column(db.String(255), nullable=True)  # For OAuth profile pictures
    last_login = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, username, email, password=None, has_password=True):
        self.username = username
        self.email = email
        self.has_password = has_password
        
        if has_password and password:
            self.set_password(password)
        elif not has_password:
            # For OAuth users without a password
            self.password_hash = None
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.has_password = True
        
    def check_password(self, password):
        if not self.has_password or not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'profile_picture': self.profile_picture,
            'has_password': self.has_password,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
class CartItem(db.Model):
    """Model for cart items"""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    source = db.Column(db.String(50))
    image = db.Column(db.String(255))
    added_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'price': self.price,
            'quantity': self.quantity,
            'source': self.source,
            'image': self.image,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }