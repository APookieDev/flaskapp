from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import io

app = Flask(__name__)

@app.route('/square', methods=['GET'])
def square_number():
    # Get the number from the request arguments
    number = request.args.get('number', type=int)
    
    if number is None:
        return jsonify({"error": "No number provided"}), 400
    
    # Calculate the square of the number
    square = number ** 2
    
    # Return the result as a JSON response
    return jsonify({"number": number, "square": square}), 200

@app.route('/convert', methods=['POST'])
def convert_image_to_binary_matrix():
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400

    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Open image using PIL
        image = Image.open(image_file).convert('L')  # Convert image to grayscale

        # Resize image to 120x40
        image = image.resize((120, 40))

        # Convert the image to a binary matrix
        threshold = 128  # Threshold for binarization
        binary_matrix = []

        for y in range(40):
            row = []
            for x in range(120):
                pixel_value = image.getpixel((x, y))
                # Convert to 1 if black (below threshold), otherwise 0 (white)
                row.append(1 if pixel_value < threshold else 0)
            binary_matrix.append(row)

        # Return the binary matrix as a JSON response
        return jsonify({"binary_matrix": binary_matrix}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
