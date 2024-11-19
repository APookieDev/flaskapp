from flask import Flask, request, jsonify, send_file
from PIL import Image
import numpy as np
import io
import re
import easyocr

app = Flask(__name__)
reader = easyocr.Reader(['en'], gpu=False)

# Route to convert the image to a binary matrix, clean it, and extract text
@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    image_file = request.files['image']
    image = Image.open(image_file).convert('L')
    
    # Resize the image to 120x40
    image = image.resize((120, 40))
    
    # Convert the image to a binary matrix
    threshold = 128
    binary_matrix = np.array([[1 if image.getpixel((x, y)) < threshold else 0 for x in range(120)] for y in range(40)])
    
    # Remove the horizontal line at row 23 without affecting text
    for x in range(120):
        if binary_matrix[23, x] == 1 and binary_matrix[22, x] == 0 and binary_matrix[24, x] == 0:
            binary_matrix[23, x] = 0
    
    # Remove the border of the image
    binary_matrix = binary_matrix[1:-1, 1:-1]
    
    # Convert the cleaned binary matrix back to an image
    cleaned_image = Image.fromarray((binary_matrix * 255).astype('uint8'))
    
    # Extract text using EasyOCR
    extracted_text = reader.readtext(np.array(cleaned_image), detail=0)
    
    # Ensure text contains only a-f and 0-9, is 4-6 characters long, and has no spaces
    if extracted_text:
        extracted_text = re.sub(r'[^a-f0-9]', '', extracted_text[0].lower())
        if len(extracted_text) < 4 or len(extracted_text) > 6:
            extracted_text = "invalid"
    else:
        extracted_text = "invalid"
    
    # Save the cleaned image with the extracted text as the filename
    filename = f"{extracted_text}.png"
    image_io = io.BytesIO()
    cleaned_image.save(image_io, format='PNG')
    image_io.seek(0)
    
    return send_file(image_io, mimetype='image/png', as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)
