from GUI.Utility_and_Test.post_script import post_status
import time
import subprocess

# Define the initial status

subprocess.Popen(['python', 'GUI/app_2.py'])

while True:
    user_input = input("Enter a status: ")
    post_status(user_input)
