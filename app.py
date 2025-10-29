from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import json
import os 
from datetime import datetime
from werkzeug.utils import secure_filename
import google.generativeai as genai
import hashlib
from functools import wraps
import qrcode
import io

from mysql.connector import Error, pooling
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
import colorama


from brain.review_validator import validate_review
from brain.db_setup import create_users_table, create_artworks_table, create_community_posts_table, create_contact_table
from brain.config import load_config
from brain.price_generator import generate as generate_price
from brain.description_generator import generate_description as generate_desc
from brain.ai_image_enhancer import edit_image_with_traditional_background


config = load_config()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database configuration from config.ini
DB_CONFIG = {
    'host': config.get('DATABASE', 'host', fallback='localhost'),
    'user': config.get('DATABASE', 'user'),
    'password': config.get('DATABASE', 'password'),
    'database': config.get('DATABASE', 'database', fallback='takneev5')
}

# Try to create connection pool
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=10,
        pool_reset_session=True,
        **DB_CONFIG
    )
    print(colorama.Fore.LIGHTGREEN_EX + f"\n✓ Successfully connected to MySQL database: {DB_CONFIG['database']}" + colorama.Style.RESET_ALL)
except Error as e:
    print(colorama.Fore.RED + f"\nERROR: Could not connect to MySQL database: {e}" + colorama.Style.RESET_ALL)

# Thread pool for async operations
executor = ThreadPoolExecutor(max_workers=5)

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    connection = connection_pool.get_connection()
    try:
        yield connection
    finally:
        connection.close()

@contextmanager
def get_db_cursor(commit=False):
    """Context manager for database operations"""
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            yield cursor
            if commit:
                connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()

def xhr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return render_template("index.html"), 403
        return f(*args, **kwargs)
    return decorated_function

# Configuration
UPLOAD_FOLDER = 'static/uploads/artworks'
TEMP_UPLOAD_FOLDER = 'static/uploads/temp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi', 'pdf'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/uploads/community', exist_ok=True)

# Gemini API Configuration
my_api_key = config.get('API', 'gemini_api_key', fallback='')
genai.configure(api_key=my_api_key)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def increment_view_count_async(artwork_id):
    """Asynchronously increment view count"""
    def _increment():
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute(
                    "UPDATE artworks SET views = views + 1 WHERE id = %s",
                    (artwork_id,)
                )
        except Exception as e:
            print(f"Error incrementing view count: {e}")
    
    executor.submit(_increment)


def generate(image_path, details_text):
    future = executor.submit(generate_price, image_path, details_text)
    return future.result()

def generate_description(image_path, title, category, material, existing_description=""):
    future = executor.submit(generate_desc, image_path, title, category, material, existing_description)
    return future.result()

def correct_and_translate_text(text_to_correct):
    """Corrects spelling and translates text to English using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        prompt = f"Correct the spelling of the following text. If the text is not in English, translate it to English. Do not add any extra information or change the meaning. Just provide the corrected and translated text. The text is: '{text_to_correct}'"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred during text correction: {e}")
        return text_to_correct

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/tools")
def tools():
    return render_template("tools.html")

@app.route("/marketplace")
def marketplace():
    return render_template("marketplace.html")

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all artworks for marketplace display"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT a.*, u.name as artist_name
                FROM artworks a
                JOIN users u ON a.user_email = u.email
                WHERE a.status = 'published'
                ORDER BY a.created_at DESC
            """)
            artworks = cursor.fetchall()
            
            products = []
            for artwork in artworks:
                files = json.loads(artwork['files']) if artwork['files'] else []
                product = {
                    'id': artwork['id'],
                    'name': artwork['title'],
                    'artist': artwork['artist_name'],
                    'category': artwork['category'],
                    'price': float(artwork['price']) if artwork['price'] else 0,
                    'image': f"/static/{files[0]}" if files else 'https://via.placeholder.com/400x280/f9fafb/9ca3af?text=No+Image',
                    'images': [f"/static/{file}" for file in files],
                    'location': 'India',
                    'rating': 4.5,
                    'reviews': artwork['views'],
                    'authentic': True,
                    'description': artwork['description'],
                    'material': artwork['material'],
                    'created_at': artwork['created_at'].isoformat() if artwork['created_at'] else None,
                    'views': artwork['views'],
                    'likes': artwork['likes']
                }
                products.append(product)
            
            return jsonify(products), 200
    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        return jsonify({'error': 'Failed to fetch products'}), 500

@app.route('/api/product/<product_id>', methods=['GET'])
def get_product_details(product_id):
    """Get detailed information about a specific product"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT a.*, u.name as artist_name
                FROM artworks a
                JOIN users u ON a.user_email = u.email
                WHERE a.id = %s
            """, (product_id,))
            artwork = cursor.fetchone()
            
            if not artwork:
                return jsonify({'error': 'Product not found'}), 404
            
            # Increment view count asynchronously
            increment_view_count_async(product_id)
            
            files = json.loads(artwork['files']) if artwork['files'] else []
            feedback = json.loads(artwork['feedback']) if artwork['feedback'] else []
            
            product = {
                'id': artwork['id'],
                'name': artwork['title'],
                'artist': artwork['artist_name'],
                'artist_email': artwork['user_email'],
                'category': artwork['category'],
                'price': float(artwork['price']) if artwork['price'] else 0,
                'images': [f"/static/{file}" for file in files],
                'location': 'India',
                'rating': 4.5,
                'reviews': artwork['views'],
                'authentic': True,
                'description': artwork['description'],
                'material': artwork['material'],
                'created_at': artwork['created_at'].isoformat() if artwork['created_at'] else None,
                'views': artwork['views'],
                'likes': artwork['likes'],
                'feedback': feedback
            }
            
            return jsonify(product), 200
    except Exception as e:
        print(f"Error fetching product details: {str(e)}")
        return jsonify({'error': 'Failed to fetch product details'}), 500

@app.route('/api/product/<product_id>/like', methods=['POST'])
@xhr_required
def like_product(product_id):
    """Like/Unlike a product"""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE artworks SET likes = likes + 1 WHERE id = %s",
                (product_id,)
            )
            
            cursor.execute("SELECT likes FROM artworks WHERE id = %s", (product_id,))
            result = cursor.fetchone()
            
            if not result:
                return jsonify({'error': 'Product not found'}), 404
            
            return jsonify({
                'success': True,
                'likes': result['likes']
            }), 200
    except Exception as e:
        print(f"Error liking product: {str(e)}")
        return jsonify({'error': 'Failed to like product'}), 500

@app.route("/community")
def community():
    return render_template("community.html")

@app.route('/api/community/posts', methods=['GET', 'POST'])
def handle_community_posts():
    COMMUNITY_UPLOAD_FOLDER = 'static/uploads/community'
    
    if request.method == 'GET':
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT cp.*, u.name as artist_name
                    FROM community_posts cp
                    JOIN users u ON cp.user_email = u.email
                    ORDER BY cp.timestamp DESC
                """)
                posts = cursor.fetchall()
                
                for post in posts:
                    if post['timestamp']:
                        post['timestamp'] = post['timestamp'].isoformat()
                
                return jsonify(posts)
        except Exception as e:
            print(f"Error fetching community posts: {str(e)}")
            return jsonify([])
    
    if request.method == 'POST':
        if 'user_email' not in session:
            return jsonify({'success': False, 'message': 'Please login first'}), 401
        
        description = request.form.get('description')
        if not description:
            return jsonify({'success': False, 'message': 'Description is required'}), 400
        
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                image_path = os.path.join(COMMUNITY_UPLOAD_FOLDER, unique_filename)
                file.save(image_path)
                image_path = image_path.replace('\\', '/')
        
        try:
            with get_db_cursor(commit=True) as cursor:
                post_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
                cursor.execute("""
                    INSERT INTO community_posts (id, user_email, description, image, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (post_id, session['user_email'], description, image_path, datetime.now()))
                
                return jsonify({'success': True, 'message': 'Post created successfully'}), 201
        except Exception as e:
            print(f"Error creating post: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to create post'}), 500

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/join")
def join():
    return render_template("join.html")

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check if email exists
            cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': 'Email already registered'})
            
            # Hash password
            salt = os.urandom(16).hex()
            hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
            
            # Insert user
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, f"{salt}:{hashed_password}")
            )
            
            session['user_email'] = email
            return jsonify({'success': True, 'message': 'Account created successfully'})
    except Exception as e:
        print(f"Error during signup: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred during signup'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                stored_password_full = user['password']
                if ':' in stored_password_full:
                    salt, stored_password_hash = stored_password_full.split(':', 1)
                    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
                    
                    if hashed_password == stored_password_hash:
                        session['user_email'] = email
                        next_url = request.json.get('next')
                        if next_url == 'community':
                            return jsonify({'success': True, 'message': 'Login successful', 'redirect': url_for('community')})
                        return jsonify({'success': True, 'message': 'Login successful'})
            
            return jsonify({'success': False, 'message': 'Invalid email or password'})
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred during login'}), 500

@app.route('/api/upload-artwork', methods=['POST'])
def upload_artwork():
    """Handle artwork upload with images and metadata"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    try:
        title = request.form.get('title').title()
        category = request.form.get('category')
        corrected_title = correct_and_translate_text(title)
        corrected_category = correct_and_translate_text(category)
        material = request.form.get('material')
        description = request.form.get('description')
        price = request.form.get('price', '')
        
        if not all([corrected_title, corrected_category, material, description]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        uploaded_files = []
        filepath = None
        
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{filename}"
                    filepath_temp = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file.save(filepath_temp)
                    
                    if not filepath:
                        filepath = filepath_temp
                    
                    uploaded_files.append(f'uploads/artworks/{unique_filename}')
        
        if not uploaded_files or not filepath:
            return jsonify({'success': False, 'message': 'At least one file is required'}), 400
        
        details_text = f"""
        Title: {corrected_title}
        Category: {corrected_category}
        Material: {material}
        Description: {description}
        """
        
        if not price:
            generated_price = generate(filepath, details_text)
            price = generated_price
        
        with get_db_cursor(commit=True) as cursor:
            artwork_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            cursor.execute("""
                INSERT INTO artworks 
                (id, user_email, title, category, material, description, price, files, created_at, status, views, likes, feedback)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                artwork_id,
                session['user_email'],
                corrected_title,
                corrected_category,
                material,
                description,
                float(price) if price and price.replace('INR', '').strip().replace(',', '').isdigit() else None,
                json.dumps(uploaded_files),
                datetime.now(),
                'published',
                0,
                0,
                json.dumps([])
            ))
            
            return jsonify({
                'success': True,
                'message': 'Artwork uploaded successfully!',
                'artwork': {
                    'id': artwork_id,
                    'title': corrected_title,
                    'category': corrected_category
                }
            }), 200
    except Exception as e:
        print(f"Error uploading artwork: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while uploading'}), 500

@app.route('/api/my-artworks', methods=['GET'])
@xhr_required
def get_my_artworks():
    """Get all artworks uploaded by the logged-in user"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM artworks WHERE user_email = %s ORDER BY created_at DESC
            """, (session['user_email'],))
            artworks = cursor.fetchall()
            
            for artwork in artworks:
                artwork['files'] = json.loads(artwork['files']) if artwork['files'] else []
                artwork['feedback'] = json.loads(artwork['feedback']) if artwork['feedback'] else []
                if artwork['created_at']:
                    artwork['created_at'] = artwork['created_at'].isoformat()
            
            return jsonify({'success': True, 'artworks': artworks}), 200
    except Exception as e:
        print(f"Error fetching artworks: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/api/my-posts', methods=['GET'])
@xhr_required
def get_my_posts():
    """Get all posts by the logged-in user"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM community_posts WHERE user_email = %s ORDER BY timestamp DESC
            """, (session['user_email'],))
            posts = cursor.fetchall()
            
            for post in posts:
                if post['timestamp']:
                    post['timestamp'] = post['timestamp'].isoformat()
            
            return jsonify({'success': True, 'posts': posts}), 200
    except Exception as e:
        print(f"Error fetching posts: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/api/delete-post/<post_id>', methods=['DELETE'])
@xhr_required
def delete_post(post_id):
    """Delete a community post"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                SELECT image FROM community_posts WHERE id = %s AND user_email = %s
            """, (post_id, session['user_email']))
            post = cursor.fetchone()
            
            if not post:
                return jsonify({'success': False, 'message': 'Post not found'}), 404
            
            if post['image'] and os.path.exists(post['image']):
                os.remove(post['image'])
            
            cursor.execute("""
                DELETE FROM community_posts WHERE id = %s AND user_email = %s
            """, (post_id, session['user_email']))
            
            return jsonify({'success': True, 'message': 'Post deleted successfully'}), 200
    except Exception as e:
        print(f"Error deleting post: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/api/delete-artwork/<artwork_id>', methods=['DELETE'])
@xhr_required
def delete_artwork(artwork_id):
    """Delete an artwork"""
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                SELECT files FROM artworks WHERE id = %s AND user_email = %s
            """, (artwork_id, session['user_email']))
            artwork = cursor.fetchone()
            
            if not artwork:
                return jsonify({'success': False, 'message': 'Artwork not found'}), 404
            
            files = json.loads(artwork['files']) if artwork['files'] else []
            for file_path in files:
                full_path = os.path.join('static', file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
            
            cursor.execute("""
                DELETE FROM artworks WHERE id = %s AND user_email = %s
            """, (artwork_id, session['user_email']))
            
            return jsonify({'success': True, 'message': 'Artwork deleted successfully'}), 200
    except Exception as e:
        print(f"Error deleting artwork: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/studio')
def studio():
    is_logged_in = 'user_email' in session
    user = None
    if is_logged_in:
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT name, email FROM users WHERE email = %s", (session['user_email'],))
                user = cursor.fetchone()
        except Exception as e:
            print(f"Error fetching user: {str(e)}")
    
    return render_template("studio.html", is_logged_in=is_logged_in, user=user)

@app.route('/api/check-auth')
@xhr_required
def check_auth():
    if 'user_email' in session:
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT name, email FROM users WHERE email = %s", (session['user_email'],))
                user = cursor.fetchone()
                return jsonify({'logged_in': True, 'user': user})
        except Exception as e:
            print(f"Error checking auth: {str(e)}")
    return jsonify({'logged_in': False})

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('studio'))

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Render product detail page"""
    return render_template('product_detail.html', product_id=product_id)


@app.route('/submit_feedback/<product_id>', methods=['POST'])
def submit_feedback(product_id):
    feedback_text = request.form.get('feedback_text')
    
    if not feedback_text:
        return jsonify({'success': False, 'message': 'Feedback cannot be empty.'}), 400

    # Run validation in a separate thread
    validation_future = executor.submit(validate_review, feedback_text)
    validation_result = validation_future.result()

    if validation_result == 'bad':
        return render_template('feedback_popup.html', message='Your review contains inappropriate content and will not be saved.')
  
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("SELECT feedback FROM artworks WHERE id = %s", (product_id,))
            artwork = cursor.fetchone()
            
            if not artwork:
                return jsonify({'success': False, 'message': 'Product not found.'}), 404
            
            feedback = json.loads(artwork['feedback']) if artwork['feedback'] else []
            feedback.append(feedback_text)
            
            cursor.execute(
                "UPDATE artworks SET feedback = %s WHERE id = %s",
                (json.dumps(feedback), product_id)
            )
            
            return redirect(url_for('product_detail', product_id=product_id))
    except Exception as e:
        print(f"Error submitting feedback: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/artist/<artist_name>')
def artist_arts(artist_name):
    """Render page with all artworks by a specific artist"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT email FROM users WHERE name = %s", (artist_name,))
            artist = cursor.fetchone()
            
            if artist:
                cursor.execute("""
                    SELECT * FROM artworks 
                    WHERE user_email = %s AND status = 'published'
                    ORDER BY created_at DESC
                """, (artist['email'],))
                artworks = cursor.fetchall()
                
                for artwork in artworks:
                    artwork['files'] = json.loads(artwork['files']) if artwork['files'] else []
                    if artwork['created_at']:
                        artwork['created_at'] = artwork['created_at'].isoformat()
            else:
                artworks = []
            
            return render_template('artist_arts.html', artist_name=artist_name, artworks=artworks)
    except Exception as e:
        print(f"Error fetching artist artworks: {str(e)}")
        return render_template('artist_arts.html', artist_name=artist_name, artworks=[])

@app.route('/api/suggest-price', methods=['POST'])
@xhr_required
def suggest_price_route():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    filepath = None
    try:
        title = request.form.get('title')
        category = request.form.get('category')
        material = request.form.get('material')
        description = request.form.get('description')
        
        if not all([title, category, material, description]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Image file is required'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            unique_filename = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}_{secure_filename(file.filename)}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(filepath)
            
            details_text = f"""
            Title: {title}
            Category: {category}
            Material: {material}
            Description: {description}
            """
            
            price = generate(filepath, details_text)
            os.remove(filepath)
            
            return jsonify({'success': True, 'price': price})
        else:
            return jsonify({'success': False, 'message': 'File type not allowed'}), 400
    except Exception as e:
        print(f"Error suggesting price: {str(e)}")
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as clean_e:
                print(f"Error cleaning up file: {clean_e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/api/generate-profile-qr/<artist_name>')
def generate_profile_qr(artist_name):
    try:
        artist_url = url_for('artist_arts', artist_name=artist_name, _external=True)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(artist_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#3E2723", back_color="#F5F0E8")
        
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        print(f"Error generating profile QR code: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/api/generate-qr/<artwork_id>')
def generate_qr_route(artwork_id):
    try:
        product_url = url_for('product_detail', product_id=artwork_id, _external=True)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(product_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#3E2723", back_color="#F5F0E8")
        
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/api/ai-search', methods=['GET'])
def ai_search():
    query = request.args.get('query', '').lower()
    category = request.args.get('category', 'all').lower()
    
    if not query:
        return jsonify([])
    
    try:
        with get_db_cursor() as cursor:
            if category == 'all':
                cursor.execute("""
                    SELECT a.*, u.name as artist_name
                    FROM artworks a
                    JOIN users u ON a.user_email = u.email
                    WHERE a.status = 'published'
                """)
            else:
                cursor.execute("""
                    SELECT a.*, u.name as artist_name
                    FROM artworks a
                    JOIN users u ON a.user_email = u.email
                    WHERE a.status = 'published' AND LOWER(a.category) = %s
                """, (category,))
            
            artworks = cursor.fetchall()
            
            search_results = []
            for artwork in artworks:
                score = 0
                title_lower = artwork['title'].lower()
                category_lower = artwork['category'].lower()
                material_lower = artwork['material'].lower()
                description_lower = artwork['description'].lower()
                
                if query in title_lower:
                    score += 3
                if query in category_lower:
                    score += 2
                if query in material_lower:
                    score += 2
                if query in description_lower:
                    score += 1
                
                if score > 0:
                    files = json.loads(artwork['files']) if artwork['files'] else []
                    search_results.append({
                        'id': artwork['id'],
                        'name': artwork['title'],
                        'artist': artwork['artist_name'],
                        'category': artwork['category'],
                        'price': float(artwork['price']) if artwork['price'] else 0,
                        'image': f"/static/{files[0]}" if files else 'https://via.placeholder.com/400x280/f9fafb/9ca3af?text=No+Image',
                        'images': [f"/static/{file}" for file in files],
                        'location': 'India',
                        'rating': 4.5,
                        'reviews': artwork['views'],
                        'authentic': True,
                        'description': artwork['description'],
                        'material': artwork['material'],
                        'created_at': artwork['created_at'].isoformat() if artwork['created_at'] else None,
                        'views': artwork['views'],
                        'likes': artwork['likes'],
                        'score': score
                    })
            
            search_results.sort(key=lambda x: x['score'], reverse=True)
            return jsonify(search_results)
    except Exception as e:
        print(f"Error in AI search: {str(e)}")
        return jsonify([])

@app.route('/api/generate-description', methods=['POST'])
@xhr_required
def generate_description_route():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    filepath = None
    try:
        title = request.form.get('title')
        category = request.form.get('category')
        material = request.form.get('material')
        existing_description = request.form.get('description', '')
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Image file is required'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            unique_filename = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}_{secure_filename(file.filename)}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(filepath)
            
            description = generate_description(filepath, title, category, material, existing_description)
            os.remove(filepath)
            
            return jsonify({'success': True, 'description': description})
        else:
            return jsonify({'success': False, 'message': 'File type not allowed'}), 400
    except Exception as e:
        print(f"Error in generate-description route: {str(e)}")
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as clean_e:
                print(f"Error cleaning up file: {clean_e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@app.route('/api/enhance-image', methods=['POST'])
@xhr_required
def enhance_image_route():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            # Save temp file
            filename = secure_filename(file.filename)
            temp_filename = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}_{filename}"
            temp_path = os.path.join(TEMP_UPLOAD_FOLDER, temp_filename) # Use new temp folder
            file.save(temp_path)

            # Define output directory
            output_dir = UPLOAD_FOLDER

            # Enhance image
            enhanced_image_path = edit_image_with_traditional_background(temp_path, output_dir)

            if enhanced_image_path:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                # Return relative path for web access
                web_path = os.path.relpath(enhanced_image_path, 'static').replace('\\', '/')
                return jsonify({'success': True, 'path': f'/static/{web_path}'})
            else:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return jsonify({'success': False, 'message': 'Image enhancement failed'}), 500

        except Exception as e:
            print(f"Error enhancing image: {e}")
            # Clean up temp file in case of error
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({'success': False, 'message': str(e)}), 500

    return jsonify({'success': False, 'message': 'File type not allowed'}), 400


# Create tables if they don't exist
create_users_table(connection_pool)
create_artworks_table(connection_pool)
create_community_posts_table(connection_pool)
create_contact_table(connection_pool)

from brain.message_validator import validate_message

@app.route('/submit-contact-form', methods=['POST'])
def submit_contact_form():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    analyse = {
        'name': name,
        'subject': subject,
        'message': message 
    }

    # Run validation in a separate thread
    validation_future = executor.submit(validate_message, analyse)
    validation_result = validation_future.result()

    if validation_result == 'bad':
        return render_template('feedback_popup.html', message='Your message contains inappropriate content and will not be sent.')

    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO contact (name, email, subject, message) VALUES (%s, %s, %s, %s)
            """, (name, email, subject, message))
        return redirect(url_for('contact'))
    except Exception as e:
        print(f"Error submitting contact form: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7777)