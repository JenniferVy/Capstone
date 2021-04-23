import trash_placement
import pygame
import random
import numpy as np

from pygame.locals import (
    RLEACCEL,
)

################################## Waves ######################################
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

WAVE_RANGES = [(0.0, 0.0), (0.1, 0.1), (0.2, 0.3), (0.6, 1.0), (1.0, 1.5), (2.0, 2.5)]
WAVE_WEIGHTS = [1, 7, 118, 223, 246, 57]

class Wave(pygame.sprite.Sprite):
  def __init__(self):
        super(Wave, self).__init__()
        
        # choose wave
        wave_choice = random.randint(0, 5)
        print(wave_choice)
        if wave_choice == 0:
            self.surf = pygame.image.load("assets/wave0.png").convert()
            self.size = random.uniform(WAVE_RANGES[0][0], WAVE_RANGES[0][1])
        elif wave_choice == 1:
            self.surf = pygame.image.load("assets/wave1.png").convert()
            self.size = random.uniform(WAVE_RANGES[1][0], WAVE_RANGES[1][1])
        elif wave_choice == 2:
            self.surf = pygame.image.load("assets/wave2.png").convert()
            self.size = random.uniform(WAVE_RANGES[2][0], WAVE_RANGES[2][1])
        elif wave_choice == 3:
            self.surf = pygame.image.load("assets/wave3.png").convert()
            self.size = random.uniform(WAVE_RANGES[3][0], WAVE_RANGES[3][1])
        elif wave_choice == 4:
            self.surf = pygame.image.load("assets/wave4.png").convert()
            self.size = random.uniform(WAVE_RANGES[4][0], WAVE_RANGES[4][1])
        elif wave_choice == 5:
            self.surf = pygame.image.load("assets/wave5.png").convert()
            self.size = random.uniform(WAVE_RANGES[5][0], WAVE_RANGES[5][1])
        else:
            self.surf = pygame.image.load("assets/wave4.png").convert()
            self.size = random.uniform(WAVE_RANGES[4][0], WAVE_RANGES[4][1])

        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(0, SCREEN_HEIGHT),
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
            )
        )
        self.speed = 1
        

  def update(self):
        self.rect.move_ip(0, -self.speed)
        if self.rect.top <= 0:
            self.kill()

################################## Trash ######################################
class Trash(pygame.sprite.Sprite):
    def __init__(self, screen_rect, color, pos, radius):
        super().__init__()
        self.image = pygame.Surface(((radius+4)*2, (radius+4)*2), pygame.SRCALPHA)
        color = pygame.Color(color)
        color.a = 127
        pygame.draw.circle(self.image, color, (radius+4, radius+4), radius+4)
        pygame.draw.circle(self.image, 'black', (radius+4, radius+4), radius)
        self.rect = self.image.get_rect(center=pos)
        self.vel = pygame.Vector2(0, 0)
        self.pos = pygame.Vector2(self.rect.center)
        self.screen_rect = screen_rect

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos

        if not self.screen_rect.contains(self.rect):
            self.kill()


############################### Environment ###################################
class Environment:
  """
  Micmics trash distribution of GPGP 
  """
  def __init__(self, width, length, pixels_per_meter, screen):
    self.areaW = width
    self.areaL = length
    self.pixels_per_meter = pixels_per_meter
    self.screen = screen
    self.screen_rect = screen.get_rect()
    self.trash_pieces = trash_placement.generate_trash(self.areaW, self.areaL)
    self.trash_sprites = pygame.sprite.Group()

    for size_class in self.trash_pieces:
        for plastic_type in self.trash_pieces[size_class]:
            for piece in self.trash_pieces[size_class][plastic_type]:
                pixel_pos = np.array(piece[0]) * self.pixels_per_meter
                pixel_radius = piece[1]/2 * self.pixels_per_meter
                self.trash_sprites.add(Trash(self.screen_rect, trash_placement.size_class_colors[size_class], pixel_pos, pixel_radius))
