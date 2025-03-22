import os
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_cors import CORS
from scraper import get_amazon_products, get_flipkart_products, get_nykaa_products
from scheduler import initialize_scheduler
from models import db, User, CartItem
from mock_data import get_mock_products, get_product_by_id as get_mock_product_by_id
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created")

# Custom login required decorator (legacy, use Flask-Login instead)
def custom_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# In-memory data store for products
products_data = []

def load_initial_data():
    """Load initial data from scraper if available, or use mock data"""
    global products_data
    try:
        # Try to get some initial data from scrapers
        amazon_products = get_amazon_products("moisturizer")
        flipkart_products = get_flipkart_products("moisturizer")
        nykaa_products = get_nykaa_products("moisturizer")
        
        # Combine all products
        products_data = amazon_products + flipkart_products + nykaa_products
        
        # If we don't have any real products, use mock data
        if len(products_data) == 0:
            products_data = get_mock_products()
            logger.info(f"Using mock data with {len(products_data)} products")
        else:
            logger.info(f"Loaded {len(products_data)} initial products from scraping")
    except Exception as e:
        logger.error(f"Error loading initial data: {e}")
        # Use mock data as fallback
        products_data = get_mock_products()
        logger.info(f"Using mock data with {len(products_data)} products due to error")

# Function to get product by ID
def get_product_by_id(product_id):
    for product in products_data:
        if product.get('id') == product_id:
            return product
    return None

# Function to search products
def search_products(query, category=None):
    if not query:
        return products_data
    
    results = []
    query = query.lower()
    for product in products_data:
        if (query in product.get('name', '').lower() or 
            query in product.get('description', '').lower()):
            if category and category != 'all' and product.get('category') != category:
                continue
            results.append(product)
    return results

# Function to get cheapest price for a product
def get_cheapest_price(product_name):
    matches = []
    product_name = product_name.lower()
    
    for product in products_data:
        if product_name in product.get('name', '').lower():
            matches.append(product)
    
    if not matches:
        return None
    
    # Find the product with the lowest price
    def extract_price(product):
        price_str = product.get('price', '0')
        if isinstance(price_str, float):
            return price_str
        return float(price_str.replace('₹', '').replace(',', ''))
        
    cheapest = min(matches, key=extract_price)
    return cheapest

# Routes
@app.route('/')
def index():
    """Home page route"""
    featured_products = products_data[:8] if products_data else []
    return render_template('index.html', featured_products=featured_products)

@app.route('/search')
def search():
    """Search results page"""
    query = request.args.get('query', '')
    category = request.args.get('category', 'all')
    
    results = search_products(query, category)
    return render_template('search.html', products=results, query=query, category=category)

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = get_product_by_id(product_id)
    if not product:
        return redirect(url_for('index'))
    
    # Find similar products for comparison
    similar_products = []
    product_name_parts = product['name'].lower().split()
    
    for p in products_data:
        if p['id'] != product_id:
            # Check if product names share words
            p_name_parts = p['name'].lower().split()
            if any(part in p_name_parts for part in product_name_parts):
                similar_products.append(p)
    
    # Limit to 4 similar products
    similar_products = similar_products[:4]
    
    return render_template('product.html', product=product, similar_products=similar_products)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

# Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    # If already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        error = None
        if not username or not email or not password:
            error = 'All fields are required'
        elif not '@' in email:
            error = 'Please enter a valid email address'
        elif password != confirm_password:
            error = 'Passwords do not match'
        
        # Check for existing username/email with retry for DB connection issues
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries and error is None:
            try:
                if User.query.filter_by(username=username).first():
                    error = 'Username is already taken'
                elif User.query.filter_by(email=email).first():
                    error = 'Email is already registered'
                break  # If we get here without exception, break the loop
            except Exception as e:
                logger.error(f"Database query error (attempt {retry_count+1}): {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    error = 'Service temporarily unavailable. Please try again later.'
                else:
                    # Wait a moment before retrying
                    import time
                    time.sleep(0.5)
            
        if error is None:
            try:
                # Create new user
                user = User(username=username, email=email, password=password, has_password=True)
                db.session.add(user)
                db.session.commit()
                
                # Log in the user with Flask-Login
                login_user(user)
                
                # Set session for backward compatibility
                session['user_id'] = user.id
                session['username'] = user.username
                
                flash('Registration successful! Welcome to SkinSaver.', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                logger.error(f"Error during user registration: {e}")
                db.session.rollback()
                flash('Service temporarily unavailable. Please try again later.', 'danger')
            
        flash(error, 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    # If already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        # Validate form data
        error = None
        user = None
        
        if not email or not password:
            error = 'Email and password are required'
        else:
            # Retry pattern for database operations
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    user = User.query.filter_by(email=email).first()
                    if not user or not user.has_password or not user.check_password(password):
                        error = 'Invalid email or password'
                    break  # Break the loop if successful
                except Exception as e:
                    logger.error(f"Database query error during login (attempt {retry_count+1}): {e}")
                    retry_count += 1
                    if retry_count >= max_retries:
                        error = 'Service temporarily unavailable. Please try again later.'
                    else:
                        # Wait a moment before retrying
                        import time
                        time.sleep(0.5)
                
        if error is None and user is not None:
            try:
                # Use Flask-Login to log in the user
                login_user(user, remember=remember)
                
                # Update last login time
                user.update_last_login()
                
                # Set session variables for backward compatibility
                session['user_id'] = user.id
                session['username'] = user.username
                
                # Get next page from request args
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):  # Security check
                    return redirect(next_page)
                    
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                logger.error(f"Error during login: {e}")
                flash('Service temporarily unavailable. Please try again later.', 'danger')
            
        flash(error, 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout route"""
    # Clear session
    session.clear()
    
    # Use Flask-Login logout
    logout_user()
    
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Cart Routes
@app.route('/cart')
@login_required  # Use Flask-Login's login_required
def view_cart():
    """View user's cart"""
    # Use current_user from Flask-Login
    user_id = current_user.id
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    total_price = 0
    cart_products = []
    
    for item in cart_items:
        # Extract price safely
        price_str = item.price
        if isinstance(price_str, float):
            price_value = price_str
        else:
            price_value = float(price_str.replace('₹', '').replace(',', ''))
            
        item_total = price_value * item.quantity
        
        product_info = {
            'id': item.id,
            'product_id': item.product_id,
            'name': item.product_name,
            'price': item.price,
            'quantity': item.quantity,
            'source': item.source,
            'image': item.image,
            'total': item_total
        }
        cart_products.append(product_info)
        total_price += item_total
    
    return render_template('cart.html', cart_items=cart_products, total_price=f"₹{total_price:,.2f}")

@app.route('/cart/add/<product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add product to cart"""
    # Use current_user from Flask-Login
    user_id = current_user.id
    product = get_product_by_id(product_id)
    
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('index'))
    
    # Database operations with retry
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Check if product already in cart
            existing_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
            
            if existing_item:
                # Update quantity
                existing_item.quantity += 1
                db.session.commit()
                flash(f'Updated {product["name"]} quantity in your cart.', 'success')
            else:
                # Add new item to cart
                cart_item = CartItem(
                    user_id=user_id,
                    product_id=product_id,
                    product_name=product['name'],
                    price=product['price'],
                    source=product['source'],
                    image=product['image']
                )
                db.session.add(cart_item)
                db.session.commit()
                flash(f'Added {product["name"]} to your cart.', 'success')
            
            # If we get here, operation was successful
            break
            
        except Exception as e:
            logger.error(f"Database error during add_to_cart (attempt {retry_count+1}): {e}")
            db.session.rollback()
            retry_count += 1
            
            if retry_count >= max_retries:
                flash('Service temporarily unavailable. Please try again later.', 'danger')
            else:
                # Wait before retrying
                import time
                time.sleep(0.5)
    
    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """Remove item from cart"""
    # Use current_user from Flask-Login
    user_id = current_user.id
    cart_item = None
    
    # Database operations with retry
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
            
            if not cart_item:
                flash('Item not found in your cart.', 'danger')
                return redirect(url_for('view_cart'))
            
            product_name = cart_item.product_name
            db.session.delete(cart_item)
            db.session.commit()
            
            flash(f'Removed {product_name} from your cart.', 'success')
            break  # Operation successful
            
        except Exception as e:
            logger.error(f"Database error during remove_from_cart (attempt {retry_count+1}): {e}")
            db.session.rollback()
            retry_count += 1
            
            if retry_count >= max_retries:
                flash('Service temporarily unavailable. Please try again later.', 'danger')
            else:
                # Wait before retrying
                import time
                time.sleep(0.5)
    
    return redirect(url_for('view_cart'))

@app.route('/cart/update/<item_id>', methods=['POST'])
@login_required
def update_cart_quantity(item_id):
    """Update cart item quantity"""
    # Use current_user from Flask-Login
    user_id = current_user.id
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity < 1:
        quantity = 1
    
    # Database operations with retry
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
            
            if not cart_item:
                flash('Item not found in your cart.', 'danger')
                return redirect(url_for('view_cart'))
            
            cart_item.quantity = quantity
            db.session.commit()
            
            flash(f'Updated {cart_item.product_name} quantity.', 'success')
            break  # Operation successful
            
        except Exception as e:
            logger.error(f"Database error during update_cart_quantity (attempt {retry_count+1}): {e}")
            db.session.rollback()
            retry_count += 1
            
            if retry_count >= max_retries:
                flash('Service temporarily unavailable. Please try again later.', 'danger')
            else:
                # Wait before retrying
                import time
                time.sleep(0.5)
    
    return redirect(url_for('view_cart'))

# API Endpoints
@app.route('/api/search', methods=['GET'])
def api_search():
    """API endpoint for searching products"""
    query = request.args.get('query', '')
    category = request.args.get('category', 'all')
    
    results = search_products(query, category)
    return jsonify(results)

@app.route('/api/cheapest', methods=['GET'])
def api_cheapest():
    """API endpoint to get the cheapest price for a product"""
    product_name = request.args.get('product', '')
    
    if not product_name:
        return jsonify({"error": "Product name is required"}), 400
    
    cheapest = get_cheapest_price(product_name)
    if not cheapest:
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify(cheapest)

@app.route('/api/products/<product_id>', methods=['GET'])
def api_product_detail(product_id):
    """API endpoint to get product details"""
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify(product)

# Initialize the app
def initialize_app():
    """Initialize the application with data and scheduler"""
    # Load initial product data
    load_initial_data()
    
    # Initialize the scheduler
    initialize_scheduler(update_product_data)
    
    # Register Google OAuth blueprint if configured
    try:
        # Import Google OAuth blueprint
        from google_auth import google_auth
        
        # Register the blueprint
        app.register_blueprint(google_auth)
        logger.info("Google OAuth blueprint registered successfully")
    except Exception as e:
        logger.error(f"Failed to register Google OAuth blueprint: {e}")

def update_product_data():
    """Update product data from scrapers - called by scheduler"""
    try:
        # Get new data from scrapers
        amazon_products = get_amazon_products("skincare")
        flipkart_products = get_flipkart_products("skincare")
        nykaa_products = get_nykaa_products("skincare")
        
        # Update global products data
        global products_data
        products_data = amazon_products + flipkart_products + nykaa_products
        
        logger.info(f"Updated products data. Total products: {len(products_data)}")
    except Exception as e:
        logger.error(f"Error updating product data: {e}")

# Initialize the app when this module is imported
initialize_app()
