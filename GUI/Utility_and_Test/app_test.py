import GUI.run_server as run_server
import threading
import time

order_list_data = []

def change_global_variable(list):
    global order_list_data
    order_list_data = list

def run_flask():
    run_server.run_server(change_global_variable)

def print_test():
    while True:
        print(order_list_data)
        time.sleep(1)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    print_thread = threading.Thread(target=print_test)

    flask_thread.start()
    print_thread.start()
