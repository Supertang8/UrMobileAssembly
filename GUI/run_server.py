def run_server(callback_function):

    from flask import Flask, render_template, request, jsonify
    import time

    app = Flask(__name__)   
    status = "Assembling your order"

    # Define a list to store order list data
    order_list = []
    #print("test")

    def current_time():
        timestamp = time.time()
        formatted_time = time.strftime('%H:%M:%S', time.localtime(timestamp)) + f":{int((timestamp % 1) * 1000):03d}"
        return jsonify({'current_time': formatted_time})
    

    # Route to render the index.html template
    @app.route('/')
    def index():
        return render_template('index.html')

    # Route to render the waiting_on_robot.html template
    @app.route('/waiting_on_robot')
    def waitingRobot():
        return render_template('waitingRobot.html')

    @app.route('/status', methods=['GET', 'POST'])
    def status_get():
        
        nonlocal status

        if request.method == "GET":
            return jsonify({'status': status})
        
        if request.method == "POST":
            #print("POST request received")
            json_data = request.json
            status = json_data.get('message')  # Extracting the value associated with the key 'message'
            #print("Received status:", status)
            return jsonify({'status': "ok"})

    @app.route('/receive_order_list', methods=['POST'])
    def receive_order_list():
        order_list_data = request.json
        new_order_list = []
        for order in order_list_data:
            new_order = []
            new_order.append(int(order[3]))

            if order[2] == "black":
                new_order.append(0)
            elif order[2] == "white":
                new_order.append(1)
            else:
                new_order.append(2)
            
            if order[1] == "black":
                new_order.append(0)
            elif order[1] == "white":
                new_order.append(1)
            else:
                new_order.append(2)
            
            new_order_list.append(new_order)

        callback_function(new_order_list)
        # Process the order list data as needed
        #print(new_order_list)
        return jsonify({'message': 'Data received successfully'})

    #if __name__ == '__main__':

    app.run(host="0.0.0.0", port=80, debug=False)
