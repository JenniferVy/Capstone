from boat import Boat
from trash_sensor import Trash_Sensor
from trash_sensor import *
from environment import *
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

# Set up the drawing window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

ADD_WAVE = pygame.USEREVENT + 1
pygame.time.set_timer(ADD_WAVE, 1000)

ADD_TRASH = pygame.USEREVENT + 2
pygame.time.set_timer(ADD_TRASH, 2000)

boat = Boat()
# controller = Controls(boat)
sensor = Trash_Sensor()

waves = pygame.sprite.Group()
trash_pieces = pygame.sprite.Group()
all_comp = pygame.sprite.Group()


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

        elif event.type == ADD_WAVE:
            new_wave = Wave() 
            waves.add(new_wave)
            all_comp.add(new_wave)
        
        elif event.type == ADD_TRASH:
            new_trash = Trash()
            trash_pieces.add(new_trash)
            all_comp.add(new_trash)
    
    pressed_keys = pygame.key.get_pressed()

    # Update the boat sprite based on user keypresses
    boat.update(pressed_keys)
    waves.update()
    trash_pieces.update()
    
    # Fill the background with light blue
    screen.fill((173, 216, 230))

    # Flip the display
    for e in all_comp:
        screen.blit(e.surf, e.rect)

    sensor.detectTrash(boat.pos.x, boat.pos.y, math.radians(boat.angle))
    sensor.drawTrash(screen)
    
    screen.blit(boat.surf, boat.rect)

    waves_hit = pygame.sprite.spritecollide(boat, waves, False)
    for wave in waves_hit:
        if wave.size > boat.oper_surv_wave_height:
            boat.setOperationState(False)
            #wave.kill()
    
    trash_collected = pygame.sprite.spritecollide(boat, trash_pieces, True)
    for trash in trash_collected:
        boat.trash_storage.trash_cap += trash.mass

    tps, tpd = 0, 0
    trash_text = myfont.render("Trash Collected [kg]: {trash:.2f}".format(
        trash = boat.trash_storage.trash_cap), 1, (0,0,0))
    tps_text = myfont.render("Trash per Time [kg/s]: {tps:.2f}".format(
        tps = boat.trash_storage.trash_cap/(pygame.time.get_ticks()/1000.0)), 1, (0,0,0))
    tpd_text = myfont.render("Trash per Distance Travelled [kg/m]: {tpd:.2f}".format( 
        tpd = boat.trash_storage.trash_cap/(boat.dist_travelled/1000.0) if boat.dist_travelled != 0 else 0), 1, (0,0,0))
    screen.blit(trash_text, (5, 10))
    screen.blit(tps_text, (5, 25))
    screen.blit(tpd_text, (5, 40))
    pygame.display.flip()

    # Ensure program maintains a rate of 10 frames per second
    clock.tick(5)

# Done! Time to quit.
pygame.quit()
