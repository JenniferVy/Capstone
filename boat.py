import pygame
from pygame.math import Vector2
from math import radians, degrees, sin, cos, sqrt
import numpy as np

from pygame.locals import (
    RLEACCEL,
    QUIT,
)

############################### Trash Storage ##################################

STORAGE_MAX_LOAD = 4500 # max trash load capacity in kg, based on 15 m^3 box and 300 kg/m^3 bulk density of plastic ()

class Trash_Storage:
  """ Stores trash as boat sweeps GPGP """

  def __init__(self):
    """ Trash_Storage Class Constructor to initialize the object

    params: None
    """
    self.mass_capacity = STORAGE_MAX_LOAD
    self.collected_mass = 0
    self.conveyor_on = False

  def activateConveyor(self, state):
    """
    Activates conveyor belt which rolls up trash to trash storage unit

    params: 
    - state: desired state of conveyor belt
    returns: updated state pf conveyor belt
    rtype: bool
    """
    return False
  
################################# Boat ########################################
MAX_SPEED = 10 # final max boat speed in range [5,10]
OPERATIONAL_SPEED = 6 # operational speed in range [2,5] knots or [1.03, 2.57] m/s

BOAT_LENGTH = 10.1 # 10.1 m
BOAT_WIDTH = 6.03 # 6.03 m
CONVEYOR_OPENING_WIDTH = 4.5 # m
BOAT_HEIGHT = 6 # final boat height in range [2, 6] meters
PROPELLER_OFFSET = 2.286 # distance of propellers from center of boat (meters)
# TACTICAL_DIAMETER = 4*BOAT_LENGTH # final boat tactical diameter < 5*length

BOAT_MASS = 24124.6 # kg
BOAT_I_VERTICAL = 264053 # moment of inertia around the vertical axis (kg*m^2)
PROPELLER_THRUST_COEFFICIENT = 0.3435 # Newtons of thrust per (rad/s)^2 of angular speed
SIMPLE_DRAG_FORCE_COEFFICIENT_FORWARD = 738.830 # Newtons of drag per (m/s)^2 of speed
SIMPLE_DRAG_FORCE_COEFFICIENT_SIDEWAYS = 8594.36 # Newtons of drag per (m/s)^2 of speed
SIMPLE_DRAG_TORQUE_COEFFICIENT = 245966 # Newton-meters of drag per (rad/s)^2 of angular speed

ANCH_MAX_SURV_WAVE_HEIGHT = 4
OPER_MAX_SURV_WAVE_HEIGHT = 2

class Boat(pygame.sprite.Sprite):
  """ Boat that will move through GPGP """

  def __init__(self, pixels_per_meter, logger, start_long = 0, start_lat = 0, angle = 0, fuel = 80, trash_stor = Trash_Storage()):
    """ Boat Class Constructor to initialize the object

    params:
    - start_long: starting longitude coordinate
    - start_lat: starting latitude coordinate
    - fuel: starting fuel levels
    - trash_stor: Trash_Storage() object part of boat
    """
    # pygame commands for simulation
    super(Boat, self).__init__()
    self.pixels_per_meter = pixels_per_meter
    self.logger = logger

    self.surf = pygame.transform.scale(pygame.image.load("assets/sccr_boat.png").convert(), (np.rint(BOAT_WIDTH*pixels_per_meter).astype(int), np.rint(BOAT_LENGTH*pixels_per_meter).astype(int)))
    self.surf.set_colorkey((255, 255, 255), RLEACCEL)
    self.orig_surf = self.surf
    self.pos = Vector2((start_long, start_lat))
    # self.offset = Vector2(TACTICAL_DIAMETER/4, 0)
    self.angle = angle
    self.set_direction()
    self.rect = pygame.Rect(0, 0, 0, 0)
    self.make_collision_rect()

    # boat dimensions in meters
    # self.length = BOAT_LENGTH
    # self.width = BOAT_WIDTH
    # self.height = BOAT_HEIGHT
    self.l_prop_offset = -PROPELLER_OFFSET
    self.r_prop_offset = PROPELLER_OFFSET
    # self.tact_diam = TACTICAL_DIAMETER

    # boat speed
    self.lin_vel = pygame.Vector2(0, 0)
    self.ang_vel = 0
    self.lin_acc = pygame.Vector2(0, 0)
    self.ang_acc = 0

    # coordinates
    self.start_lat = start_lat
    self.start_long = start_long
    self.curr_lat = start_lat
    self.curr_long = start_long
    self.pivot = [(self.rect.right - self.rect.left)/2, (self.rect.bottom - self.rect.top)/2]
    self.fuel = fuel

    # stability
    self.oper_surv_wave_height = OPER_MAX_SURV_WAVE_HEIGHT
    self.anch_surv_wave_height = ANCH_MAX_SURV_WAVE_HEIGHT
    #self.stability_thresh = tilt_degrees
    self.in_oper = True

    # trash storage
    self.trash_storage = trash_stor

    self.dist_travelled = 0

  def update(self, l_motor_speed, r_motor_speed, dt):
    # Approximate linear and angular velocity change by multiplying motor speeds by thrust coefficient (neglect drag).
    prev_lin_vel = self.lin_vel
    prev_ang_vel = self.ang_vel
    self.lin_vel += self.lin_acc * dt
    self.ang_vel += self.ang_acc * dt

    # Use average velocity of current and previous time steps to update position
    old_pos = (self.pos[0], self.pos[1])
    self.pos += self.pixels_per_meter * (prev_lin_vel + self.lin_vel) / 2 * dt
    self.rect.center = self.pos
    self.angle += degrees((prev_ang_vel + self.ang_vel) / 2 * dt)
    self.rotate()

    # TODO dist_travelled calculations might be off, seems to be overestimating too much
    self.dist_travelled += sqrt((old_pos[0] - self.pos[1])**2 + (old_pos[1] - self.pos[1])**2) / self.pixels_per_meter
    self.logger.update_distance_travelled(self.dist_travelled)
    # # Keep boat on the screen
    # if self.rect.left < 0:
    #     self.rect.left = 0
    # if self.rect.right > SCREEN_WIDTH:
    #     self.rect.right = SCREEN_WIDTH
    # if self.rect.top <= 0:
    #     self.rect.top = 0
    # if self.rect.bottom >= SCREEN_HEIGHT:
    #     self.rect.bottom = SCREEN_HEIGHT

    # Propeller thrust model. Propellers are at a 10 degree angle, so scale thrust accordingly.
    thrust_l = PROPELLER_THRUST_COEFFICIENT * cos(radians(10)) * abs(l_motor_speed) * l_motor_speed
    thrust_r = PROPELLER_THRUST_COEFFICIENT * cos(radians(10)) * abs(r_motor_speed) * r_motor_speed
    force_l = self.direction * thrust_l
    force_r = self.direction * thrust_r
    torque_l = thrust_l * self.l_prop_offset
    torque_r = thrust_r * self.r_prop_offset

    # Drag
    forward_vel = np.dot(self.lin_vel, self.direction)
    sideways_vel =  np.dot(self.lin_vel, (self.direction[1], -self.direction[0]))
    forward_drag_force = -SIMPLE_DRAG_FORCE_COEFFICIENT_FORWARD * abs(forward_vel) * forward_vel
    sideways_drag_force = -SIMPLE_DRAG_FORCE_COEFFICIENT_SIDEWAYS * abs(sideways_vel) * sideways_vel

    drag_force = forward_drag_force * self.direction + sideways_drag_force * pygame.Vector2(self.direction[1], -self.direction[0])
    drag_torque = -SIMPLE_DRAG_TORQUE_COEFFICIENT * abs(self.ang_vel) * self.ang_vel

    # Acceleration is force (or torque) divided by mass (or moment of inertia)
    self.lin_acc = (force_l + force_r + drag_force) / BOAT_MASS
    self.ang_acc = (torque_l + torque_r + drag_torque) / BOAT_I_VERTICAL
  
  def rotate(self):
    """Rotate the image of the sprite around a pivot point."""
    self.surf = pygame.transform.rotate(self.orig_surf, self.angle)
    self.set_direction()
    self.make_collision_rect()

  def make_collision_rect(self):
    # make a rectangle that has the proper width when projected perpendicular to the conveyor belt
    collection_width = self.pixels_per_meter*CONVEYOR_OPENING_WIDTH - 8 # make collision area smaller by 8 pixels because trash sprites have 4 pixel radius highlight

    self.rect.width = max(abs(collection_width * cos(radians(self.angle))), 2)
    self.rect.height = max(abs(collection_width * sin(radians(self.angle))), 2)

    collision_x_offset = (self.surf.get_height()/2 - 4) * sin(radians(self.angle))
    collision_y_offset = (self.surf.get_height()/2 - 4) * cos(radians(self.angle))
    self.rect.center = (self.pos[0] + collision_x_offset, self.pos[1] + collision_y_offset)

  def stableState(self):
    """
    Periodically checks if boat is in stable state; if max wave height collding, then stop operation

    params: None
    returns: whether boat is in stable state
    rtype: bool
    """
    return True
  
  def setOperationState(self, state):
    """
    Sets operation state of boat

    params: 
    - state: desired operation state of boat
    returns: updated operation state of boat
    rtype: bool
    """
    self.in_oper = state
    return self.in_oper

  def set_direction(self):
    rad = radians(self.angle)
    self.direction = pygame.Vector2(sin(rad), cos(rad))
    
