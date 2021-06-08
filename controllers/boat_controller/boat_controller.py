"""boat_controller controller."""
import sys
import getpass


from numpy import longdouble
if getpass.getuser() == 'ryannemiroff':
    sys.path.append("/Applications/Webots.app/lib/controller/python38")
sys.path.append("../../") # Capstone folder

import math
import trash_placer

from waves import frontLoad_Forces, frontLoad_Torques, sideLoad_Forces, sideLoad_Torques

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor

SONAR_SOURCE_POWER = 51469 # Watts
SONAR_RECEIVER_GAIN = 1
SONAR_SAMPLING_RATE = 40 # Update rate is 25Hz = 40ms: http://www.teledynemarine.com/Lists/Downloads/BlueView%20M900-2250-130-Mk2%20product%20leaflet.pdf

NUM_TOP_CLEATS = 7

# create the Robot instance.
supervisor = Supervisor()
robot = supervisor

robot_node = supervisor.getFromDef('BOAT')

sonar_node = supervisor.getFromDef('SONAR')
sonar_pos = sonar_node.getField("translation").getSFVec3f()
sonar_display = supervisor.getFromDef('SONAR_DISPLAY').getField("children")
sonar_blobs = []

boat_pos = robot_node.getField("translation").getSFVec3f()
area_width = 100 # m
area_length = 100 # m
# trash_placer.place_trash(supervisor.getRoot().getField("children"), boat_pos[0], boat_pos[2], area_width, area_length)

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

sonar = robot.getDevice('sonar')
sonar.enable(SONAR_SAMPLING_RATE)
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
        received_intensity = (10**(target.received_power/10)) / 1000 # We are using received_power to hold an intensity value, but first we pretend we're convertimg from dBm to Watts (when we are really interpreting it as W/m^2)
        backscattering_cross_section = (received_intensity * (4*math.pi)**2 * target.distance**4) / (SONAR_SOURCE_POWER * SONAR_RECEIVER_GAIN) # Based on sonar spherical propagation
        size_est = 2 * math.sqrt(backscattering_cross_section/math.pi) # Based on backscattering cross-section for a sphere: sigma = pi*R^2
        # print("Trash: distance: {} m, azimuth: {} rad, size: {} m".format(target.distance, target.azimuth, size_est))

        # Note: The boat position and heading used here can be used for path planning if we're too lazy to add a GPS + compass.
        x_rel = target.distance * math.cos(target.azimuth) + sonar_pos[0]
        z_rel = target.distance * math.sin(target.azimuth) + sonar_pos[2]
        boat_rotation = robot_node.getField("rotation").getSFRotation()
        boat_heading = -boat_rotation[1] * boat_rotation[3] # convert from axis-angle representation
        boat_pos = robot_node.getField("translation").getSFVec3f()
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


# CONVEYOR CODE

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
cleat_bot_thresholds = [-5.25+c for c in cleat_top_thresholds]

for m, motor in enumerate(cleat_motors):
    # motor.setPosition(cleat_pos[m])
  motor.setPosition(float('+inf'))
  motor.setVelocity(1.0)
    
def move_conveyor_cleats(time_step):
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

  if time_step % 100 == 0:
    # print('Cleats Updating')
    for c, cleat in enumerate(conveyor_cleats):
      # cleat_pos[c] += 0.1
      # if cleat_pos[c] > cleat_top_thresholds[c]:
      if cleat.getField('position').getSFFloat() > cleat_top_thresholds[c]:
        cleat.getField('position').setSFFloat(cleat_bot_thresholds[c])
        # cleat_pos[c] = cleat_bot_thresholds[c]
  
# WAVE FORCES CODE

WAVE_SAMPLING_RATE = 5
NUM_WAVE_VALUES = 479

def add_front_wave(index):
    # print('Entered Wave Function')
    # Fx1 = frontLoad_Forces.at[index-1, 'front_Fx']
    # Fy1 = frontLoad_Forces.at[index-1, 'front_Fy']
    # Fz1 = frontLoad_Forces.at[index-1, 'front_Fz']
    # Fx2 = frontLoad_Forces.at[index, 'front_Fx']
    # Fy2 = frontLoad_Forces.at[index, 'front_Fy']
    # Fz2 = frontLoad_Forces.at[index, 'front_Fz']
    # robot_node.addForce([Fx2-Fx1, Fy2-Fy1, Fz2-Fz1], True)

    # Tx1 = frontLoad_Torques.at[index-1, 'front_Tx']
    # Ty1 = frontLoad_Torques.at[index-1, 'front_Ty']
    # Tz1 = frontLoad_Torques.at[index-1, 'front_Tz']
    # Tx2 = frontLoad_Torques.at[index, 'front_Tx']
    # Ty2 = frontLoad_Torques.at[index, 'front_Ty']
    # Tz2 = frontLoad_Torques.at[index, 'front_Tz']
    # print(Tx2-Tx1, Ty2-Ty1, Tz2-Tz1)
    # robot_node.addTorque([Tx2-Tx1, Ty2-Ty1, Tz2-Tz1], True)

    Fx = frontLoad_Forces.at[index, 'front_Fx']
    Fy = frontLoad_Forces.at[index, 'front_Fy']
    Fz = frontLoad_Forces.at[index, 'front_Fz']
    robot_node.addForce([Fy, Fz, Fx], True)

    # Tx = frontLoad_Torques.at[index, 'front_Tx']
    # Ty = frontLoad_Torques.at[index, 'front_Ty']
    # Tz = frontLoad_Torques.at[index, 'front_Tz']
    # print(Ty, Tz, Tx)
    # robot_node.addTorque([Ty, Tz, Tx], True)

    Tx = frontLoad_Torques.at[index, 'front_Tx']
    Ty = frontLoad_Torques.at[index, 'front_Ty']
    Tz = frontLoad_Torques.at[index, 'front_Tz']
    robot_node.addTorque([-Tx, Ty, -Tz], True)
    
    # print(Fx)
    # print("Added Front Wave Torque")

def add_side_wave(index):
    # Fx = sideLoad_Forces.at[index, 'side_Fx']
    # Fy = sideLoad_Forces.at[index, 'side_Fy']
    # Fz = sideLoad_Forces.at[index, 'side_Fz']
    # robot_node.addForce([-Fz, -Fx, -Fy], True)

    Tx = sideLoad_Torques.at[0, 'side_Tx']
    Ty = sideLoad_Torques.at[0, 'side_Ty']
    Tz = sideLoad_Torques.at[0, 'side_Tz']
    robot_node.addTorque([Tz, Tx, Ty], True)

    # Fx1 = sideLoad_Forces.at[index-1, 'side_Fx']
    # Fy1 = sideLoad_Forces.at[index-1, 'side_Fy']
    # Fz1 = sideLoad_Forces.at[index-1, 'side_Fz']
    # Fx2 = sideLoad_Forces.at[index, 'side_Fx']
    # Fy2 = sideLoad_Forces.at[index, 'side_Fy']
    # Fz2 = sideLoad_Forces.at[index, 'side_Fz']
    # robot_node.addForce([Fx2-Fx1, Fy2-Fy1, Fz2-Fz1], True)
    # print("Added Side Wave")

# Main loop:
# - perform simulation steps until Webots is stopping the controller
time = 0
wave_counter = 0

# Fx = frontLoad_Forces.at[0, 'front_Fx']
# Fy = frontLoad_Forces.at[0, 'front_Fy']
# Fz = frontLoad_Forces.at[0, 'front_Fz']
# robot_node.addForce([-Fy, Fz, Fx], True)

# Tx = frontLoad_Torques.at[0, 'front_Tx']
# Ty = frontLoad_Torques.at[0, 'front_Ty']
# Tz = frontLoad_Torques.at[0, 'front_Tz']
# robot_node.addTorque([-Ty, Tz, Tx], True)

# Fx = sideLoad_Forces.at[0, 'side_Fx']
# Fy = sideLoad_Forces.at[0, 'side_Fy']
# Fz = sideLoad_Forces.at[0, 'side_Fz']
# robot_node.addForce([-Fz, -Fx, -Fy], True)

Tx = sideLoad_Torques.at[0, 'side_Tx']
Ty = sideLoad_Torques.at[0, 'side_Ty']
Tz = sideLoad_Torques.at[0, 'side_Tz']
robot_node.addTorque([Tx, Ty, -Tz], True)
# print(Ty, Tz, Tx)
# print('Added Torque')

while robot.step(timestep) != -1:
    time += timestep
    wave_counter += timestep
    # Read the sensors:
    # if time % SONAR_SAMPLING_RATE == 0: # this assumes SONAR_SAMPLING_RATE is divisible by indexstep
    #     display_sonar_targets()

    # Waves
    move_conveyor_cleats(time)
    # add_front_wave(wave_counter)
    add_side_wave(wave_counter)
    if wave_counter == NUM_WAVE_VALUES:
      wave_counter = 0

    prop_r_motor.setVelocity(80) # demonstrate turning the boat by throttling the propeller motors
    prop_l_motor.setVelocity(100)

# Enter here exit cleanup code.
