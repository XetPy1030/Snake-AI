import os
import time

import pygame

from app.game_core import Game, Direction
from app.gui.config import DIVIDER, NANOS_PER_TICK, FPS
from app.gui.objects import GUISnake, SAppleSprite
from app.sprites import ASSETS_DIR, SnakeSegmentSprite, AppleSprite


def main():
    # Initialize Pygame
    pygame.init()

    # Set up the screen
    screen = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)

    # Get screen dimensions
    width = screen.get_width()
    height = screen.get_height()

    # Set up the background
    background = pygame.image.load(os.path.join(ASSETS_DIR, 'background.jpg'))
    background = pygame.transform.scale(background, (width, height))

    # Set up the clock
    clock = pygame.time.Clock()

    # Initialize Groups
    all_sprites = pygame.sprite.Group()
    SnakeSegmentSprite.containers = all_sprites
    AppleSprite.containers = all_sprites

    # Set up the game
    game = Game(width // DIVIDER, height // DIVIDER)
    snake = GUISnake()
    game.add_snake(snake)
    game.spawn_food()

    # Initialize the sprite
    SAppleSprite(game, width=DIVIDER, height=DIVIDER)

    # Main loop
    last_tick = time.time_ns()
    while not game.is_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction(Direction.UP)
                if event.key == pygame.K_DOWN:
                    snake.change_direction(Direction.DOWN)
                if event.key == pygame.K_LEFT:
                    snake.change_direction(Direction.LEFT)
                if event.key == pygame.K_RIGHT:
                    snake.change_direction(Direction.RIGHT)

        screen.blit(background, (0, 0))

        current_tick = time.time_ns()
        if current_tick - last_tick >= NANOS_PER_TICK:
            last_tick += NANOS_PER_TICK
            if not game.tick():
                return

        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)
