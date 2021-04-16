from boat import Boat
from trash_sensor import *
# from controls import *

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

ADD_TRASH = pygame.USEREVENT + 1
pygame.time.set_timer(ADD_TRASH, 250)

boat = Boat()
# controller = Controls(boat)

trash_pieces = pygame.sprite.Group()
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
        elif event.type == ADD_TRASH:
            new_trash = Trash()
            trash_pieces.add(new_trash)
            all_comp.add(new_trash)
    
    pressed_keys = pygame.key.get_pressed()

    # Update the boat sprite based on user keypresses
    boat.update(pressed_keys)
    trash_pieces.update()

    # Fill the background with white
    screen.fill((173, 216, 230))

    # Flip the display
    for e in all_comp:
        screen.blit(e.surf, e.rect)

    trash_collected = pygame.sprite.spritecollide(boat, trash_pieces, True)
    for trash in trash_collected:
        boat.trash_storage.trash_cap += 1

    trash_text = myfont.render("Trash Collected [kg]: {0}".format(boat.trash_storage.trash_cap), 1, (0,0,0))
    screen.blit(trash_text, (5, 10))

    pygame.display.flip()

    # Ensure program maintains a rate of 10 frames per second
    clock.tick(10)

# Done! Time to quit.
pygame.quit()