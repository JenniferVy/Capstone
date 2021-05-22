import math
import numpy as np
from dataclasses import dataclass

SONAR_SOURCE_POWER = 51469 # Watts
SONAR_RECEIVER_GAIN = 1
SONAR_SAMPLING_PERIOD = 40 # Update rate is 25Hz = 40ms: http://www.teledynemarine.com/Lists/Downloads/BlueView%20M900-2250-130-Mk2%20product%20leaflet.pdf
BACKSCATTERING_CROSS_SECTION_SCALING = 0.5 # Defined in trash_placer.py. Assume this is roughly known in order to compute the size of detected trash (maybe add noise later).

@dataclass
class SonarObject:
    distance: float
    azimuth: float
    size_est: float

class Sensors:
    def __init__(self, gps, compass, gyro, sonar):
        self.gps = gps
        self.compass = compass
        self.gyro = gyro
        self.sonar = sonar

        self.gps.enable(40)
        self.compass.enable(40)
        self.gyro.enable(40)
        self.sonar.enable(SONAR_SAMPLING_PERIOD)

        self.vel_direction = np.array((1,0))
        self.last_gps_pos = None

    def step(self):
        current_gps_pos = self.get_pos()
        if self.last_gps_pos is not None:
            if current_gps_pos[0] == self.last_gps_pos[0] and current_gps_pos[1] == self.last_gps_pos[1]:
                return
            dx = current_gps_pos[0] - self.last_gps_pos[0]
            dz = current_gps_pos[1] - self.last_gps_pos[1]
            self.vel_direction = np.array((dx, dz))
            self.vel_direction /= np.linalg.norm(self.vel_direction)
        self.last_gps_pos = current_gps_pos

    def get_pos(self):
        gps_3d_pos = self.gps.getValues()
        return (gps_3d_pos[0], gps_3d_pos[2])

    def get_heading(self):
        direction = self.get_direction()
        return math.atan2(direction[1], direction[0])

    def get_direction(self):
        compass_axes = self.compass.getValues()
        direction = np.array((compass_axes[0], -compass_axes[2]))
        direction /= np.linalg.norm(direction)
        return direction

    def get_forward_vel(self):
        lin_vel = self.gps.getSpeed() * self.vel_direction
        direction = self.get_direction()
        return np.dot(lin_vel, direction)

    def get_sideways_vel(self):
        lin_vel = self.gps.getSpeed() * self.vel_direction
        direction = self.get_direction()
        return np.dot(lin_vel, (direction[1], -direction[0]))

    def get_ang_vel(self):
        return -self.gyro.getValues()[1]

    def get_sonar_objects(self):
        # TODO account for off-center sonar location, or cheat and move sonar to the center
        sonar_objects = []
        for target in self.sonar.getTargets():
            received_intensity = (10**(target.received_power/10)) / 1000 # We are using received_power to hold an intensity value, but first we pretend we're convertimg from dBm to Watts (when we are really interpreting it as W/m^2)
            backscattering_cross_section = (received_intensity * (4*math.pi)**2 * target.distance**4) / (SONAR_SOURCE_POWER * SONAR_RECEIVER_GAIN) # Based on sonar spherical propagation
            size_est = 2 * math.sqrt(backscattering_cross_section/(math.pi*BACKSCATTERING_CROSS_SECTION_SCALING)) # Based on backscattering cross-section for a sphere: sigma = pi*R^2, and adjusted based on BACKSCATTERING_CROSS_SECTION_SCALING
            # print("Trash: distance: {} m, azimuth: {} rad, size: {} m".format(target.distance, target.azimuth, size_est))
            sonar_objects.append(SonarObject(target.distance, target.azimuth, size_est))
        
        return sonar_objects
