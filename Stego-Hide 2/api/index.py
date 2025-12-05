"""
Flask Application for Image Steganography - Vercel Serverless Version
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from steganography import Steganography

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

stego = Steganography()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename):
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_id = str(uuid.uuid4())[:8]
    return f"{unique_id}.{ext}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/encode', methods=['POST'])
def encode():
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
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
