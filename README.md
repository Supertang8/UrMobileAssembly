Det her er vores P2 projekt

Medlemmer:
Jacob,
Simon,
Nina,
Vithuran,
Jonas

Vi bruger RTDE til at komunikere med UR5 robotten

Vores GUI et en webside som bliver kørt som en python flask app

Held og lykke

--How to run program on UR5--
    Make sure ROBOT_HOST in code.py is the same as the robot's IP address.
    Transfer rtde_control_loop.urp to the robot using magic upload file and a USB. Run the program.
    Open the folder Ur_Code in integrated terminal, enter the virtual environment then run: python code.py

--How to enter virtual environment--: 
First enter the Ur_Code folder in the terminal.

    WINDOWS: Set-ExecutionPolicy Unrestricted -Scope Process
    WINDOWS: .venv\Scripts\activate

    raspberryPI: source .venv/Scripts/activate
