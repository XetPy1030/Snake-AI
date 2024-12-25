import os

import pygame

from app.game_core import Game

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')


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
        self.rect.x = game.food[0] * self.width
        self.rect.y = game.food[1] * self.height

    def update(self):
        self.rect.x = self.game.food[0] * self.width
        self.rect.y = self.game.food[1] * self.height
