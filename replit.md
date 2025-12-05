# StegoCrypt - Image Steganography Application

## Overview
StegoCrypt is a web application that allows users to hide secret messages inside images using LSB (Least Significant Bit) steganography. Users can encode text into images and later decode/extract the hidden messages.

## Project Structure
```
/
├── app.py              # Main Flask application with routes
├── steganography.py    # Core LSB steganography logic
├── templates/          # HTML templates
│   └── index.html      # Main page with encode/decode UI
├── static/             # Static assets
│   ├── css/
│   │   └── style.css   # Responsive styling
│   └── js/
│       └── main.js     # Client-side functionality
├── uploads/            # Temporary file storage
├── .gitignore          # Git ignore rules
└── replit.md           # This file
```

## Technologies Used

### Backend
- **Flask**: Lightweight Python web framework for handling HTTP requests
- **Pillow (PIL)**: Python imaging library for reading/writing image files
- **NumPy**: Efficient array operations for pixel manipulation

### Frontend
- **HTML5**: Semantic structure with form inputs for file upload
- **CSS3**: Modern responsive design with CSS variables
- **Vanilla JavaScript**: AJAX requests, drag-and-drop, file handling

### Steganography Technique
- **LSB (Least Significant Bit)**: Modifies the last bit of each RGB value
- Each pixel can hide 3 bits (1 per color channel)
- Changes are invisible to the human eye (1/256 difference)

## How to Run
```bash
python app.py
```
The server runs on http://0.0.0.0:5000

## API Endpoints
- `GET /` - Main page
- `POST /encode` - Hide text in image (multipart form: image + secret_text)
- `POST /decode` - Extract text from image (multipart form: image)
- `GET /download/<filename>` - Download encoded image

## Recent Changes
- December 5, 2025: Initial implementation with encode/decode functionality

## User Preferences
- None recorded yet
