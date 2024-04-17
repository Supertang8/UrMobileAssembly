import requests
import time

# Define the URL of the endpoint
url = 'http://127.0.0.1/status'

# Define the data you want to send
status = "running"
data = {"message": status}

# Define the interval in seconds
interval = 1

while True:
    try:
        # Send the POST request with JSON data
        response = requests.post(url, json=data)

        # Check the response status
        if response.status_code == 200:
            print("POST request successful.")
        else:
            print(f"POST request failed with status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Pause execution for the defined interval
    time.sleep(interval)
