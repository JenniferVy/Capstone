from boat import Boat

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

clock = pygame.time.Clock()

# Set up the drawing window
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

boat = Boat()

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
    
    pressed_keys = pygame.key.get_pressed()

    # Update the boat sprite based on user keypresses
    boat.update(pressed_keys)

    # Fill the background with white
    screen.fill((173, 216, 230))

    # Flip the display
    screen.blit(boat.surf, boat.rect)
    pygame.display.flip()

    # Ensure program maintains a rate of 30 frames per second
    clock.tick(5)

# Done! Time to quit.
pygame.quit()