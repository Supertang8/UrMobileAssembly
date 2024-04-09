import sys

sys.path.append("..")
import logging

import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
import time

# logging.basicConfig(level=logging.INFO)

#ROBOT_HOST = "169.254.141.137"
ROBOT_HOST = "192.168.0.104"
ROBOT_PORT = 30004
config_filename = "control_loop_configuration.xml"

keep_running = True

logging.getLogger().setLevel(logging.INFO)

conf = rtde_config.ConfigFile(config_filename)
state_names, state_types = conf.get_recipe("state")
setp_names, setp_types = conf.get_recipe("setp")
watchdog_names, watchdog_types = conf.get_recipe("watchdog")
gripper_names, gripper_types = conf.get_recipe("gripper")

con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
con.connect()

# get controller version
con.get_controller_version()

# setup recipes
con.send_output_setup(state_names, state_types)
setp = con.send_input_setup(setp_names, setp_types)
watchdog = con.send_input_setup(watchdog_names, watchdog_types)
gripper = con.send_input_setup(gripper_names, gripper_types)

# Setpoints to move the robot to
setp1 = [-0.12, -0.43, 0.14, 0, 3.11, 0.04]
setp2 = [0.116, -0.539, 0.39, 0.916, -2.433, -0.097]

front_cover_pos = [
    [0.116, -0.539, 0.39, 0.916, -2.433, -0.097],
    [0.116, -0.539, 0.39, 0.916, -2.433, -0.097],
    [0.116, -0.539, 0.39, 0.916, -2.433, -0.097]
]

back_cover_pos = [
    [-0.12, -0.43, 0.14, 0, 3.11, 0.04],
    [0.116, -0.539, 0.39, 0.916, -2.433, -0.097],
    [0.116, -0.539, 0.39, 0.916, -2.433, -0.097]
]

fuse_pos = [
    [7, 0, 0, 0, 0, 0],
    [8, 0, 0, 0, 0, 0]
]
pcb_pos = [0.006, -0.286, 0.073, 3, 0, -0.96]
end_pos = [-0.12, -0.43, 0.14, 0, 3.11, 0.04]

setp.input_double_register_0 = 0
setp.input_double_register_1 = 0
setp.input_double_register_2 = 0
setp.input_double_register_3 = 0
setp.input_double_register_4 = 0
setp.input_double_register_5 = 0

gripper.standard_digital_output = 0
gripper.standard_digital_output_mask = 0

# The function "rtde_set_watchdog" in the "rtde_control_loop.urp" creates a 1 Hz watchdog
watchdog.input_int_register_0 = 0


def setp_to_list(sp):
    sp_list = []
    for i in range(0, 6):
        sp_list.append(sp.__dict__["input_double_register_%i" % i])
    return sp_list


def list_to_setp(sp, list):
    for i in range(0, 6):
        sp.__dict__["input_double_register_%i" % i] = list[i]
    return sp

def grab(id): # 0=close, 1=small, 2=large
    #gripper.standard_digital_output_mask = 0b01100000 #Set digital output 5 and 6 to LOW.
    #gripper.standard_digital_output = 0b10011111 
    #con.send(gripper)
    gripper.standard_digital_output_mask = 0b01111000
    if(id == 2): 
        #gripper.standard_digital_output_mask = 0b00100000 #close gripper, set digital output 6 to HIGH
        gripper.standard_digital_output = 0b00100000 
    elif(id == 1): 
        #gripper.standard_digital_output_mask = 0b00100000 #close gripper, set digital output 6 to HIGH
        gripper.standard_digital_output = 0b10000000 
    else:
        #gripper.standard_digital_output_mask = 0b01000000 #open gripper, set digital output 5 to HIGH
        gripper.standard_digital_output = 0b01010000 
    #gripper.standard_digital_output = 0b11111111 
    con.send(gripper)
queue = [0,0]
def order_to_queue(order):
    queue = []
    if order[0] != 0: #if the order contains at least one fuse
        queue.append(fuse_pos[order[0]-1]) #add fuse position
        queue.append("s")
    #pcb_approach = pcb_pos
    #pcb_approach[0] = pcb_approach[0] + 0.02
    #pcb_approach[2] = pcb_approach[2] + 0.02
    queue.append([0.058, -0.286, 0.145, 3, 0, -0.96])
    queue.append(pcb_pos)
    queue.append("l")
    queue.append([0.058, -0.286, 0.145, 3, 0, -0.96])
    #queue.append("r")
    '''queue.append(back_cover_pos[order[1]])
    queue.append("r")
    queue.append(front_cover_pos[order[2]])
    queue.append("l")
    queue.append(back_cover_pos[order[1]])
    queue.append(end_pos)
    queue.append("r")'''
    return queue

#Order data from PIServer
orders = [
    [0, 0, 0],
    [2, 1, 1]
]

queue = order_to_queue(orders[0])
current_task = 0

print(queue)

# start data synchronization
if not con.send_start():
    sys.exit()

# control loop
move_completed = True
while True:
    # receive the current state
    state = con.receive()

    if state is None:
        break

    # do my thing
    if move_completed and state.output_int_register_0 == 1:
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
        print(current_task)
        current_task += 1
        watchdog.input_int_register_0 = 1
        time.sleep(0.5)
    elif not move_completed and state.output_int_register_0 == 0:
        move_completed = True
        watchdog.input_int_register_0 = 0

    if current_task > len(queue):
        break

    con.send(watchdog)

    '''# do something...
    if move_completed and state.output_int_register_0 == 1:

        move_completed = False

        if setp_to_list(setp) == setp2:
            new_setp = setp1
            grab(True)
        else:
            new_setp = setp2
            grab(False)
        list_to_setp(setp, new_setp)
        print("New pose = " + str(new_setp))
        # send new setpoint
        con.send(setp)
        watchdog.input_int_register_0 = 1

    elif not move_completed and state.output_int_register_0 == 0:
        print("Move to confirmed pose = " + str(state.target_q))
        move_completed = True
        watchdog.input_int_register_0 = 0

    # kick watchdog
    con.send(watchdog)'''

con.send_pause()

con.disconnect()
