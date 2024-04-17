import requests
import time

# Define the URL of the endpoint
url = 'http://127.0.0.1/status'

# Define the initial status
status = "idle"
# Define the interval in seconds
interval = 1

while True:
    try:
        # Take user input for status
        new_status = input("Enter the new status: ")

        # Update the status if user input is not empty
        if new_status.strip():
            status = new_status.strip()

        # Define the data you want to send
        data = {"message": status}

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
