#!/usr/bin/env python3

from sensors import Sensors
from boat import Boat
from trash_sensor import *
from environment import *
from controls import Controls
import math

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

pygame.init()
myfont = pygame.font.SysFont("monospace", 16)

clock = pygame.time.Clock()
dt = 0.1
PLAYBACK_SPEED = 100 # e.g. 2 for playback twice as fast as reality
FRAMES_PER_SECOND = PLAYBACK_SPEED / dt

# Set up the drawing window
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
PIXELS_PER_METER = 10

WORLD_WIDTH = 200 # meters
WORLD_HEIGHT = 250

real_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen = pygame.Surface((WORLD_WIDTH*PIXELS_PER_METER, WORLD_HEIGHT*PIXELS_PER_METER), pygame.SRCALPHA)

ADD_WAVE = pygame.USEREVENT + 1
pygame.time.set_timer(ADD_WAVE, 1000)

# ADD_TRASH = pygame.USEREVENT + 2
# pygame.time.set_timer(ADD_TRASH, 2000)

gps_path = [
    (60, 60),
    (WORLD_WIDTH-60, 60),
    (WORLD_WIDTH-60, WORLD_HEIGHT-60),
    (60, WORLD_HEIGHT-60)
]

boat = Boat(pixels_per_meter=PIXELS_PER_METER, start_long=WORLD_WIDTH*PIXELS_PER_METER/2, start_lat=WORLD_HEIGHT*PIXELS_PER_METER/2)
environment = Environment(SCREEN_WIDTH, SCREEN_HEIGHT, PIXELS_PER_METER, screen)
sensor = Trash_Sensor(environment)
controller = Controls(Sensors(boat, sensor, PIXELS_PER_METER), gps_path)

# waves = pygame.sprite.Group()
trash_pieces = pygame.sprite.Group()
# all_comp = pygame.sprite.Group()

class PositionTargetSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        r = 10
        self.image = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, 'red', (r, r), r, width=3)
        pygame.draw.circle(self.image, 'red', (r, r), r-6)
        self.rect = self.image.get_rect(center=(0,0))
        self.pos = pygame.Vector2(self.rect.center)

    def update(self, pos):
        self.pos = pos
        self.rect.center = self.pos

pos_target_sprite = PositionTargetSprite()
target_pos = None

# Run until the user asks to quit
running = True
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        # Did the user hit a key?
        if event.type == KEYDOWN:
            # Was it the Escape key? If so, stop the loop.
            if event.key == K_ESCAPE:
                running = False

        # Did the user click the window close button? If so, stop the loop.
        elif event.type == QUIT:
            running = False

        # elif event.type == pygame.MOUSEBUTTONUP:
        #     target_pos = pygame.mouse.get_pos()
        #     pos_target_sprite.update(target_pos)

        # elif event.type == ADD_WAVE:
        #     new_wave = Wave() 
        #     waves.add(new_wave)
        #     all_comp.add(new_wave)
        
        # elif event.type == ADD_TRASH:
        #     new_trash = Trash()
        #     trash_pieces.add(new_trash)
        #     all_comp.add(new_trash)
    
    pressed_keys = pygame.key.get_pressed()

    # Control the boat
    # controller.keyboardInput(pressed_keys, dt) # Motor control via user input
    boat.update(*controller.top_level_control(dt), dt)

    environment.trash_sprites.update()
    sensor.update(boat.pos.x, boat.pos.y, math.radians(boat.angle))
    # waves.update()
    trash_pieces.update()
    
    # Fill the background with light blue
    screen.fill((173, 216, 230))

    # # Flip the display
    # for e in all_comp:
    #     screen.blit(e.surf, e.rect)

    environment.trash_sprites.draw(screen)
    sensor.draw(screen)

    if controller.current_goal_index < len(controller.gps_path):
        pos_target_sprite.update(pygame.Vector2(controller.gps_path[controller.current_goal_index]) * PIXELS_PER_METER)
        screen.blit(pos_target_sprite.image, pos_target_sprite.rect)
    
    screen.blit(boat.surf, boat.rect)

    # display world contents, and center around boat
    real_screen.fill('white')
    real_screen.blit(screen, (SCREEN_WIDTH/2-boat.pos[0], SCREEN_HEIGHT/2-boat.pos[1]))

    # waves_hit = pygame.sprite.spritecollide(boat, waves, False)
    # for wave in waves_hit:
    #     if wave.size > boat.oper_surv_wave_height:
    #         boat.setOperationState(False)
    #         #wave.kill()
    
    trash_collected = pygame.sprite.spritecollide(boat, environment.trash_sprites, True) # TODO collide with front of boat
    for trash in trash_collected:
        boat.trash_storage.trash_cap += trash.mass

    tps, tpd = 0, 0
    trash_text = myfont.render("Trash Collected [kg]: {trash:.4f}".format(
        trash = boat.trash_storage.trash_cap), 1, (0,0,0))
    tps_text = myfont.render("Trash per Time [kg/s]: {tps:.4f}".format(
        tps = boat.trash_storage.trash_cap/(pygame.time.get_ticks()/1000.0)), 1, (0,0,0))
    tpd_text = myfont.render("Trash per Distance Travelled [kg/m]: {tpd:.4f}".format( 
        tpd = boat.trash_storage.trash_cap/(boat.dist_travelled/1000.0) if boat.dist_travelled != 0 else 0), 1, (0,0,0))
    real_screen.blit(trash_text, (5, 10))
    real_screen.blit(tps_text, (5, 25))
    real_screen.blit(tpd_text, (5, 40))
    pygame.display.flip()

    # Ensure program maintains a rate of x frames per second
    clock.tick(FRAMES_PER_SECOND)

# Done! Time to quit.
pygame.quit()
