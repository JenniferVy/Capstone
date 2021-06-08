from matplotlib.pyplot import pie
from trash_placement import *
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
        wave_choice = random.choices(list(range(0, 6, 1)), WAVE_WEIGHTS)
        if wave_choice[0] == 0:
            self.surf = pygame.image.load("assets/wave0.png").convert()
            self.size = random.uniform(WAVE_RANGES[0][0], WAVE_RANGES[0][1])
        elif wave_choice[0] == 1:
            self.surf = pygame.image.load("assets/wave1.png").convert()
            self.size = random.uniform(WAVE_RANGES[1][0], WAVE_RANGES[1][1])
        elif wave_choice[0] == 2:
            self.surf = pygame.image.load("assets/wave2.png").convert()
            self.size = random.uniform(WAVE_RANGES[2][0], WAVE_RANGES[2][1])
        elif wave_choice[0] == 3:
            self.surf = pygame.image.load("assets/wave3.png").convert()
            self.size = random.uniform(WAVE_RANGES[3][0], WAVE_RANGES[3][1])
        elif wave_choice[0] == 4:
            self.surf = pygame.image.load("assets/wave4.png").convert()
            self.size = random.uniform(WAVE_RANGES[4][0], WAVE_RANGES[4][1])
        elif wave_choice[0] == 5:
            self.surf = pygame.image.load("assets/wave5.png").convert()
            self.size = random.uniform(WAVE_RANGES[5][0], WAVE_RANGES[5][1])
        else:
            self.surf = pygame.image.load("assets/wave4.png").convert()
            self.size = random.uniform(WAVE_RANGES[4][0], WAVE_RANGES[4][1])

        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, 10),
            )
        )
        self.speed = 3
        

  def update(self):
    self.rect.move_ip(-self.speed/3, +self.speed)
    if self.rect.bottom >= SCREEN_HEIGHT:
      self.kill()
    if self.rect.left < 0:
      self.kill()

################################## Trash ######################################
class TrashSprite(pygame.sprite.Sprite):
    def __init__(self, color, pos, radius, piece, pixels_per_meter):
        super().__init__()
        self.piece = piece
        self.pixels_per_meter = pixels_per_meter
        self.image = pygame.Surface(((radius+4)*2, (radius+4)*2), pygame.SRCALPHA)
        color = pygame.Color(color)
        color.a = 127
        pygame.draw.circle(self.image, color, (radius+4, radius+4), radius+4)
        pygame.draw.circle(self.image, 'black', (radius+4, radius+4), radius)
        self.rect = self.image.get_rect(center=pos)
        self.vel = pygame.Vector2(0, 0)
        self.pos = pygame.Vector2(self.rect.center)

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos

        # for demo:
        self.piece.x = self.pos[0] / self.pixels_per_meter
        self.piece.y = self.pos[1] / self.pixels_per_meter


############################### Environment ###################################
class Environment:
    """
    Micmics trash distribution of GPGP 
    """
    def __init__(self, width, length, pixels_per_meter):
        self.areaW = width
        self.areaL = length
        self.pixels_per_meter = pixels_per_meter
        self.trash_pieces: List[Trash] = generate_trash(self.areaW, self.areaL, use_example=True)
        self.trash_sprites = pygame.sprite.Group()
        self.trash_sprite_list = []

        for piece in self.trash_pieces:
            pixel_pos = np.array((piece.x, piece.y)) * self.pixels_per_meter
            pixel_radius = piece.size/2 * self.pixels_per_meter
            self.trash_sprite_list.append(TrashSprite(size_class_colors[piece.size_class], pixel_pos, pixel_radius, piece, pixels_per_meter))
            self.trash_sprites.add(self.trash_sprite_list[-1])

    def collect_trash(self, sprite, trash_storage, logger):
        piece = self.trash_pieces[self.trash_sprite_list.index(sprite)]
        trash_storage.collected_mass += piece.mass
        logger.log_trash(piece)

        if trash_storage.collected_mass >= trash_storage.mass_capacity:
            print("Trash mass reached capacity!")
            logger.final_report()

        # don't destroy trash for demo
        sprite.pos[1] += 30
        # sprite.kill()
        # piece.size = 0
