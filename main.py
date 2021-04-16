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

# ADD_TRASH = pygame.USEREVENT + 1
# pygame.time.set_timer(ADD_TRASH, 250)

ADD_WAVE = pygame.USEREVENT + 1
pygame.time.set_timer(ADD_WAVE, 1000)

boat = Boat()
# controller = Controls(boat)
sensor = Trash_Sensor()

waves = pygame.sprite.Group()
#trash_pieces = pygame.sprite.Group()
all_comp = pygame.sprite.Group()
all_comp.add(boat)

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

        # add trash
        elif event.type == ADD_WAVE:
            new_wave = Wave()
            # trash_pieces.add(new_trash)
            # all_comp.add(new_trash)
            waves.add(new_wave)
            all_comp.add(new_wave)
    
    pressed_keys = pygame.key.get_pressed()

    # Update the boat sprite based on user keypresses
    boat.update(pressed_keys)
    #trash_pieces.update()
    waves.update()

    # Fill the background with white
    screen.fill((173, 216, 230))

    # Flip the display
    for e in waves:
        screen.blit(e.surf, e.rect)

    sensor.detectTrash(boat.pos.x, boat.pos.y, math.radians(boat.angle))
    sensor.drawTrash(screen)
    
    screen.blit(boat.surf, boat.rect)

    #trash_collected = pygame.sprite.spritecollide(boat, trash_pieces, True)
    waves_hit = pygame.sprite.spritecollide(boat, waves, False)
    for wave in waves_hit:
        #boat.trash_storage.trash_cap += 1
        if wave.size > boat.oper_surv_wave_height:
            boat.setOperationState(False)
        wave_text = myfont.render("Wave Height [m]: {0}".format(wave.size), 1, (0, 0, 0))

    
    #trash_text = myfont.render("Trash Collected [kg]: {0}".format(boat.trash_storage.trash_cap), 1, (0,0,0))
    #screen.blit(wave_text, (5, 10))

    pygame.display.flip()

    # Ensure program maintains a rate of 10 frames per second
    clock.tick(10)

# Done! Time to quit.
pygame.quit()
