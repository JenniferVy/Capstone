from environment import Environment
from trash_placement import *
import pygame
from pygame.math import Vector2
from math import radians, sin, cos

################################### Trash ######################################
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

TRASH_SIZES = [(0, 0), (0, 0), (1, 5), (5, 10)]
TRASH_MASS = [(0.00, 0.23), (0.00, 0.36), (0.02, 1.55), (0.35, 4.28)]
TRASH_WEIGHTS = [8, 13, 26, 53]

class Trash(pygame.sprite.Sprite):
  def __init__(self):
    super(Trash, self).__init__()

    # choose trash type
    trash_choice = random.choices(list(range(0, 4, 1)), TRASH_WEIGHTS)
    tr_c = trash_choice[0]
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, 10)
    if tr_c == 2:
      r = random.uniform(TRASH_SIZES[tr_c][0], TRASH_SIZES[tr_c][1])/2.0
      self.surf = pygame.Surface((r*2.0, r*2.0))
      self.surf.fill((255, 128, 0))
      pygame.draw.circle(self.surf, (255, 128, 0), (r,r), r)
    elif tr_c == 3:
      r = random.uniform(TRASH_SIZES[tr_c][0], TRASH_SIZES[tr_c][1])/2.0
      self.surf = pygame.Surface((r*2.0, r*2.0))
      self.surf.fill((255, 0, 0))
      pygame.draw.circle(self.surf, (255, 0, 0), (r,r), r)
    else:
      self.surf = pygame.Surface((1, 1))
      self.surf.fill((0, 128, 255))
      
    self.rect = self.surf.get_rect(
      center = (random.randint(0, SCREEN_WIDTH),
          random.randint(0, 10)))
    #self.pos = Vector2(self.rect.center)
    self.speed = 3
    self.mass = random.uniform(TRASH_MASS[tr_c][0], TRASH_MASS[tr_c][1])

  def update(self):
    # self.pos += (-self.speed/3, self.speed)
    # self.rect.center = self.pos
    self.rect.move_ip(-self.speed/3, +self.speed)
    if self.rect.bottom >= SCREEN_HEIGHT:
      self.kill()
    if self.rect.left < 0:
      self.kill()

############################### Trash Sensor ###################################

TRASH_SIZE = 5 # default trash size, collecting macro and above
TRASH_SENSOR_RADIUS = 10

class Trash_Sensor:
  """
  Senses trash 
  """
  def __init__(self, enviro = Environment()):
    """ Trash_Sensor Class Constructor to initialize the object
    params: None
    """
    # TODO: establish trash size ranges
    self.trash_size = TRASH_SIZE
    self.sensor_radius = TRASH_SENSOR_RADIUS

  def detectTrash(self):
    """
    Detects trash of trash_size within radius of sensor_radius
    params: None
    returns: latitude and longitude of closest trash surpassing trash size in radius
    rtype: [float, float]
    """
    # TODO: detect trash and return its coordinates
    return []