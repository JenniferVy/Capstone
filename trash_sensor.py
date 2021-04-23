from environment import Environment
from trash_placement import *
import pygame
import math

class SonarCone(pygame.sprite.Sprite):
    def __init__(self, radius, fov):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        self.orig_image = self.image
        pygame.draw.arc(self.image, pygame.Color(255,255,0,63), self.image.get_rect(), -fov/2-math.pi/2, fov/2-math.pi/2, width=int(radius))
        self.rect = self.image.get_rect(center=(0,0))
        self.pos = pygame.Vector2(self.rect.center)

    def update(self, pos, angle):
        self.pos = pos
        self.rotate(angle)

    def rotate(self, angle):
        """Rotate the image of the sprite around a pivot point."""
        self.image = pygame.transform.rotate(self.orig_image, math.degrees(angle))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

class TrashOutline(pygame.sprite.Sprite):
    def __init__(self, screen_rect, pos, radius):
        super().__init__()
        self.image = pygame.Surface(((radius+4)*2, (radius+4)*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, 'purple', (radius+4, radius+4), radius+4, width=1)
        self.rect = self.image.get_rect(center=pos)
        self.vel = pygame.Vector2(0, 0)
        self.pos = pygame.Vector2(self.rect.center)
        self.screen_rect = screen_rect

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos

        if not self.screen_rect.contains(self.rect):
            self.kill()
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
  def __init__(self, enviro: Environment):
    """ Trash_Sensor Class Constructor to initialize the object
    params: None
    """
    self.enviro = enviro
    self.detected_pieces = []
    self.sonar_cone_sprite = SonarCone(TRASH_SENSOR_RANGE*enviro.pixels_per_meter, TRASH_SENSOR_FOV)
    self.detected_trash_sprites = pygame.sprite.Group()
    self.detected_trash_sprite_lookup = {}

  def update(self, x, y, heading):
    """
    Detects trash of trash_size within radius of sensor_radius
    params: None
    returns: latitude and longitude of closest trash surpassing trash size in radius
    rtype: [(float, float), float, float] : [(pos), size, mass]
    """
    x /= self.enviro.pixels_per_meter
    y /= self.enviro.pixels_per_meter
    pygame_heading = heading
    heading = -heading + math.pi/2
    sonar_dist_from_center = 2.2 # m
    x += sonar_dist_from_center*math.cos(heading)
    y += sonar_dist_from_center*math.sin(heading)

    self.sonar_cone_sprite.update((x*self.enviro.pixels_per_meter,y*self.enviro.pixels_per_meter), pygame_heading)

    self.detected_pieces = []
    old_sprites = self.detected_trash_sprite_lookup.copy()

    pieces = self.enviro.trash_pieces
    for size_class in pieces:
        for plastic_type in pieces[size_class]:
            for i in range(len(pieces[size_class][plastic_type])):
                piece = pieces[size_class][plastic_type][i]
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

                            if (size_class,plastic_type,i) not in self.detected_trash_sprite_lookup:
                                pixel_pos = np.array(piece[0]) * self.enviro.pixels_per_meter
                                pixel_radius = piece[1]/2 * self.enviro.pixels_per_meter
                                sprite = TrashOutline(self.enviro.screen_rect, pixel_pos, pixel_radius)
                                self.detected_trash_sprites.add(sprite)
                                self.detected_trash_sprite_lookup[(size_class,plastic_type,i)] = sprite
                            else:
                                del old_sprites[(size_class,plastic_type,i)]

    for piece_key in old_sprites:
        old_sprites[piece_key].kill()
        del self.detected_trash_sprite_lookup[piece_key]

    self.detected_trash_sprites.update()

    return self.detected_pieces

  def draw(self, screen):
      screen.blit(self.sonar_cone_sprite.image, self.sonar_cone_sprite.rect)
      self.detected_trash_sprites.draw(screen)
