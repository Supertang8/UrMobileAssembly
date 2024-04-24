import requests

# Define the URL of the endpoint
# url = 'http://192.168.0.90/status'
url = 'http://http://127.0.0.1/status'

def post_status(status):
    # Define the data you want to send
    data = {"message": status}

    # Send the POST request with JSON data
    response = requests.post(url, json=data)

    # Check the response status
    if response.status_code == 200:
        print("POST request successful.")
    else:
        print(f"POST request failed with status code: {response.status_code}")

