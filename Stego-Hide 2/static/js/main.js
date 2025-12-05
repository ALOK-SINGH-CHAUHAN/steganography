/**
 * JAVASCRIPT FOR STEGOCRYPT
 * 
 * WHY VANILLA JAVASCRIPT?
 * - No framework overhead (React, Vue, etc.)
 * - Faster load times for this simple application
 * - Easy to understand and maintain
 * - Full browser compatibility
 * 
 * FUNCTIONALITY:
 * 1. Tab switching between Encode/Decode
 * 2. Drag & drop file upload
 * 3. File preview with image thumbnail
 * 4. Form submission via AJAX (no page refresh)
 * 5. Results display and download handling
 * 6. Copy to clipboard functionality
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initTabs();
    initEncodeForm();
    initDecodeForm();
    initCharCounter();
});

/**
 * TAB SWITCHING FUNCTIONALITY
 * 
 * WHY TABS?
 * - Separates encode and decode into distinct sections
 * - Cleaner UX than showing both at once
 * - Users typically do one operation at a time
 */
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const tabId = button.dataset.tab;
            document.getElementById(tabId).classList.add('active');
        });
    });
}

/**
 * ENCODE FORM FUNCTIONALITY
 * 
 * Handles:
 * - Image upload with drag & drop
 * - Image preview
 * - Form submission to /encode endpoint
 * - Result/error display
 */
function initEncodeForm() {
    const uploadArea = document.getElementById('encode-upload-area');
    const fileInput = document.getElementById('encode-image');
    const preview = document.getElementById('encode-preview');
    const previewImg = document.getElementById('encode-preview-img');
    const filenameText = document.getElementById('encode-filename');
    const removeBtn = document.getElementById('encode-remove');
    const form = document.getElementById('encode-form');
    const submitBtn = document.getElementById('encode-btn');
    
    // Initialize drag & drop
    initDragAndDrop(uploadArea, fileInput, preview, previewImg, filenameText);
    
    // Remove button handler
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUpload(fileInput, preview, uploadArea);
    });
    
    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validate inputs
        if (!fileInput.files[0]) {
            showError('encode', 'Please select an image file.');
            return;
        }
        
        const secretText = document.getElementById('secret-text').value.trim();
        if (!secretText) {
            showError('encode', 'Please enter a secret message.');
            return;
        }
        
        // Show loading state
        setButtonLoading(submitBtn, true);
        hideResults('encode');
        
        // Prepare form data
        const formData = new FormData();
        formData.append('image', fileInput.files[0]);
        formData.append('secret_text', secretText);
        
        try {
            // Send request to server
            const response = await fetch('/encode', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                showEncodeSuccess(data.message, data.download_url);
            } else {
                showError('encode', data.message);
            }
        } catch (error) {
            showError('encode', 'An error occurred. Please try again.');
            console.error('Encode error:', error);
        } finally {
            setButtonLoading(submitBtn, false);
        }
    });
}

/**
 * DECODE FORM FUNCTIONALITY
 * 
 * Handles:
 * - Image upload with drag & drop
 * - Image preview
 * - Form submission to /decode endpoint
 * - Extracted text display
 */
function initDecodeForm() {
    const uploadArea = document.getElementById('decode-upload-area');
    const fileInput = document.getElementById('decode-image');
    const preview = document.getElementById('decode-preview');
    const previewImg = document.getElementById('decode-preview-img');
    const filenameText = document.getElementById('decode-filename');
    const removeBtn = document.getElementById('decode-remove');
    const form = document.getElementById('decode-form');
    const submitBtn = document.getElementById('decode-btn');
    
    // Initialize drag & drop
    initDragAndDrop(uploadArea, fileInput, preview, previewImg, filenameText);
    
    // Remove button handler
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUpload(fileInput, preview, uploadArea);
    });
    
    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validate inputs
        if (!fileInput.files[0]) {
            showError('decode', 'Please select an encoded image file.');
            return;
        }
        
        // Show loading state
        setButtonLoading(submitBtn, true);
        hideResults('decode');
        
        // Prepare form data
        const formData = new FormData();
        formData.append('image', fileInput.files[0]);
        
        try {
            // Send request to server
            const response = await fetch('/decode', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                showDecodeSuccess(data.extracted_text);
            } else {
                showError('decode', data.message);
            }
        } catch (error) {
            showError('decode', 'An error occurred. Please try again.');
            console.error('Decode error:', error);
        } finally {
            setButtonLoading(submitBtn, false);
        }
    });
    
    // Copy button handler
    document.getElementById('copy-btn').addEventListener('click', () => {
        const extractedText = document.getElementById('extracted-text').textContent;
        navigator.clipboard.writeText(extractedText).then(() => {
            const copyBtn = document.getElementById('copy-btn');
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        });
    });
}

/**
 * DRAG & DROP FUNCTIONALITY
 * 
 * WHY DRAG & DROP?
 * - Modern, intuitive interface
 * - Faster than clicking through dialogs
 * - Provides visual feedback
 */
function initDragAndDrop(uploadArea, fileInput, preview, previewImg, filenameText) {
    // Click to upload
    uploadArea.addEventListener('click', () => {
        if (!preview.style.display || preview.style.display === 'none') {
            fileInput.click();
        }
    });
    
    // File selected via input
    fileInput.addEventListener('change', () => {
        handleFileSelect(fileInput.files[0], preview, previewImg, filenameText, uploadArea);
    });
    
    // Drag events
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.add('dragover');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.remove('dragover');
        });
    });
    
    // Handle drop
    uploadArea.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        if (file && isValidImageFile(file)) {
            // Update the file input
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            
            handleFileSelect(file, preview, previewImg, filenameText, uploadArea);
        }
    });
}

/**
 * Handle file selection - show preview
 */
function handleFileSelect(file, preview, previewImg, filenameText, uploadArea) {
    if (!file) return;
    
    if (!isValidImageFile(file)) {
        alert('Please select a valid image file (PNG or JPG).');
        return;
    }
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        filenameText.textContent = file.name;
        preview.style.display = 'flex';
        uploadArea.querySelector('.upload-content').style.display = 'none';
    };
    reader.readAsDataURL(file);
}

/**
 * Check if file is a valid image
 */
function isValidImageFile(file) {
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    return validTypes.includes(file.type);
}

/**
 * Reset upload area to initial state
 */
function resetUpload(fileInput, preview, uploadArea) {
    fileInput.value = '';
    preview.style.display = 'none';
    uploadArea.querySelector('.upload-content').style.display = 'block';
}

/**
 * CHARACTER COUNTER
 * 
 * WHY?
 * - Helps users know how much text they're adding
 * - Image capacity limits how much can be hidden
 */
function initCharCounter() {
    const textarea = document.getElementById('secret-text');
    const counter = document.getElementById('char-counter');
    
    textarea.addEventListener('input', () => {
        counter.textContent = textarea.value.length;
    });
}

/**
 * Show/hide loading state on buttons
 */
function setButtonLoading(button, isLoading) {
    const btnText = button.querySelector('.btn-text');
    const btnLoading = button.querySelector('.btn-loading');
    
    if (isLoading) {
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
        button.disabled = true;
    } else {
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        button.disabled = false;
    }
}

/**
 * Hide all result areas for a section
 */
function hideResults(section) {
    document.getElementById(`${section}-result`).style.display = 'none';
    document.getElementById(`${section}-error`).style.display = 'none';
}

/**
 * Show encode success result
 */
function showEncodeSuccess(message, downloadUrl) {
    const resultArea = document.getElementById('encode-result');
    const messageEl = document.getElementById('encode-message');
    const downloadLink = document.getElementById('download-link');
    
    messageEl.textContent = message;
    downloadLink.href = downloadUrl;
    resultArea.style.display = 'block';
}

/**
 * Show decode success result
 */
function showDecodeSuccess(extractedText) {
    const resultArea = document.getElementById('decode-result');
    const textEl = document.getElementById('extracted-text');
    
    textEl.textContent = extractedText;
    resultArea.style.display = 'block';
}

/**
 * Show error message
 */
function showError(section, message) {
    const errorArea = document.getElementById(`${section}-error`);
    const messageEl = document.getElementById(`${section}-error-message`);
    
    messageEl.textContent = message;
    errorArea.style.display = 'block';
}
