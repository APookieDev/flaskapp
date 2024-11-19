from flask import Flask, request, jsonify, send_file
from PIL import Image
import numpy as np
import io
import easyocr

app = Flask(__name__)

reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader for English characters

@app.route('/square', methods=['GET'])
def square_number():
    number = request.args.get('number', type=int)
    
    if number is None:
        return jsonify({"error": "No number provided"}), 400
    
    square = number ** 2
    return jsonify({"number": number, "square": square}), 200

@app.route('/convert', methods=['POST'])
def convert_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    image_file = request.files['image']
    image = Image.open(image_file).convert('L')  # Convert to grayscale
    
    # Resize image to 120x40
    image = image.resize((120, 40))
    
    # Convert the image to a binary matrix (1 for black, 0 for white)
    binary_matrix = []
    threshold = 128  # Grayscale threshold for binary conversion
    
    for y in range(40):
        row = []
        for x in range(120):
            pixel_value = image.getpixel((x, y))
            row.append(1 if pixel_value < threshold else 0)
        binary_matrix.append(row)
    
    # Remove the horizontal line at line 23 without affecting text
    for x in range(120):
        if binary_matrix[23][x] == 1:
            if binary_matrix[22][x] == 0 and binary_matrix[24][x] == 0:
                binary_matrix[23][x] = 0  # Remove the line pixel
    
    # Remove the border of the image
    for x in range(120):
        binary_matrix[0][x] = 0  # Top border
        binary_matrix[39][x] = 0  # Bottom border

    for y in range(40):
        binary_matrix[y][0] = 0  # Left border
        binary_matrix[y][119] = 0  # Right border
    
    # Convert the binary matrix back to an image
    binary_image = Image.new('L', (120, 40))
    for y in range(40):
        for x in range(120):
            binary_image.putpixel((x, y), 0 if binary_matrix[y][x] == 1 else 255)
    
    # Use EasyOCR to extract text
    extracted_text = reader.readtext(np.array(binary_image), detail=0, allowlist='0123456789abcdef')
    
    if not extracted_text:
        return jsonify({"error": "Failed to extract text"}), 400
    
    # Get the first text prediction and sanitize it
    text = extracted_text[0].replace(" ", "")[:6]  # Ensure no spaces, and limit to 6 characters
    
    # Save the binary image to a BytesIO object with the extracted text as the filename
    img_io = io.BytesIO()
    binary_image.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name=f'{text}.png')

if __name__ == '__main__':
    app.run(debug=True, port=5454)
