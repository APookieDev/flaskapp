from flask import Flask, request, jsonify, send_file
from PIL import Image
import numpy as np
import io

app = Flask(__name__)

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
    # Top and bottom borders
    for x in range(120):
        binary_matrix[0][x] = 0  # Top border
        binary_matrix[39][x] = 0  # Bottom border

    # Left and right borders
    for y in range(40):
        binary_matrix[y][0] = 0  # Left border
        binary_matrix[y][119] = 0  # Right border
    
    # Convert the binary matrix back to an image
    binary_image = Image.new('L', (120, 40))
    for y in range(40):
        for x in range(120):
            binary_image.putpixel((x, y), 0 if binary_matrix[y][x] == 1 else 255)
    
    # Save the binary image to a BytesIO object
    img_io = io.BytesIO()
    binary_image.save(img_io, 'PNG')
    img_io.seek(0)  # Rewind the BytesIO object to the beginning
    
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='cleaned_image.png')

if __name__ == '__main__':
    app.run(debug=True, port=5454)
