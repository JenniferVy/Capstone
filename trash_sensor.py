from environment import Environment
from trash_placement import *
import pygame

################################### Trash ######################################
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

class Trash(pygame.sprite.Sprite):
  def __init__(self):
        super(Trash, self).__init__()
        self.surf = pygame.Surface((5, 5))
        self.surf.fill((105, 105, 105))
        self.rect = self.surf.get_rect(
            center=(
                random.randint(0, SCREEN_HEIGHT),
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
            )
        )
        self.speed = random.randint(1, 2)

  def update(self):
        self.rect.move_ip(0, -self.speed)
        if self.rect.top <= 0:
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
