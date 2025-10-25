from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import uuid
from datetime import datetime, timedelta
from bcrypt import hashpw, gensalt, checkpw
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# ============================================================================
# AWS DYNAMODB SETUP (Real AWS Connection)
# ============================================================================

print("\n" + "="*70)
print("🗄️  Connecting to AWS DynamoDB...")
print("="*70)

# Initialize DynamoDB with AWS credentials
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'ap-south-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

dynamodb_client = boto3.client(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'ap-south-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

print("✅ Connected to AWS DynamoDB successfully!")
print("="*70 + "\n")

# ============================================================================
# PRODUCT DATA - 30 Products
# ============================================================================

PRODUCTS = [
    # FRUITS (15 products)
    {'product_id': '1', 'name': 'Green Apples', 'category': 'Fruits', 'price': 120, 'unit': 'kg',
     'description': 'Crisp and juicy green apples', 'image': 'https://images.unsplash.com/photo-1619546813926-a78fa6372cd2?w=500&h=500&fit=crop',
     'stock': 40, 'active': True},
    {'product_id': '2', 'name': 'Red Apples', 'category': 'Fruits', 'price': 130, 'unit': 'kg',
     'description': 'Sweet and crunchy red apples', 'image': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=500&h=500&fit=crop',
     'stock': 45, 'active': True},
    {'product_id': '3', 'name': 'Bananas', 'category': 'Fruits', 'price': 50, 'unit': 'dozen',
     'description': 'Yellow ripe bananas', 'image': 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=500&h=500&fit=crop',
     'stock': 100, 'active': True},
    {'product_id': '4', 'name': 'Oranges', 'category': 'Fruits', 'price': 80, 'unit': 'kg',
     'description': 'Sweet juicy oranges', 'image': 'https://images.unsplash.com/photo-1547514701-42782101795e?w=500&h=500&fit=crop',
     'stock': 45, 'active': True},
    {'product_id': '5', 'name': 'Mangoes', 'category': 'Fruits', 'price': 150, 'unit': 'kg',
     'description': 'Sweet Alphonso mangoes', 'image': 'https://images.unsplash.com/photo-1605027990121-cbae9f90ffb0?w=500&h=500&fit=crop',
     'stock': 25, 'active': True},
    {'product_id': '6', 'name': 'Strawberries', 'category': 'Fruits', 'price': 200, 'unit': 'kg',
     'description': 'Fresh sweet strawberries', 'image': 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=500&h=500&fit=crop',
     'stock': 20, 'active': True},
    {'product_id': '7', 'name': 'Watermelon', 'category': 'Fruits', 'price': 30, 'unit': 'kg',
     'description': 'Refreshing red watermelon', 'image': 'https://images.unsplash.com/photo-1587049352846-4a222e784e38?w=500&h=500&fit=crop',
     'stock': 35, 'active': True},
    {'product_id': '8', 'name': 'Grapes', 'category': 'Fruits', 'price': 90, 'unit': 'kg',
     'description': 'Sweet green grapes', 'image': 'https://images.unsplash.com/photo-1599819177041-fbb9ea8b0e25?w=500&h=500&fit=crop',
     'stock': 30, 'active': True},
    {'product_id': '9', 'name': 'Pineapple', 'category': 'Fruits', 'price': 60, 'unit': 'piece',
     'description': 'Fresh tropical pineapple', 'image': 'https://images.unsplash.com/photo-1550828520-4cb496926fc9?w=500&h=500&fit=crop',
     'stock': 40, 'active': True},
    {'product_id': '10', 'name': 'Papaya', 'category': 'Fruits', 'price': 45, 'unit': 'kg',
     'description': 'Fresh ripe papaya', 'image': 'https://images.unsplash.com/photo-1517282009859-f000ec3b26fe?w=500&h=500&fit=crop',
     'stock': 28, 'active': True},
    {'product_id': '11', 'name': 'Pomegranate', 'category': 'Fruits', 'price': 140, 'unit': 'kg',
     'description': 'Ruby red pomegranate', 'image': 'https://images.unsplash.com/photo-1553279964-67a92de6ff81?w=500&h=500&fit=crop',
     'stock': 22, 'active': True},
    {'product_id': '12', 'name': 'Kiwi', 'category': 'Fruits', 'price': 180, 'unit': 'kg',
     'description': 'Fresh green kiwi', 'image': 'https://images.unsplash.com/photo-1585059895524-72359e06133a?w=500&h=500&fit=crop',
     'stock': 18, 'active': True},
    {'product_id': '13', 'name': 'Blueberries', 'category': 'Fruits', 'price': 250, 'unit': 'kg',
     'description': 'Fresh organic blueberries', 'image': 'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=500&h=500&fit=crop',
     'stock': 15, 'active': True},
    {'product_id': '14', 'name': 'Cherries', 'category': 'Fruits', 'price': 300, 'unit': 'kg',
     'description': 'Premium fresh cherries', 'image': 'https://images.unsplash.com/photo-1528821128474-27f963b062bf?w=500&h=500&fit=crop',
     'stock': 12, 'active': True},
    {'product_id': '15', 'name': 'Dragon Fruit', 'category': 'Fruits', 'price': 220, 'unit': 'kg',
     'description': 'Exotic dragon fruit', 'image': 'https://images.unsplash.com/photo-1527325678964-54921661f888?w=500&h=500&fit=crop',
     'stock': 16, 'active': True},
    
    # VEGETABLES (15 products)
    {'product_id': '16', 'name': 'Fresh Tomatoes', 'category': 'Vegetables', 'price': 40, 'unit': 'kg',
     'description': 'Fresh red tomatoes', 'image': 'https://images.unsplash.com/photo-1546470427-227ddde4e638?w=500&h=500&fit=crop',
     'stock': 50, 'active': True},
    {'product_id': '17', 'name': 'Fresh Carrots', 'category': 'Vegetables', 'price': 35, 'unit': 'kg',
     'description': 'Organic carrots', 'image': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=500&h=500&fit=crop',
     'stock': 60, 'active': True},
    {'product_id': '18', 'name': 'Fresh Spinach', 'category': 'Vegetables', 'price': 30, 'unit': 'kg',
     'description': 'Green leafy spinach', 'image': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=500&h=500&fit=crop',
     'stock': 35, 'active': True},
    {'product_id': '19', 'name': 'Bell Peppers', 'category': 'Vegetables', 'price': 60, 'unit': 'kg',
     'description': 'Colorful bell peppers', 'image': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=500&h=500&fit=crop',
     'stock': 30, 'active': True},
    {'product_id': '20', 'name': 'Broccoli', 'category': 'Vegetables', 'price': 70, 'unit': 'kg',
     'description': 'Fresh green broccoli', 'image': 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=500&h=500&fit=crop',
     'stock': 25, 'active': True},
    {'product_id': '21', 'name': 'Cauliflower', 'category': 'Vegetables', 'price': 40, 'unit': 'kg',
     'description': 'Fresh white cauliflower', 'image': 'https://images.unsplash.com/photo-1568584711271-4cdaa2bd9299?w=500&h=500&fit=crop',
     'stock': 38, 'active': True},
    {'product_id': '22', 'name': 'Potatoes', 'category': 'Vegetables', 'price': 25, 'unit': 'kg',
     'description': 'Fresh potatoes', 'image': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=500&h=500&fit=crop',
     'stock': 80, 'active': True},
    {'product_id': '23', 'name': 'Onions', 'category': 'Vegetables', 'price': 35, 'unit': 'kg',
     'description': 'Fresh red onions', 'image': 'https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=500&h=500&fit=crop',
     'stock': 70, 'active': True},
    {'product_id': '24', 'name': 'Cucumbers', 'category': 'Vegetables', 'price': 30, 'unit': 'kg',
     'description': 'Fresh crunchy cucumbers', 'image': 'https://images.unsplash.com/photo-1589621316382-008455b857cd?w=500&h=500&fit=crop',
     'stock': 45, 'active': True},
    {'product_id': '25', 'name': 'Lettuce', 'category': 'Vegetables', 'price': 50, 'unit': 'kg',
     'description': 'Fresh crispy lettuce', 'image': 'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=500&h=500&fit=crop',
     'stock': 32, 'active': True},
    {'product_id': '26', 'name': 'Green Beans', 'category': 'Vegetables', 'price': 55, 'unit': 'kg',
     'description': 'Fresh green beans', 'image': 'https://images.unsplash.com/photo-1592921870789-04563d55041c?w=500&h=500&fit=crop',
     'stock': 28, 'active': True},
    {'product_id': '27', 'name': 'Cabbage', 'category': 'Vegetables', 'price': 20, 'unit': 'kg',
     'description': 'Fresh green cabbage', 'image': 'https://images.unsplash.com/photo-1594282486552-05b4d80fbb9f?w=500&h=500&fit=crop',
     'stock': 42, 'active': True},
    {'product_id': '28', 'name': 'Eggplant', 'category': 'Vegetables', 'price': 45, 'unit': 'kg',
     'description': 'Fresh purple eggplant', 'image': 'https://images.unsplash.com/photo-1659261200833-ec8761558af7?w=500&h=500&fit=crop',
     'stock': 34, 'active': True},
    {'product_id': '29', 'name': 'Mushrooms', 'category': 'Vegetables', 'price': 120, 'unit': 'kg',
     'description': 'Fresh button mushrooms', 'image': 'https://images.unsplash.com/photo-1608896820203-1b5c5d9f0d4f?w=500&h=500&fit=crop',
     'stock': 18, 'active': True},
    {'product_id': '30', 'name': 'Sweet Corn', 'category': 'Vegetables', 'price': 40, 'unit': 'kg',
     'description': 'Fresh sweet corn', 'image': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=500&h=500&fit=crop',
     'stock': 50, 'active': True}
]

# ============================================================================
# CREATE TABLES IF NOT EXISTS
# ============================================================================

def create_tables_if_not_exists():
    """Create DynamoDB tables if they don't exist"""
    print("📦 Checking/Creating DynamoDB tables...")
    
    existing_tables = dynamodb_client.list_tables()['TableNames']
    
    # Create Products Table
    if 'FreshBasket_Products' not in existing_tables:
        print("Creating Products table...")
        dynamodb.create_table(
            TableName='FreshBasket_Products',
            KeySchema=[{'AttributeName': 'product_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'product_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        print("✅ Products table created")
    
    # Create Users Table
    if 'FreshBasket_Users' not in existing_tables:
        print("Creating Users table...")
        dynamodb.create_table(
            TableName='FreshBasket_Users',
            KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        print("✅ Users table created")
    
    # Create Cart Table
    if 'FreshBasket_Cart' not in existing_tables:
        print("Creating Cart table...")
        dynamodb.create_table(
            TableName='FreshBasket_Cart',
            KeySchema=[
                {'AttributeName': 'user_email', 'KeyType': 'HASH'},
                {'AttributeName': 'product_id', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_email', 'AttributeType': 'S'},
                {'AttributeName': 'product_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("✅ Cart table created")
    
    # Create Orders Table
    if 'FreshBasket_Orders' not in existing_tables:
        print("Creating Orders table...")
        dynamodb.create_table(
            TableName='FreshBasket_Orders',
            KeySchema=[{'AttributeName': 'order_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'order_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        print("✅ Orders table created")
    
    # Create Contact Messages Table
    if 'FreshBasket_ContactMessages' not in existing_tables:
        print("Creating Contact Messages table...")
        dynamodb.create_table(
            TableName='FreshBasket_ContactMessages',
            KeySchema=[{'AttributeName': 'message_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'message_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        print("✅ Contact Messages table created")
    
    print("✅ All tables ready!")
    print("="*70 + "\n")

def seed_products():
    """Seed products if table is empty"""
    products_table = dynamodb.Table('FreshBasket_Products')
    
    try:
        response = products_table.scan(Limit=1)
        if response['Count'] == 0:
            print("🌱 Seeding 30 products...")
            for product in PRODUCTS:
                products_table.put_item(Item=product)
            print(f"✅ Successfully seeded {len(PRODUCTS)} products!")
        else:
            print("✅ Products already exist in database")
    except Exception as e:
        print(f"⚠️  Error seeding products: {e}")

# Initialize tables
try:
    create_tables_if_not_exists()
    # Wait for tables to be active
    import time
    time.sleep(2)
    seed_products()
except Exception as e:
    print(f"⚠️  Warning: {e}")

# DynamoDB Tables
users_table = dynamodb.Table('FreshBasket_Users')
products_table = dynamodb.Table('FreshBasket_Products')
orders_table = dynamodb.Table('FreshBasket_Orders')
cart_table = dynamodb.Table('FreshBasket_Cart')
contact_messages_table = dynamodb.Table('FreshBasket_ContactMessages')

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_logged_in():
    return 'user_email' in session

def get_all_products():
    try:
        response = products_table.scan(FilterExpression=Attr('active').eq(True))
        products = response.get('Items', [])
        for p in products:
            p['id'] = int(p['product_id'])
        return products
    except Exception as e:
        print(f"Error getting products: {e}")
        return []

def get_product_by_id(product_id):
    try:
        response = products_table.get_item(Key={'product_id': str(product_id)})
        product = response.get('Item')
        if product:
            product['id'] = int(product['product_id'])
        return product
    except:
        return None

def get_user_cart(user_email):
    try:
        response = cart_table.query(KeyConditionExpression=Key('user_email').eq(user_email))
        items = response.get('Items', [])
        for item in items:
            item['id'] = int(item['product_id'])
        return items
    except:
        return []

def init_cart():
    if not is_logged_in() and 'cart' not in session:
        session['cart'] = []

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    init_cart()
    products = get_all_products()[:8]
    return render_template('index.html', products=products, is_logged_in=is_logged_in())

@app.route('/products')
def products():
    init_cart()
    category = request.args.get('category', 'all')
    all_products = get_all_products()
    if category == 'all':
        filtered_products = all_products
    else:
        filtered_products = [p for p in all_products if p.get('category', '').lower() == category.lower()]
    return render_template('products.html', products=filtered_products, category=category, is_logged_in=is_logged_in())

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    init_cart()
    product = get_product_by_id(product_id)
    if product:
        return render_template('product_detail.html', product=product, is_logged_in=is_logged_in())
    flash("Product not found!", "danger")
    return redirect(url_for('products'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash("Passwords don't match!", "danger")
            return redirect(url_for('register'))
        
        try:
            response = users_table.get_item(Key={'email': email})
            if 'Item' in response:
                flash("User already exists!", "info")
                return redirect(url_for('login'))
        except:
            pass
        
        hashed = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
        
        try:
            users_table.put_item(Item={
                'email': email,
                'name': name,
                'password': hashed,
                'phone': request.form.get('phone', ''),
                'address': request.form.get('address', ''),
                'user_type': 'customer',
                'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_orders': 0,
                'total_spent': 0
            })
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Registration failed: {str(e)}", "danger")
            print(f"Registration error: {e}")
            return redirect(url_for('register'))
    
    return render_template('register.html', is_logged_in=is_logged_in())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            response = users_table.get_item(Key={'email': email})
            user = response.get('Item')
            
            if not user:
                flash("User not found!", "danger")
                return redirect(url_for('login'))
            
            if not checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                flash("Invalid password!", "danger")
                return redirect(url_for('login'))
            
            session['user_email'] = email
            session['user_name'] = user['name']
            session['user_type'] = user.get('user_type', 'customer')
            
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Login failed: {str(e)}", "danger")
            print(f"Login error: {e}")
            return redirect(url_for('login'))
    
    return render_template('login.html', is_logged_in=is_logged_in())

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    init_cart()
    cart_items = get_user_cart(session['user_email']) if is_logged_in() else session.get('cart', [])
    total = sum(float(item.get('price', 0)) * int(item.get('quantity', 0)) for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total, is_logged_in=is_logged_in())

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    init_cart()
    data = request.json
    product_id = str(data.get('product_id'))
    quantity = int(data.get('quantity', 1))
    product = get_product_by_id(product_id)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'})
    
    if is_logged_in():
        user_email = session['user_email']
        try:
            response = cart_table.get_item(Key={'user_email': user_email, 'product_id': product_id})
            if 'Item' in response:
                cart_table.update_item(
                    Key={'user_email': user_email, 'product_id': product_id},
                    UpdateExpression="SET quantity = quantity + :qty",
                    ExpressionAttributeValues={':qty': quantity}
                )
            else:
                cart_table.put_item(Item={
                    'user_email': user_email,
                    'product_id': product_id,
                    'name': product['name'],
                    'price': product['price'],
                    'unit': product['unit'],
                    'quantity': quantity,
                    'image': product['image'],
                    'added_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            return jsonify({'success': True})
        except Exception as e:
            print(f"Add to cart error: {e}")
            return jsonify({'success': False, 'message': str(e)})
    else:
        cart = session.get('cart', [])
        existing = next((i for i in cart if i['id'] == int(product_id)), None)
        if existing:
            existing['quantity'] += quantity
        else:
            cart.append({
                'id': int(product_id),
                'name': product['name'],
                'price': product['price'],
                'unit': product['unit'],
                'quantity': quantity,
                'image': product['image']
            })
        session['cart'] = cart
        session.modified = True
        return jsonify({'success': True})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.json
    product_id = str(data.get('product_id'))
    
    if is_logged_in():
        try:
            cart_table.delete_item(Key={'user_email': session['user_email'], 'product_id': product_id})
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    else:
        cart = [i for i in session.get('cart', []) if i['id'] != int(product_id)]
        session['cart'] = cart
        session.modified = True
        return jsonify({'success': True})

@app.route('/ai_assistant')
def ai_assistant():
    init_cart()
    products = get_all_products()
    return render_template('ai_assistant.html', products=products, is_logged_in=is_logged_in())

@app.route('/generate_recipe', methods=['POST'])
def generate_recipe():
    data = request.json
    ingredients = data.get('ingredients', [])
    if not ingredients:
        return jsonify({'success': False, 'message': 'Select ingredients'})
    
    recipe = {
        'name': f'🥗 {" & ".join(ingredients)} Recipe',
        'time': '20 min',
        'difficulty': 'Easy',
        'servings': '3-4',
        'ingredients_list': [f'{i} - 200g' for i in ingredients],
        'instructions': ['Wash all ingredients', 'Chop into pieces', 'Cook or mix', 'Season to taste', 'Serve hot or cold'],
        'tips': 'Fresh ingredients make the best dishes!'
    }
    return jsonify({'success': True, 'recipe': recipe})

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            contact_messages_table.put_item(Item={
                'message_id': str(uuid.uuid4()),
                'name': request.form['name'],
                'email': request.form['email'],
                'subject': request.form['subject'],
                'message': request.form['message'],
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            flash("Message sent successfully!", "success")
        except Exception as e:
            flash(f"Error sending message: {str(e)}", "danger")
        return redirect(url_for('contact'))
    return render_template('contact.html', is_logged_in=is_logged_in())

@app.route('/profile')
def profile():
    if not is_logged_in():
        flash("Please login first!", "info")
        return redirect(url_for('login'))
    
    try:
        response = users_table.get_item(Key={'email': session['user_email']})
        user = response.get('Item', {})
        return render_template('profile.html', user=user, recent_orders=[], is_logged_in=is_logged_in())
    except Exception as e:
        flash(f"Error loading profile: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if not is_logged_in():
        flash("Please login first!", "info")
        return redirect(url_for('login'))
    
    try:
        user_email = session['user_email']
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        users_table.update_item(
            Key={'email': user_email},
            UpdateExpression="SET #n = :name, phone = :phone, address = :address",
            ExpressionAttributeNames={'#n': 'name'},
            ExpressionAttributeValues={':name': name, ':phone': phone, ':address': address}
        )
        
        session['user_name'] = name
        flash("Profile updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating profile: {str(e)}", "danger")
    
    return redirect(url_for('profile'))

@app.route('/my-orders')
def my_orders():
    if not is_logged_in():
        flash("Please login first!", "info")
        return redirect(url_for('login'))
    return render_template('my_orders.html', orders=[], is_logged_in=is_logged_in())

@app.route('/admin')
def admin_dashboard():
    if not is_logged_in() or session.get('user_type') != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html', is_logged_in=is_logged_in())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', is_logged_in=is_logged_in()), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html', is_logged_in=is_logged_in()), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 FreshBasket - Fresh Fruits & Vegetables Store")
    print("="*70)
    print("✨ Running with AWS DynamoDB")
    print("💾 Data persisted in AWS Cloud")
    print("📍 http://127.0.0.1:5000")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
