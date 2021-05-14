from trash_sensor import Trash_Sensor
from boat import Boat
import math
import numpy as np
from dataclasses import dataclass

@dataclass
class SonarObject:
    distance: float
    azimuth: float
    size_est: float

class Sensors:
    def __init__(self, boat: Boat, trash_sensor: Trash_Sensor, pixels_per_meter):
        self.trash_sensor = trash_sensor
        self.boat = boat
        self.pixels_per_meter = pixels_per_meter

    def get_pos(self):
        return self.boat.pos / self.pixels_per_meter

    def get_heading(self):
        return -math.radians(self.boat.angle) + math.pi/2

    def get_direction(self):
        return self.boat.direction

    def get_forward_vel(self):
        return np.dot(self.boat.lin_vel, self.boat.direction)

    def get_sideways_vel(self):
        return np.dot(self.boat.lin_vel, (self.boat.direction[1], -self.boat.direction[0]))

    def get_ang_vel(self):
        return -self.boat.ang_vel

    def get_sonar_objects(self):
        sonar_objects = []
        for piece in self.trash_sensor.detected_pieces:
            dx = piece.x - self.get_pos()[0]
            dy = piece.y - self.get_pos()[1]
            distance = math.sqrt(dx**2 + dy**2)
            piece_angle = math.atan2(dy, dx)
            boat_angle = self.get_heading()
            azimuth = piece_angle - boat_angle
            sonar_objects.append(SonarObject(distance, azimuth, piece.size))
        
        return sonar_objects
