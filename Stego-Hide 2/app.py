"""
Flask Application for Image Steganography

WHY FLASK?
- Lightweight and minimal: Perfect for this focused application
- Easy to learn and deploy: Great documentation and community
- Built-in development server: Quick testing during development
- Werkzeug: Secure file upload handling included
- Jinja2: Powerful templating for HTML rendering
- Production-ready with Gunicorn/uWSGI for deployment

PROJECT STRUCTURE EXPLANATION:
/
├── app.py              # Main Flask application (this file)
├── steganography.py    # Core steganography logic (separation of concerns)
├── templates/          # HTML templates (Flask convention)
│   └── index.html      # Main page template
├── static/             # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css   # Styling
│   └── js/
│       └── main.js     # Client-side functionality
└── uploads/            # Temporary file storage

WHY THIS STRUCTURE?
- Follows Flask conventions for easy deployment
- Separates concerns: logic, presentation, styling
- Easy to maintain and extend
- Compatible with all Flask hosting platforms
"""

import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from steganography import Steganography
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

stego = Steganography()


def allowed_file(filename):
    """
    Check if uploaded file has an allowed extension.
    
    WHY THIS CHECK?
    - Security: Prevents uploading malicious file types
    - Functionality: Only image files work with steganography
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename):
    """
    Generate a unique filename to prevent overwrites.
    
    WHY UUID?
    - Prevents filename collisions
    - Adds security by obscuring original filenames
    - Allows multiple users to upload files simultaneously
    """
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_id = str(uuid.uuid4())[:8]
    return f"{unique_id}.{ext}"


@app.route('/')
def index():
    """
    Serve the main page.
    
    WHY SEPARATE TEMPLATE?
    - Separation of concerns: HTML in templates folder
    - Easier to maintain and modify the UI
    - Flask's Jinja2 templating provides powerful features
    """
    return render_template('index.html')


@app.route('/encode', methods=['POST'])
def encode():
    """
    API endpoint to hide text in an image.
    
    WHY POST METHOD?
    - POST is used for data submission
    - Allows sending files in the request body
    - More secure than GET for sensitive data
    
    PROCESS:
    1. Validate file upload
    2. Validate secret text
    3. Save uploaded file temporarily
    4. Perform steganography encoding
    5. Return encoded image path for download
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image file provided'}), 400
    
    file = request.files['image']
    secret_text = request.form.get('secret_text', '')
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not secret_text:
        return jsonify({'success': False, 'message': 'No secret text provided'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file type. Please use PNG or JPG images.'}), 400
    
    unique_filename = generate_unique_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"input_{unique_filename}")
    output_filename = f"encoded_{unique_filename.rsplit('.', 1)[0]}.png"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    file.save(input_path)
    
    max_capacity = stego.get_max_capacity(input_path)
    if len(secret_text) > max_capacity:
        os.remove(input_path)
        return jsonify({
            'success': False, 
            'message': f'Text too long! This image can hide up to {max_capacity} characters. Your text has {len(secret_text)} characters.'
        }), 400
    
    success, message = stego.encode(input_path, secret_text, output_path)
    
    try:
        os.remove(input_path)
    except:
        pass
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'download_url': f'/download/{output_filename}'
        })
    else:
        return jsonify({'success': False, 'message': message}), 400


@app.route('/decode', methods=['POST'])
def decode():
    """
    API endpoint to extract hidden text from an image.
    
    PROCESS:
    1. Validate file upload
    2. Save uploaded file temporarily
    3. Perform steganography decoding
    4. Return extracted message
    5. Clean up temporary file
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file type. Please use PNG or JPG images.'}), 400
    
    unique_filename = generate_unique_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"decode_{unique_filename}")
    
    file.save(input_path)
    
    success, message = stego.decode(input_path)
    
    try:
        os.remove(input_path)
    except:
        pass
    
    return jsonify({
        'success': success,
        'message': message if not success else 'Hidden message extracted successfully!',
        'extracted_text': message if success else None
    })


@app.route('/download/<filename>')
def download(filename):
    """
    Serve encoded image for download.
    
    WHY SEPARATE DOWNLOAD ENDPOINT?
    - Allows the encoded image to be downloaded after processing
    - send_file handles proper MIME types and headers
    - as_attachment triggers browser download dialog
    
    SECURITY:
    - Uses secure_filename to sanitize input
    - Validates file stays within uploads directory (prevents path traversal)
    - Only allows files that start with 'encoded_' prefix
    """
    safe_filename = secure_filename(filename)
    
    if not safe_filename or not safe_filename.startswith('encoded_'):
        return jsonify({'success': False, 'message': 'Invalid filename'}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    
    real_path = os.path.realpath(file_path)
    upload_dir = os.path.realpath(app.config['UPLOAD_FOLDER'])
    if not real_path.startswith(upload_dir + os.sep):
        return jsonify({'success': False, 'message': 'Invalid file path'}), 400
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': 'File not found'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=safe_filename
    )


@app.after_request
def add_cache_headers(response):
    """
    Add cache control headers to prevent caching issues.
    
    WHY DISABLE CACHING?
    - Ensures users always see the latest version
    - Prevents stale data issues in iframes
    - Important for dynamic content
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
