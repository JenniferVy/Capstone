"""boat_controller controller."""
import sys
import getpass
if getpass.getuser() == 'ryannemiroff':
    sys.path.append("/Applications/Webots.app/lib/controller/python38")
sys.path.append("../../") # Capstone folder

import math
import trash_placer

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor

# create the Robot instance.
supervisor = Supervisor()
robot = supervisor

robot_node = supervisor.getFromDef('BOAT')

boat_pos = robot_node.getField("translation").getSFVec3f()
trash_placer.place_trash(supervisor.getRoot().getField("children"), boat_pos[0], boat_pos[2])

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()

    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.
