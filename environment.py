from trash_placement import *
import pygame
import random

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

############################### Environment ###################################

ENVIRO_LENGTH = 1000
ENVIRO_WIDTH = 1000

class Environment:
  """
  Micmics trash distribution of GPGP 
  """
  def __init__(self, length = ENVIRO_LENGTH, width = ENVIRO_WIDTH):
    self.areaL = length
    self.areaW = width

  def generateTrashGrid(self):
    # TODO: generate grid of trash
    return []

  def plotTrashGrid(self):
    # TODO: visualize grid of trash
    return []

