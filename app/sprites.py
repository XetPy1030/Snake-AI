import os
import time

import pygame

from app.game_core import Game
from app.gui.config import NANOS_PER_TICK, TICKS_PER_SECOND

ASSETS_DIR = 'assets/'


class SnakeSegmentSprite(pygame.sprite.Sprite):
    containers = None

    def __init__(self, position, is_head=False, width=10, height=10):
        super().__init__(self.containers)

        self.width = width
        self.height = height

        self.is_head = is_head

        self.image = pygame.image.load(os.path.join(ASSETS_DIR, 'snake_head.png' if is_head else 'snake_body.png'))
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        self.rect = self.image.get_rect()
        self.rect.x = position[0] * self.width
        self.rect.y = position[1] * self.height

    def update_position(self, position):
        self.rect.x = position[0] * self.width
        self.rect.y = position[1] * self.height


class SnakeFuturePathSegmentSprite(pygame.sprite.Sprite):
    containers = None

    def __init__(self, position, game, width=10, height=10):
        super().__init__(self.containers)

        self.width = width
        self.height = height
        self.game = game
        self.position = position

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 255, 0))
        self.image.set_alpha(50)

        self.rect = self.image.get_rect()
        self.rect.x = position[0] * self.width
        self.rect.y = position[1] * self.height

        self.start_update = None

    def update(self, *args, **kwargs):
        if self.start_update is None and self.position == self.game.snake.body[0]:
            self.start_update = time.time_ns()

        if self.start_update is not None:
            progress = (time.time_ns() - self.start_update) / (NANOS_PER_TICK * TICKS_PER_SECOND)
            if progress > 1:
                progress = 1
            self.image.set_alpha(50 - 50 * progress)

            if progress >= 1:
                self.kill()


class AppleSprite(pygame.sprite.Sprite):
    containers = None

    def __init__(self, game: Game, width=10, height=10):
        super().__init__(self.containers)

        self.game = game

        self.width = width
        self.height = height

        self.image = pygame.image.load(os.path.join(ASSETS_DIR, 'apple.png'))
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        self.rect = self.image.get_rect()
        self.rect.x = self.game.food[0] * self.width
        self.rect.y = self.game.food[1] * self.height

        self.last_coordinate = self.game.food
        self.position_for_update = self.game.food
        self.start_update = time.time_ns()
        self.last_update = time.time_ns()

    def update(self):
        if self.game.is_over:
            self.kill()
            return

        if self.last_coordinate == self.game.food:
            return

        if self.position_for_update != self.game.food:
            self.start_update = time.time_ns()
            self.position_for_update = self.game.food

        progress = (time.time_ns() - self.start_update) / NANOS_PER_TICK
        if progress > 1:
            progress = 1

        self.rect.x = self.last_coordinate[0] * self.width + (
                self.game.food[0] - self.last_coordinate[0]) * self.width * progress
        self.rect.y = self.last_coordinate[1] * self.height + (
                self.game.food[1] - self.last_coordinate[1]) * self.height * progress

        if progress >= 1:
            self.last_coordinate = self.game.food
            self.last_update = time.time_ns()
