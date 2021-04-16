import pygame
from pygame.math import Vector2
from math import radians, sin, cos

from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
############################### Trash Storage ##################################

MAX_LOAD = 5000 # max trash load capacity in kg

class Trash_Storage:
  """ Stores trash as boat sweeps GPGP """

  def __init__(self):
    """ Trash_Storage Class Constructor to initialize the object

    params: None
    """
    self.max_stor = MAX_LOAD
    self.trash_cap = 0
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

BOAT_LENGTH = 142 # final boat length in range [5, 20] meters -- 142px
BOAT_WIDTH = 82 # final boat width in range [2, 6] meters -- 82px
BOAT_HEIGHT = 6 # final boat height in range [2, 6] meters
TACTICAL_DIAMETER = 4*BOAT_LENGTH # final boat tactical diameter < 5*length

ANCH_MAX_SURV_WAVE_HEIGHT = 4
OPER_MAX_SURV_WAVE_HEIGHT = 2

class Boat(pygame.sprite.Sprite):
  """ Boat that will move through GPGP """

  def __init__(self, start_lat = SCREEN_HEIGHT/2, start_long = SCREEN_WIDTH/2, angle = 0, fuel = 80, trash_stor = Trash_Storage()):
    """ Boat Class Constructor to initialize the object

    params:
    - start_lat: starting latitude coordinate
    - start_long: starting longitude coordinate
    - fuel: starting fuel levels
    - trash_stor: Trash_Storage() object part of boat
    """
    # pygame commands for simulation
    super(Boat, self).__init__()
    self.surf = pygame.image.load("assets/sccr_boat.png").convert()
    self.surf.set_colorkey((255, 255, 255), RLEACCEL)
    self.orig_surf = self.surf
    self.rect = self.surf.get_rect(
      center=(
                start_lat,
                start_long,
            )
    )
    self.pos = Vector2(self.rect.center)
    self.offset = Vector2(TACTICAL_DIAMETER/4, 0)
    self.angle = angle
    self.set_direction()

    # boat dimensions in meters
    self.length = BOAT_LENGTH
    self.width = BOAT_WIDTH
    self.height = BOAT_HEIGHT
    self.tact_diam = TACTICAL_DIAMETER

    # boat speed
    self.max_speed = MAX_SPEED
    self.curr_speed = 2 # operational speed  in range [2,5] knots or [1.03, 2.57] m/s
    self.rot_speed = self.curr_speed / 2

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

  def update(self, pressed_keys):
    if pressed_keys[K_UP]:
        self.pos += self.direction * self.curr_speed
        self.rect.center = self.pos
    if pressed_keys[K_DOWN]:
        self.rect.center = self.pos
    if pressed_keys[K_LEFT]:
        self.angle += self.rot_speed
        self.rotate()
    if pressed_keys[K_RIGHT]:
        self.angle -= self.rot_speed
        self.rotate()

    # Keep boat on the screen
    if self.rect.left < 0:
        self.rect.left = 0
    if self.rect.right > SCREEN_WIDTH:
        self.rect.right = SCREEN_WIDTH
    if self.rect.top <= 0:
        self.rect.top = 0
    if self.rect.bottom >= SCREEN_HEIGHT:
        self.rect.bottom = SCREEN_HEIGHT
  
  def rotate(self):
    """Rotate the image of the sprite around a pivot point."""
    self.surf = pygame.transform.rotate(self.orig_surf, self.angle)
    self.rect = self.surf.get_rect()
    self.rect.center = self.pos
    self.set_direction()

  def stableState(self):
    """
    Periodically checks if boat is in stable state; if too much tilt, then stop operation

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
  
