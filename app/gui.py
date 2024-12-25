import os

import pygame

from app.game_core import Snake, Game, Direction


ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')


class SnakeSprite(pygame.sprite.Sprite):
    containers = None

    def __init__(self, snake: Snake):
        super().__init__(self.containers)

        self.snake = snake

        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 255, 255))

        self.rect = self.image.get_rect()
        self.rect.x = snake.body[0][0] * 10
        self.rect.y = snake.body[0][1] * 10

    def update(self):
        self.rect.x = self.snake.body[0][0] * 10
        self.rect.y = self.snake.body[0][1] * 10


class AppleSprite(pygame.sprite.Sprite):
    containers = None

    def __init__(self, game: Game):
        super().__init__(self.containers)

        self.game = game

        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = game.food[0] * 10
        self.rect.y = game.food[1] * 10

    def update(self):
        self.rect.x = self.game.food[0] * 10
        self.rect.y = self.game.food[1] * 10


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

    # Set up the game
    game = Game(width // 10, height // 10)
    snake = Snake()
    game.add_snake(snake)

    # Initialize Groups
    all_sprites = pygame.sprite.Group()
    SnakeSprite.containers = all_sprites
    AppleSprite.containers = all_sprites

    # Initialize the sprite
    SnakeSprite(snake)
    AppleSprite(game)

    # Main loop
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

        if not game.tick():
            return

        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(10)


if __name__ == '__main__':
    main()
    pygame.quit()
