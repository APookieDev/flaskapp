from flask import Flask, request, jsonify

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

if __name__ == '__main__':
    app.run(debug=True)
