def run_server(callback_function):

    from flask import Flask, render_template, request, jsonify
    import time

    app = Flask(__name__)

    # Define a list to store order list data
    order_list = []
    print("test")

    @app.route('/current_time')
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


    @app.route('/receive_order_list', methods=['POST'])
    def receive_order_list():
        order_list_data = request.json

        for order in order_list_data:
            for element in order:
                if element == "black":
                    element = 0
                elif element == "white":
                    element = 1
                elif element == "blue":
                    element = 2

        callback_function(order_list_data)
        # Process the order list data as needed
        print(order_list_data)
        return jsonify({'message': 'Data received successfully'})

    #if __name__ == '__main__':

    app.run(host="0.0.0.0", port=80)
