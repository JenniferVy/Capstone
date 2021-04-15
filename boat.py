import pygame

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

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
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

BOAT_LENGTH = 20 # final boat length in range [5, 20] meters
BOAT_WIDTH = 6 # final boat width in range [2, 6] meters
BOAT_HEIGHT = 6 # final boat height in range [2, 6] meters
TACTICAL_DIAMETER = 5*BOAT_LENGTH # final boat tactical diameter < 5*length

class Boat(pygame.sprite.Sprite):
  """ Boat that will move through GPGP """

  def __init__(self, tilt_degrees = 0, start_lat = 0, start_long = 0, orientation = 90, fuel = 80, trash_stor = Trash_Storage()):
    """ Boat Class Constructor to initialize the object

    params:
    - start_lat: starting latitude coordinate
    - start_long: starting longitude coordinate
    - fuel: starting fuel levels
    - trash_stor: Trash_Storage() object part of boat
    """
    # pygame commands for simulation
    super(Boat, self).__init__()
    self.surf = pygame.image.load("assets/small_trasnparent_boat.png").convert()
    self.surf.set_colorkey((255, 255, 255), RLEACCEL)
    self.rect = self.surf.get_rect()

    # boat dimensions in meters
    self.length = BOAT_LENGTH
    self.width = BOAT_WIDTH
    self.height = BOAT_HEIGHT
    self.tact_diam = TACTICAL_DIAMETER

    # boat speed
    self.max_speed = MAX_SPEED
    self.curr_speed = 0 # operational speed  in range [2,5] knots or [1.03, 2.57] m/s

    # coordinates
    self.start_lat = start_lat
    self.start_long = start_long
    self.curr_lat = start_lat
    self.curr_long = start_long
    self.orientation = orientation
    self.fuel = fuel

    # stability
    self.stability_thresh = tilt_degrees
    self.in_oper = True

    # trash storage
    self.trash_storage = trash_stor

  def update(self, pressed_keys):
    if pressed_keys[K_UP]:
        self.rect.move_ip(0, -2)
    if pressed_keys[K_DOWN]:
        self.rect.move_ip(0, 2)
    if pressed_keys[K_LEFT]:
        self.rect.move_ip(-21, 0)
    if pressed_keys[K_RIGHT]:
        self.rect.move_ip(2, 0)

    # Keep boat on the screen
    if self.rect.left < 0:
        self.rect.left = 0
    if self.rect.right > SCREEN_WIDTH:
        self.rect.right = SCREEN_WIDTH
    if self.rect.top <= 0:
        self.rect.top = 0
    if self.rect.bottom >= SCREEN_HEIGHT:
        self.rect.bottom = SCREEN_HEIGHT

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
    return True

    
  
