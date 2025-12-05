"""
Steganography Module - LSB (Least Significant Bit) Implementation

WHY LSB STEGANOGRAPHY?
- LSB is the most common image steganography technique
- It modifies only the least significant bit of each color channel (RGB)
- Human eyes cannot detect changes in the least significant bit
- Provides good capacity: 3 bits per pixel (1 bit per RGB channel)

HOW IT WORKS:
1. ENCODING: Convert text to binary, then replace the LSB of each color value
   with one bit of the message. A delimiter marks the end of the message.
2. DECODING: Read the LSB of each color value, reconstruct the binary string,
   convert back to text until the delimiter is found.
"""

import numpy as np
from PIL import Image
import os


class Steganography:
    """
    LSB Steganography class for hiding and extracting text in images.
    
    WHY USE A CLASS?
    - Encapsulates all steganography logic in one place
    - Makes code reusable and testable
    - Allows for easy extension with new methods
    """
    
    DELIMITER = "<<END>>"
    
    def __init__(self):
        pass
    
    def _text_to_binary(self, text):
        """
        Convert text string to binary representation.
        
        WHY THIS CONVERSION?
        - Computers store everything in binary (0s and 1s)
        - Each character is converted to its 8-bit ASCII/UTF-8 representation
        - This binary data will be hidden in image pixels
        
        Example: 'A' -> '01000001'
        """
        binary = ''.join(format(ord(char), '08b') for char in text)
        return binary
    
    def _binary_to_text(self, binary):
        """
        Convert binary string back to text.
        
        WHY?
        - Reverses the encoding process during extraction
        - Groups 8 bits together to form each character
        """
        text = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        return text
    
    def get_max_capacity(self, image_path):
        """
        Calculate maximum number of characters that can be hidden.
        
        WHY CALCULATE CAPACITY?
        - Prevents errors from trying to hide too much data
        - Helps users know the limits before encoding
        
        FORMULA:
        - Each pixel has 3 color channels (RGB)
        - Each channel can hide 1 bit
        - So each pixel hides 3 bits
        - 1 character = 8 bits, so we need ~2.67 pixels per character
        """
        try:
            img = Image.open(image_path)
            width, height = img.size
            total_pixels = width * height
            total_bits = total_pixels * 3
            delimiter_bits = len(self.DELIMITER) * 8
            available_bits = total_bits - delimiter_bits
            max_chars = available_bits // 8
            return max_chars
        except Exception as e:
            return 0
    
    def encode(self, image_path, secret_text, output_path):
        """
        Hide secret text inside an image using LSB steganography.
        
        WHY LSB (Least Significant Bit)?
        - The LSB contributes least to the color value (only 1 out of 256)
        - Changing it causes imperceptible visual difference
        - Example: RGB(255,255,255) vs RGB(254,254,254) looks identical
        
        PROCESS:
        1. Load image as numpy array (efficient pixel manipulation)
        2. Flatten the array to process pixels sequentially
        3. Convert text + delimiter to binary
        4. Replace LSB of each color value with message bit
        5. Reshape and save as PNG (lossless format)
        
        WHY PNG OUTPUT?
        - PNG is lossless compression (preserves exact pixel values)
        - JPG is lossy and would destroy the hidden data
        """
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            img_array = np.array(img)
            original_shape = img_array.shape
            flat_array = img_array.flatten()
            
            secret_text_with_delimiter = secret_text + self.DELIMITER
            binary_secret = self._text_to_binary(secret_text_with_delimiter)
            
            if len(binary_secret) > len(flat_array):
                return False, "Error: Image too small to hide this message. Try a larger image or shorter text."
            
            for i, bit in enumerate(binary_secret):
                flat_array[i] = (flat_array[i] & 0xFE) | int(bit)
            
            encoded_array = flat_array.reshape(original_shape)
            encoded_img = Image.fromarray(encoded_array.astype('uint8'))
            
            encoded_img.save(output_path, 'PNG')
            
            return True, "Message successfully hidden in image!"
            
        except Exception as e:
            return False, f"Error during encoding: {str(e)}"
    
    def decode(self, image_path):
        """
        Extract hidden text from a steganography image.
        
        PROCESS:
        1. Load image and convert to numpy array
        2. Extract LSB from each color value
        3. Group bits into bytes (8 bits = 1 character)
        4. Convert to text until delimiter is found
        5. Return the extracted message
        
        WHY CHECK FOR DELIMITER?
        - We don't know how long the hidden message is
        - The delimiter marks where the message ends
        - Without it, we'd get garbage data from unused pixels
        """
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            img_array = np.array(img)
            flat_array = img_array.flatten()
            
            binary_message = ''
            extracted_text = ''
            
            for i, value in enumerate(flat_array):
                binary_message += str(value & 1)
                
                if len(binary_message) >= 8 and len(binary_message) % 8 == 0:
                    extracted_text = self._binary_to_text(binary_message)
                    
                    if self.DELIMITER in extracted_text:
                        message = extracted_text.split(self.DELIMITER)[0]
                        return True, message
            
            return False, "No hidden message found in this image. Make sure you're using an image that was encoded with this tool."
            
        except Exception as e:
            return False, f"Error during decoding: {str(e)}"
