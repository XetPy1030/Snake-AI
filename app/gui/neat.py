import os
import sys

import neat
import pygame

import app.gui
from app.game_core import Game, Direction
from app.gui.config import DIVIDER, FPS
from app.gui.objects import GUISnake, SAppleSprite
from app.sprites import ASSETS_DIR, SnakeSegmentSprite, AppleSprite

start = False
generation = 0
MAX_TICKS_WITHOUT_FOOD = 300


class GenerationGame(Game):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticks = 0
        self.last_growth_tick = 0

    def tick(self):
        is_success = super().tick()
        if is_success:
            self.ticks += 1
            if self.ticks - self.last_growth_tick >= MAX_TICKS_WITHOUT_FOOD:
                self.is_over = True
                return False

        return is_success

    def spawn_food(self) -> bool:
        if not super().spawn_food():
            return False

        self.last_growth_tick = self.ticks
        return True

    def get_data(self):
        head = self.snake.body[0]

        nearest_upper_wall = head[1]
        higher_body = [segment for segment in self.snake.body if segment[1] < head[1] and segment != head]
        if higher_body:
            nearest_upper_wall = head[1] - max(higher_body)[1]

        nearest_lower_wall = self.height - head[1]
        lower_body = [segment for segment in self.snake.body if segment[1] > head[1] and segment != head]
        if lower_body:
            nearest_lower_wall = min(lower_body)[1] - head[1]

        nearest_left_wall = head[0]
        left_body = [segment for segment in self.snake.body if segment[0] < head[0] and segment != head]
        if left_body:
            nearest_left_wall = head[0] - max(left_body)[0]

        nearest_right_wall = self.width - head[0]
        right_body = [segment for segment in self.snake.body if segment[0] > head[0] and segment != head]
        if right_body:
            nearest_right_wall = min(right_body)[0] - head[0]

        return [
            self.snake.direction == Direction.UP,
            self.snake.direction == Direction.DOWN,
            self.snake.direction == Direction.LEFT,
            self.snake.direction == Direction.RIGHT,
            self.snake.body[0][0] < self.food[0],
            self.snake.body[0][0] > self.food[0],
            self.snake.body[0][1] < self.food[1],
            self.snake.body[0][1] > self.food[1],
            len(self.snake.body) - 1,
            nearest_upper_wall,
            nearest_lower_wall,
            nearest_left_wall,
            nearest_right_wall
        ]

    def get_reward(self):
        return (len(self.snake.body) - 1) * 10


def run_generation(genomes, config):
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

    nets = []
    games = []

    # init genomes
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0  # every genome is not successful at the start

        # init games
        game = GenerationGame(width // DIVIDER, height // DIVIDER)
        snake = GUISnake()
        game.add_snake(snake)
        game.spawn_food()
        games.append(game)

        # Initialize the sprite
        SAppleSprite(game, width=DIVIDER, height=DIVIDER)

    font = pygame.font.SysFont("Roboto", 40)
    heading_font = pygame.font.SysFont("Roboto", 80)

    # the LOOP
    app.gui.neat.generation += 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    app.gui.neat.start = True

        if not app.gui.neat.start:
            continue

        # input each game data
        for i, game in enumerate(games):
            if game.is_over:
                continue

            output = nets[i].activate(game.get_data())
            i = output.index(max(output))

            if i == 0:
                game.snake.change_direction(Direction.UP)
            elif i == 1:
                game.snake.change_direction(Direction.DOWN)
            elif i == 2:
                game.snake.change_direction(Direction.LEFT)
            elif i == 3:
                game.snake.change_direction(Direction.RIGHT)

        # now, update game and set fitness (for alive games only)
        games_left = 0
        for i, game in enumerate(games):
            if not game.is_over:
                games_left += 1
                game.tick()
                genomes[i][1].fitness += game.get_reward()  # new fitness (aka game instance success)

        # check if games left
        if not games_left:
            max_snake_length = max(len(game.snake.body) for game in games)
            print(f"Generation {app.gui.neat.generation} finished with max snake length: {max_snake_length}")

            break

        # display stuff
        screen.blit(background, (0, 0))

        all_sprites.update()
        all_sprites.draw(screen)

        label = heading_font.render("Поколение: " + str(app.gui.neat.generation), True, (73, 168, 70))
        label_rect = label.get_rect()
        label_rect.center = (width / 2, height / 2 - 100)
        screen.blit(label, label_rect)

        label = font.render("Игр осталось: " + str(games_left), True, (51, 59, 70))
        label_rect = label.get_rect()
        label_rect.center = (width / 2, height / 2)
        screen.blit(label, label_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
