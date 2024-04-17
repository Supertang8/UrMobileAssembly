# ---------- Import libraries and data from other script(s) ---------- #
import sys

sys.path.append("..")
#import logging

import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
import time
#import keyboard
import threading
import requests
from ..GUI import run_server

#from TestingCode import rx, ry, rz
from find_positions import top_cover_pos, top_cover_approach, bottom_cover_pos, bottom_cover_approach, fuse_pos, fuse_approach, pcb_pos, pcb_approach, bottom_cover_drop, fixture_test_pos

# ---------- configure robot & communications ---------- #
# logging.basicConfig(level=logging.INFO)
ROBOT_HOST = "192.168.0.104"
ROBOT_PORT = 30004
config_filename = "control_loop_configuration.xml"

power_log_file = open("power_log.txt", 'w')

#logging.getLogger().setLevel(logging.INFO)

conf = rtde_config.ConfigFile(config_filename)
state_names, state_types = conf.get_recipe("state")
setp_names, setp_types = conf.get_recipe("setp")
watchdog_names, watchdog_types = conf.get_recipe("watchdog")
gripper_names, gripper_types = conf.get_recipe("gripper")

con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
con.connect()

#Get controller version
con.get_controller_version()

#Setup recipes
con.send_output_setup(state_names, state_types)
setp = con.send_input_setup(setp_names, setp_types)
watchdog = con.send_input_setup(watchdog_names, watchdog_types)
gripper = con.send_input_setup(gripper_names, gripper_types)

end_pos = [0.164, -0.400, 0.072, 3.131, 0, 0]

setp.input_double_register_0 = 0
setp.input_double_register_1 = 0
setp.input_double_register_2 = 0
setp.input_double_register_3 = 0
setp.input_double_register_4 = 0
setp.input_double_register_5 = 0

gripper.standard_digital_output = 0
gripper.standard_digital_output_mask = 0

#The function "rtde_set_watchdog" in the "rtde_control_loop.urp" creates a 1 Hz watchdog
watchdog.input_int_register_0 = 0

# ---------- GUI server ---------- #

#function for running GUI script.
def run_gui_script():
    run_server.run_server(get_order_data) #Send the callback function get_order_data as an argument, which can then be run by the run_server script.

#start a thread running run_gui_script() in parallel with this script. 
gui_thread = threading.thread(target=run_gui_script)

#Get orders from running script.
orders = []
def get_order_data(order_data):
    global orders
    orders = order_data

# ---------- utility functions ---------- #
def setp_to_list(sp):
    sp_list = []
    for i in range(0, 6):
        sp_list.append(sp.__dict__["input_double_register_%i" % i])
    return sp_list

def list_to_setp(sp, list):
    for i in range(0, 6):
        sp.__dict__["input_double_register_%i" % i] = list[i]
    return sp

def order_to_queue(order):
    queue = []

    if order[0] != 0: #if the order contains at least one fuse
        queue.append(fuse_approach[order[0]-1])
        queue.append(fuse_pos[order[0]-1])
        queue.append("s") #small suction cup
        queue.append(fuse_approach[order[0]-1])

    queue.append(pcb_approach)
    queue.append(pcb_pos)
    queue.append("l") #large suction cup
    queue.append(pcb_approach)
    queue.append(bottom_cover_approach[order[1]])
    queue.append(bottom_cover_drop[order[1]])
    queue.append("r") #release
    queue.append(bottom_cover_approach[order[1]])
    queue.append(top_cover_approach[order[2]])
    queue.append(top_cover_pos[order[2]])
    queue.append("l") #large suction cup
    queue.append(top_cover_approach[order[2]])
    queue.append(bottom_cover_approach[order[1]])
    queue.append(bottom_cover_pos[order[1]])
    queue.append(bottom_cover_approach[order[1]])

    #End pos
    queue.append(end_pos)
    queue.append("r") #release

    return queue

# ---------- controlling end-effector ---------- #
def grab(id): # 0=close, 1=small, 2=large
    gripper.standard_digital_output_mask = 0b01111000 #Mask the 4 digital outputs we are changing.
    if(id == 2): 
        #Start large suction, set digital output 6 to HIGH
        gripper.standard_digital_output = 0b00100000 
    elif(id == 1): 
        #Start small suction, set digital output 8 to HIGH
        gripper.standard_digital_output = 0b10000000 
    else:
        ##Stop all suction, set digital output 5 and 7 to HIGH
        gripper.standard_digital_output = 0b01010000 
    con.send(gripper)

# ---------- startup ---------- #
#Init variables
paused = True
order_completed = False
move_completed = True
current_task = 0
current_order = 0

power_log_file.write('Time[s] Voltage[V] Current[A] Power[W]\n')

#Start data synchronization
if not con.send_start():
    sys.exit()

# ---------- control loop ---------- #
while True:
    #Get current state
    state = con.receive()
    if state is None:
        break
    
    #Print State
    if paused:
        message = "Idle"
    else:
        message = "Running"
    data = {"message", message}
    requests.post('http://127.0.0.1/status', json=data)

    #If robot is paused, check for start signal.
    if paused == True:
        if orders != []:
            paused = False
            queue = order_to_queue(orders[current_order])#Convert to queue of movements
            start_time = time.time()

    else: #If not paused, move the robot.

        #If an order has been completed:
        if order_completed == True:
            print("Order completed")
            current_order += 1

            #If there are no more orders, reset variables and pause the robot.
            if(current_order >= len(orders)):
                orders = []
                paused = True
                order_completed = False
                move_completed = True
                current_task = 0
                current_order = 0
                continue

            #If there are more orders, load the next one.
            else:
                queue = order_to_queue(orders[current_order])
                current_task = 0
                order_completed = False
        
        #If the order has not yet been completed:
        else:
            # log the power
            power_log_file.write(f'{time.time()-start_time} {state.actual_robot_voltage} {state.actual_robot_current} {state.actual_robot_voltage*state.actual_robot_current}\n')
            
            #Check if the queue has been finished.
            if current_task >= len(queue):
                order_completed = True

            # ---------- Move the robot ---------- #
            #If move was completed, start new move
            elif move_completed and state.output_int_register_0 == 1:
                print(f'Move {current_task} at time: {time.time()-start_time} is: {queue[current_task]}')
                move_completed = False
                
                if queue[current_task] == "l":
                    grab(2)
                elif queue[current_task] == "s":
                    grab(1)
                elif queue[current_task] == "r":
                    grab(0)
                else:
                    list_to_setp(setp, queue[current_task])
                    con.send(setp)
                current_task += 1
                watchdog.input_int_register_0 = 1
                #time.sleep(0.005)
                continue
            
            #If output_int_register_0 is 0, the robot has finished moving. Mark the move as finished. Maybe idk how it works
            elif not move_completed and state.output_int_register_0 == 0:
                move_completed = True
                watchdog.input_int_register_0 = 0

    #Send watchdog, so we don't lose connection.
    con.send(watchdog)

# ---------- after disconnect ----------#
con.send_pause()
con.disconnect()