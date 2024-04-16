from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Define a list to store order list data
order_list = []
print("test")

# Route to render the index.html template
@app.route('/')
def index():
    return render_template('index.html', order_list=order_list)

@app.route('/receive_order_list', methods=['POST'])
def receive_order_list():
    order_list_data = request.json
    # Process the order list data as needed
    print(order_list_data)
    return jsonify({'message': 'Data received successfully'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)