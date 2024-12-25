import os
import sys
import time
from functools import partial

import neat
import pygame

from app.game_core import Snake, Game, Direction
from app.gui_config import DIVIDER, FPS, NANOS_PER_TICK
from app.sprites import ASSETS_DIR, AppleSprite, SnakeSegmentSprite

SSnakeSegmentSprite = partial(SnakeSegmentSprite, width=DIVIDER, height=DIVIDER)
SAppleSprite = partial(AppleSprite, width=DIVIDER, height=DIVIDER)


class GUISnake(Snake):
    def __init__(self):
        super().__init__()
        self.segments = [SSnakeSegmentSprite(position, is_head=(i == 0)) for i, position in enumerate(self.body)]

    def move(self):
        super().move()
        for segment, position in zip(self.segments, self.body):
            segment.update_position(position)

    def grow(self):
        super().grow()
        self.segments.append(SSnakeSegmentSprite(self.body[-1]))

    def kill(self):
        super().kill()
        for segment in self.segments:
            segment.kill()
        self.segments = []


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
    global generation
    global start

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
        games.append(game)

        # Initialize the sprite
        SAppleSprite(game, width=DIVIDER, height=DIVIDER)

    font = pygame.font.SysFont("Roboto", 40)
    heading_font = pygame.font.SysFont("Roboto", 80)

    # the LOOP
    generation += 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start = True

        if not start:
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
            print(f"Generation {generation} finished with max snake length: {max_snake_length}")

            break

        # display stuff
        screen.blit(background, (0, 0))

        all_sprites.update()
        all_sprites.draw(screen)

        label = heading_font.render("Поколение: " + str(generation), True, (73, 168, 70))
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


if __name__ == '__main__':
    main()
    pygame.quit()
