from environment import Environment
from trash_placement import *
import pygame
import math

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

# Trash sensor (sonar): http://www.teledynemarine.com/M900-2250-130-Mk2
TRASH_SENSOR_RANGE = 100 # meters
TRASH_SENSOR_FOV = math.radians(130) # radians
TRASH_SENSOR_HORIZONTAL_RESOLUTION = 0.18 # degrees TODO: This is based on beam spacing, but actual resolution might be worse.

# Assume miniumum detectable object size is related to the square of the detection distance, due to the inverse square law.
TRASH_SENSOR_MIN_OBJECT_SIZE_OVER_SQUARE_OF_DISTANCE = 1 / 60**2 # Tyler Whitaker from Teledyne Marine estimates (based on experience) that the sonar can detect a 1m x 1m objects at 60m range.

class Trash_Sensor:
  """
  Senses trash 
  """
  def __init__(self, enviro = Environment()): # TODO pass correct width and length
    """ Trash_Sensor Class Constructor to initialize the object
    params: None
    """
    self.enviro = enviro

  def detectTrash(self, x, y, heading):
    """
    Detects trash of trash_size within radius of sensor_radius
    params: None
    returns: latitude and longitude of closest trash surpassing trash size in radius
    rtype: [float, float]
    """
    x /= self.enviro.pixels_per_meter
    y /= self.enviro.pixels_per_meter
    heading = -heading + math.pi/2
    # TODO place sonar at front of boat
    x += 5*math.cos(heading)
    y += 5*math.sin(heading)

    self.detected_pieces = []

    pieces = self.enviro.trash_pieces
    for size_class in pieces:
        for plastic_type in pieces[size_class]:
            for piece in pieces[size_class][plastic_type]:
                # todo distance from boat -> can detect this size and in range? -> angle w/ heading -> within FOV?
                distance = math.sqrt((piece[0][0]-x)**2 + (piece[0][1]-y)**2)
                if distance <= TRASH_SENSOR_RANGE:
                    min_detectable_size = TRASH_SENSOR_MIN_OBJECT_SIZE_OVER_SQUARE_OF_DISTANCE * distance**2
                    if piece[1] >= min_detectable_size:
                        angle = math.atan2(piece[0][1]-y, piece[0][0]-x) - heading
                        while angle > math.pi:
                            angle -= 2*math.pi
                        while angle < -math.pi:
                            angle += 2*math.pi
                        if abs(angle) <= TRASH_SENSOR_FOV/2:
                            self.detected_pieces.append(piece)
    
    return self.detected_pieces

  def drawTrash(self, screen):
      self.enviro.drawTrash(screen)
      for piece in self.detected_pieces:
          pixel_pos = np.array(piece[0]) * self.enviro.pixels_per_meter
          pygame.draw.circle(screen, "purple", pixel_pos, piece[1]/2 * self.enviro.pixels_per_meter + 4, width=1)
