from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import json
import os 
from datetime import datetime
from werkzeug.utils import secure_filename
import google.generativeai as genai
from PIL import Image
import hashlib
from functools import wraps


import qrcode
import io

app = Flask(__name__)
app.secret_key = "supersecretkey"  

def xhr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return render_template("index.html"), 403
        return f(*args, **kwargs)
    return decorated_function

DATA_FILE = 'users.json'

# Configuration
UPLOAD_FOLDER = 'static/uploads/artworks'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi', 'pdf'}
ARTWORKS_FILE = 'data/artworks.json'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_artworks():
    """Read artworks from JSON file"""
    if os.path.exists(ARTWORKS_FILE):
        with open(ARTWORKS_FILE, 'r') as f:
            return json.load(f)
    return []

def write_artworks(artworks):
    """Write artworks to JSON file"""
    with open(ARTWORKS_FILE, 'w') as f:
        json.dump(artworks, f, indent=4)


def generate(image_path, details_text):
    """
    Analyzes an image of an ornament and suggests a fair price.
    """
    try:
        # Configure the API key from environment variables
        api_key = "AIzaSyAlv3bdC2r3dAW7dL_5mZumkElQVXmN2Yk"
        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable not set.")
            return
        genai.configure(api_key=api_key)

        # Load the image
        img = Image.open(image_path)

        # Initialize the generative model
        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        # Create the prompt
        prompt_parts = [
            details_text,
            img,
            "\n\nSee the image and details, and suggest a fair price for the ornament based on recent Indian market trends, satisfying both the maker and supplier. dont ask any follow up questions. and just the price nothing else or any other text. The price should be in INR and rather than a range it should be a single value.The price should match the city trends and no price should be less than 1000 INR and go upto lakhs."
        ]

        # Generate content and stream the response
        response = model.generate_content(prompt_parts, stream=True)

        generated_price = ""
        for chunk in response:
            generated_price += chunk.text
        
        return generated_price.strip()

    except FileNotFoundError:
        print(f"Error: The file was not found at {image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")



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
        artworks = read_artworks()
        users = read_users()
        
        # Filter only published artworks
        published_artworks = [art for art in artworks if art.get('status') == 'published']
        
        # Transform artworks to product format for marketplace
        products = []
        for artwork in published_artworks:
            # Get artist information
            user = next((u for u in users if u['email'] == artwork['user_email']), None)
            artist_name = user['name'] if user else 'Anonymous Artisan'
            
            # Get artist location (you can add location field to user profile)
            location = user.get('location', 'India') if user else 'India'
            
            product = {
                'id': artwork['id'],
                'name': artwork['title'],
                'artist': artist_name,
                'category': artwork['category'],
                'price': artwork.get('price', 0) or 0,
                'image': f"/static/{artwork['files'][0]}" if artwork['files'] else 'https://via.placeholder.com/400x280/f9fafb/9ca3af?text=No+Image',
                'images': [f"/static/{file}" for file in artwork['files']],
                'location': location,
                'rating': 4.5,  # Default rating, you can implement actual rating system
                'reviews': artwork.get('views', 0),
                'authentic': True,
                'description': artwork['description'],
                'material': artwork['material'],
                'created_at': artwork['created_at'],
                'views': artwork.get('views', 0),
                'likes': artwork.get('likes', 0)
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
        artworks = read_artworks()
        users = read_users()
        
        # Find the artwork
        artwork = next((art for art in artworks if art['id'] == product_id), None)
        
        if not artwork:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get artist information
        user = next((u for u in users if u['email'] == artwork['user_email']), None)
        artist_name = user['name'] if user else 'Anonymous Artisan'
        location = user.get('location', 'India') if user else 'India'
        
        # Increment view count
        artwork['views'] = artwork.get('views', 0) + 1
        write_artworks(artworks)
        
        product = {
            'id': artwork['id'],
            'name': artwork['title'],
            'artist': artist_name,
            'artist_email': artwork['user_email'],
            'category': artwork['category'],
            'price': artwork.get('price', 0) or 0,
            'images': [f"/static/{file}" for file in artwork['files']],
            'location': location,
            'rating': 4.5,
            'reviews': artwork.get('views', 0),
            'authentic': True,
            'description': artwork['description'],
            'material': artwork['material'],
            'created_at': artwork['created_at'],
            'views': artwork.get('views', 0),
            'likes': artwork.get('likes', 0)
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
        artworks = read_artworks()
        
        # Find the artwork
        artwork = next((art for art in artworks if art['id'] == product_id), None)
        
        if not artwork:
            return jsonify({'error': 'Product not found'}), 404
        
        # Toggle like (simple implementation, you can make it user-specific)
        artwork['likes'] = artwork.get('likes', 0) + 1
        write_artworks(artworks)
        
        return jsonify({
            'success': True,
            'likes': artwork['likes']
        }), 200
        
    except Exception as e:
        print(f"Error liking product: {str(e)}")
        return jsonify({'error': 'Failed to like product'}), 500




@app.route("/community")
def community():
    return render_template("community.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/join")
def join():
    return render_template("join.html")

def read_users():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    users = read_users()
    
    if any(u['email'] == email for u in users):
        return jsonify({'success': False, 'message': 'Email already registered'})

    salt = os.urandom(16).hex()
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()

    users.append({
        'name': name,
        'email': email,
        'password': f"{salt}:{hashed_password}"
    })
    save_users(users)

    # Log the user in immediately after signup
    session['user_email'] = email

    return jsonify({'success': True, 'message': 'Account created successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    users = read_users()
    
    user = next((u for u in users if u['email'] == email), None)

    if user:
        stored_password_full = user.get('password', '')
        if ':' in stored_password_full:
            salt, stored_password_hash = stored_password_full.split(':', 1)
            hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
            if hashed_password == stored_password_hash:
                session['user_email'] = email
                return jsonify({'success': True, 'message': 'Login successful'})

    return jsonify({'success': False, 'message': 'Invalid email or password'})

@app.route('/api/upload-artwork', methods=['POST'])
def upload_artwork():
    """Handle artwork upload with images and metadata"""
    
    # Check if user is logged in
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    try:
        # Get form data
        title = request.form.get('title').title()
        category = request.form.get('category')

        # Correct and translate title and category
        corrected_title = correct_and_translate_text(title)
        corrected_category = correct_and_translate_text(category)

        material = request.form.get('material')
        description = request.form.get('description')
        price = request.form.get('price', '')
        
        
        # Validate required fields
        if not all([corrected_title, corrected_category, material, description]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        # Handle file uploads
        uploaded_files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    # Secure the filename
                    filename = secure_filename(file.filename)
                    
                    # Create unique filename with timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{filename}"
                    
                    # Save file
                    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file.save(filepath)
                    
                    # Store relative path for web access
                    uploaded_files.append(f'uploads/artworks/{unique_filename}')
        
        if not uploaded_files:
            return jsonify({'success': False, 'message': 'At least one file is required'}), 400
        
        # Create artwork object
        details_text = f"""
        Title: {corrected_title}
        Category: {corrected_category}
        Material: {material}
        Description: {description}
        """
        if not price:
            generated_price = generate(filepath, details_text)
            price = generated_price

        artwork = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'user_email': session['user_email'],
            'title': corrected_title,
            'category': corrected_category,
            'material': material,
            'description': description,
            'price': float(price) if price else None,
            'files': uploaded_files,
            'created_at': datetime.now().isoformat(),
            'status': 'published',
            'views': 0,
            'likes': 0
        }
        
        # Read existing artworks
        artworks = read_artworks()
        
        # Add new artwork
        artworks.append(artwork)
        
        # Save to file
        write_artworks(artworks)
        
        return jsonify({
            'success': True,
            'message': 'Artwork uploaded successfully!',
            'artwork': artwork
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
        artworks = read_artworks()
        user_email = session['user_email']
        
        # Filter artworks by user
        user_artworks = [art for art in artworks if art['user_email'] == user_email]
        
        return jsonify({
            'success': True,
            'artworks': user_artworks
        }), 200
        
    except Exception as e:
        print(f"Error fetching artworks: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@app.route('/api/delete-artwork/<artwork_id>', methods=['DELETE'])
@xhr_required
def delete_artwork(artwork_id):
    """Delete an artwork"""
    
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    try:
        artworks = read_artworks()
        user_email = session['user_email']
        
        # Find the artwork
        artwork = next((art for art in artworks if art['id'] == artwork_id and art['user_email'] == user_email), None)
        
        if not artwork:
            return jsonify({'success': False, 'message': 'Artwork not found'}), 404
        
        # Delete associated files
        for file_path in artwork['files']:
            full_path = os.path.join('static', file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        
        # Remove artwork from list
        artworks = [art for art in artworks if art['id'] != artwork_id]
        
        # Save updated list
        write_artworks(artworks)
        
        return jsonify({'success': True, 'message': 'Artwork deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error deleting artwork: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@app.route('/api/all-artworks', methods=['GET'])
def get_all_artworks():
    """Get all published artworks (for marketplace)"""
    
    try:
        artworks = read_artworks()
        
        # Only return published artworks
        published_artworks = [art for art in artworks if art.get('status') == 'published']
        
        return jsonify({
            'success': True,
            'artworks': published_artworks
        }), 200
        
    except Exception as e:
        print(f"Error fetching artworks: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

# Update your studio route
@app.route('/studio')
def studio():
    is_logged_in = 'user_email' in session
    user = None
    if is_logged_in:
        user_email = session['user_email']
        users = read_users()
        user = next((u for u in users if u['email'] == user_email), None)
    
    return render_template("studio.html", is_logged_in=is_logged_in, user=user)
    
@app.route('/api/check-auth')
@xhr_required
def check_auth():
    if 'user_email' in session:
        users = read_users()
        user = next((u for u in users if u['email'] == session['user_email']), None)
        return jsonify({'logged_in': True, 'user': user})
    return jsonify({'logged_in': False})

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('studio'))

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Render product detail page"""
    return render_template('product_detail.html', product_id=product_id)    

@app.route('/api/suggest-price', methods=['POST'])
@xhr_required
def suggest_price_route():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
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
            filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
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
        return jsonify({'success': False, 'message': 'An error occurred while suggesting price'}), 500

@app.route('/api/generate-qr/<artwork_id>')
def generate_qr_route(artwork_id):
    try:
        # Generate the URL for the product
        product_url = url_for('product_detail', product_id=artwork_id, _external=True)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(product_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#3E2723", back_color="#F5F0E8")
        
        # Save QR code to a bytes buffer
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')

    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while generating QR code'}), 500

@app.route('/api/ai-search', methods=['GET'])
def ai_search():
    query = request.args.get('query', '').lower()
    category = request.args.get('category', 'all').lower()

    artworks = read_artworks()
    users = read_users()

    if not query:
        return jsonify([])

    # Simulate AI-powered search with weighted scoring
    search_results = []
    for artwork in artworks:
        if artwork.get('status') != 'publ       ished':
            continue

        score = 0
        # Higher weight for title matches
        if query in artwork['title'].lower():
            score += 3
        # Medium weight for category and material matches
        if query in artwork['category'].lower():
            score += 2
        if query in artwork['material'].lower():
            score += 2
        # Lower weight for description matches
        if query in artwork['description'].lower():
            score += 1

        if score > 0:
            if category == 'all' or artwork['category'].lower() == category:
                user = next((u for u in users if u['email'] == artwork['user_email']), None)
                artist_name = user['name'] if user else 'Anonymous Artisan'
                location = user.get('location', 'India') if user else 'India'

                search_results.append({
                    'id': artwork['id'],
                    'name': artwork['title'],
                    'artist': artist_name,
                    'category': artwork['category'],
                    'price': artwork.get('price', 0) or 0,
                    'image': f"/static/{artwork['files'][0]}" if artwork['files'] else 'https://via.placeholder.com/400x280/f9fafb/9ca3af?text=No+Image',
                    'images': [f"/static/{file}" for file in artwork['files']],
                    'location': location,
                    'rating': 4.5,
                    'reviews': artwork.get('views', 0),
                    'authentic': True,
                    'description': artwork['description'],
                    'material': artwork['material'],
                    'created_at': artwork['created_at'],
                    'views': artwork.get('views', 0),
                    'likes': artwork.get('likes', 0),
                    'score': score
                })

    # Sort results by score
    search_results.sort(key=lambda x: x['score'], reverse=True)

    return jsonify(search_results)

def generate_description(image_path, title, category, material, existing_description=""):
    """
    Generates a description for an artwork using AI.
    """
    try:
        api_key = "AIzaSyAlv3bdC2r3dAW7dL_5mZumkElQVXmN2Yk"
        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable not set.")
            return "API key not configured."
        genai.configure(api_key=api_key)

        img = Image.open(image_path)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        if existing_description:
            prompt = f"""
            Enhance the following description for an artwork with the given details.
            Make it more evocative and appealing to potential buyers.
            Keep it concise and under 100 words.

            Title: {title}
            Category: {category}
            Material: {material}
            Existing Description: {existing_description}

            Enhanced Description:
            """
        else:
            prompt = f"""
            Write a compelling and brief description (under 80 words) for the following artwork.
            Focus on the visual elements, the craftsmanship, and the potential story behind the piece.
            The description should entice potential buyers and art enthusiasts. 
            The discription is for an ecommerce website made for tradition handicraft artisans and buyers so make the discription according to it only.

            Title: {title}
            Category: {category}
            Material: {material}

            Description:
            """

        response = model.generate_content([prompt, img])
        return response.text.strip()

    except Exception as e:
        print(f"An error occurred during description generation: {e}")
        return "Failed to generate description."

def correct_and_translate_text(text_to_correct):
    """
    Corrects spelling and translates text to English using Gemini AI.
    """
    try:
        # Configure the API key
        api_key = "AIzaSyAlv3bdC2r3dAW7dL_5mZumkElQVXmN2Yk"
        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable not set.")
            return text_to_correct # Return original text if API key is not set
        genai.configure(api_key=api_key)

        # Initialize the generative model
        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        # Create the prompt
        prompt = f"Correct the spelling of the following text. If the text is not in English, translate it to English. Do not add any extra information or change the meaning. Just provide the corrected and translated text. The text is: '{text_to_correct}'"

        # Generate content
        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception as e:
        print(f"An error occurred during text correction: {e}")
        return text_to_correct # Return original text in case of an error

@app.route('/api/generate-description', methods=['POST'])
@xhr_required
def generate_description_route():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401

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
            filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
            file.save(filepath)

            description = generate_description(filepath, title, category, material, existing_description)

            os.remove(filepath)

            return jsonify({'success': True, 'description': description})
        else:
            return jsonify({'success': False, 'message': 'File type not allowed'}), 400

    except Exception as e:
        print(f"Error in generate-description route: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while generating the description'}), 500

if __name__ == "__main__":
    app.run(debug=True)