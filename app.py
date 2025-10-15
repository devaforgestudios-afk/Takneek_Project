from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os 
from datetime import datetime
from werkzeug.utils import secure_filename
import google.generativeai as genai
from PIL import Image


app = Flask(__name__)
app.secret_key = "supersecretkey"  

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
            "\n\nSee the image and details, and suggest a fair price for the ornament based on recent Indian market trends, satisfying both the maker and supplier. dont ask any follow up questions. and just the price nothing else or any other text. The price should be in INR and rather than a range it should be a single value."
        ]

        # Generate content and stream the response
        response = model.generate_content(prompt_parts, stream=True)

        print("--- AI Generated Output ---")
        for chunk in response:
            print(chunk.text, end="")
        print("\n--------------------------")

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

    users.append({
        'name': name,
        'email': email,
        'password': password
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
    
    user = next((u for u in users if u['email'] == email and u['password'] == password), None)

    if user:
        session['user_email'] = email
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'})

@app.route('/api/upload-artwork', methods=['POST'])
def upload_artwork():
    """Handle artwork upload with images and metadata"""
    
    # Check if user is logged in
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    try:
        # Get form data
        title = request.form.get('title')
        title = title.title()
        category = request.form.get('category')
        material = request.form.get('material')
        description = request.form.get('description')
        price = request.form.get('price', '')
        
        # Validate required fields
        if not all([title, category, material, description]):
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
        artwork = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'user_email': session['user_email'],
            'title': title,
            'category': category,
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

if __name__ == "__main__":
    app.run(debug=True)