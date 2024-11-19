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
    
    # Convert the binary matrix back to an image
    binary_image = Image.new('L', (120, 40))
    for y in range(40):
        for x in range(120):
            binary_image.putpixel((x, y), 0 if binary_matrix[y][x] == 1 else 255)
    
    # Save the binary image to a BytesIO object
    img_io = io.BytesIO()
    binary_image.save(img_io, 'PNG')
    img_io.seek(0)  # Rewind the BytesIO object to the beginning
    
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='converted_image.png')

if __name__ == '__main__':
    app.run(debug=True, port=5454)
