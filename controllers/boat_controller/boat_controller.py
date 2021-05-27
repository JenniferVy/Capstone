"""boat_controller controller."""
import sys
import getpass

from numpy import longdouble
if getpass.getuser() == 'ryannemiroff':
    sys.path.append("/Applications/Webots.app/lib/controller/python38")
sys.path.append("../../") # Capstone folder

import math
import trash_placer
from webots_sensors import Sensors
from controls import Controls

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor

conveyor_test = False # TODO don't place other trash and make boat move forward when this is true

# PReconfigured waypoint path for boat
gps_path = [
    (35, -35),
    (-35, -35),
    (-35, 35),
    (35, 35)
]

CONTROLLER_SAMPLING_PERIOD = 40
next_controller_step = 40 # should be after all sensors have measured their first value

NUM_TOP_CLEATS = 7

# create the Robot instance.
supervisor = Supervisor()
robot = supervisor

robot_node = supervisor.getFromDef('BOAT')

sonar_node = supervisor.getFromDef('SONAR')
sonar_pos = sonar_node.getField("translation").getSFVec3f()
sonar_display = supervisor.getFromDef('SONAR_DISPLAY').getField("children")
sonar_blobs = []

boat_pos = robot_node.getPosition()
area_width = 100 # m
area_length = 100 # m
trash_placer.place_trash(supervisor.getRoot().getField("children"), boat_pos[0], boat_pos[2], area_width, area_length)

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

gps = robot.getDevice('gps')
compass = robot.getDevice('compass')
gyro = robot.getDevice('gyro')
sonar = robot.getDevice('sonar')

sensors = Sensors(gps, compass, gyro, sonar)
controller = Controls(sensors, gps_path)

prop_r_motor = robot.getDevice('prop_r_motor')
prop_r_motor.setPosition(float('+inf'))
prop_r_motor.setVelocity(0)
prop_l_motor = robot.getDevice('prop_l_motor')
prop_l_motor.setPosition(float('+inf'))
prop_l_motor.setVelocity(0)

def display_sonar_targets():
    sonar_targets = sonar.getTargets()
    i = 0
    for target in sonar_targets:
        x_rel = target.distance * math.cos(target.azimuth) + sonar_pos[0]
        z_rel = target.distance * math.sin(target.azimuth) + sonar_pos[2]
        boat_rotation = robot_node.getField("rotation").getSFRotation()
        boat_heading = -boat_rotation[1] * boat_rotation[3] # convert from axis-angle representation
        boat_pos = robot_node.getPosition()
        x = (math.cos(boat_heading) * x_rel - math.sin(boat_heading) * z_rel) + boat_pos[0]
        z = (math.sin(boat_heading) * x_rel + math.cos(boat_heading) * z_rel) + boat_pos[2]

        if i < len(sonar_blobs):
            sonar_blobs[i].getField("translation").setSFVec3f([x, 0, z])
        else:
            blob_str = """
                Transform {{
                  translation {x} 0 {z}
                  children [
                    Shape {{
                      appearance PBRAppearance {{
                        baseColor 0.5 0 1
                        transparency 0.5
                        metalness 0
                      }}
                      geometry Sphere {{
                        radius 1
                      }}
                    }}
                  ]
                }}
            """.format(x=x, z=z)
            sonar_display.importMFNodeFromString(-1, blob_str)
            sonar_blobs.append(sonar_display.getMFNode(-1))
        
        i += 1

    for j in range(len(sonar_blobs) - i):
        sonar_display.removeMF(-1)
        sonar_blobs.pop()

    # print("-")

top_motor = robot.getDevice('top_motor')
top_pos = 0.00
top_motor.setPosition(float('+inf'))
top_motor.setVelocity(1.0)

mid_motor = robot.getDevice('mid_motor')
# mid_pos = 0.00
mid_motor.setPosition(float('+inf'))
mid_motor.setVelocity(1.0)

conveyor_cleats = [] 
cleat_motors = []
for i in range(3, NUM_TOP_CLEATS+3):
  conveyor_cleats.append(supervisor.getFromDef('BOAT.CONVEYOR.T{:02d}_SLIDER.T{:02d}_PARAM'.format(i, i)))
  cleat_motors.append(supervisor.getDevice('T{:02d}_motor'.format(i)))

cleat_pos = [0]*NUM_TOP_CLEATS
cleat_top_thresholds = [0.60, 1.35, 2.05, 2.75, 3.45, 4.15, 4.85]
cleat_bot_thresholds = [-5.5+c for c in cleat_top_thresholds]

for m, motor in enumerate(cleat_motors):
    # motor.setPosition(cleat_pos[m])
  motor.setPosition(float('+inf'))
  motor.setVelocity(1.0)

next_movement_step = 0

def move_conveyor_cleats(time_ms):
  global next_movement_step
  # global top_pos
  # top_pos += 0.02      
  # top_motor.setPosition(top_pos)
  top_motor.setVelocity(1.0)
  # global mid_pos
  # mid_pos += 0.02      
  # mid_motor.setPosition(mid_pos)
  mid_motor.setVelocity(1.0)
  
  # print('Function Called')
  for m, motor in enumerate(cleat_motors):
    # motor.setPosition(cleat_pos[m])
    motor.setVelocity(1.0)
  # print('Position Set')

  if time_ms >= next_movement_step:
    next_movement_step += 100
    # print('Cleats Updating')
    for c, cleat in enumerate(conveyor_cleats):
      # cleat_pos[c] += 0.1
      # if cleat_pos[c] > cleat_top_thresholds[c]:
      if cleat.getField('position').getSFFloat() > cleat_top_thresholds[c]:
        cleat.getField('position').setSFFloat(cleat_bot_thresholds[c])
        # cleat_pos[c] = cleat_bot_thresholds[c]
  

# Main loop:
# - perform simulation steps until Webots is stopping the controller
time = 0
while robot.step(timestep) != -1:
    time += timestep
    
    if time >= next_controller_step:
        next_controller_step += CONTROLLER_SAMPLING_PERIOD
        display_sonar_targets()
        sensors.step()
        l_motor_speed, r_motor_speed = controller.top_level_control(timestep/1000)
        prop_l_motor.setVelocity(l_motor_speed)
        prop_r_motor.setVelocity(r_motor_speed)

    move_conveyor_cleats(time)

# Enter here exit cleanup code.
