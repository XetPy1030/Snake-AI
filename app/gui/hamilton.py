import os
import time

import pygame

from app.game_core import Game, Direction
from app.gui.config import DIVIDER, NANOS_PER_TICK, FPS
from app.gui.objects import GUISnake, SAppleSprite, SSnakeFuturePathSegmentSprite
from app.hamiltonian_cycle import HamiltonianCycle, HPath, HNode, Vector
from app.sprites import ASSETS_DIR, SnakeSegmentSprite, AppleSprite, SnakeFuturePathSegmentSprite


class HamiltonSnake(GUISnake):
    def __init__(self):
        super().__init__()
        self.hc = None
        self.cycle = []
        self.add_count = 0

    def grow(self):
        super().grow()

    def on_food_eaten(self):
        super().on_food_eaten()
        self.add_count += 1

    def move(self):
        super().move()
        self.add_count = max(0, self.add_count - 1)

    def reset_on_hamiltonian(self, hc, cycle):
        self.hc = hc
        self.cycle = cycle
        self.body = [(self.cycle[3].x, self.cycle[3].y), (self.cycle[2].x, self.cycle[2].y), (self.cycle[1].x, self.cycle[1].y), (self.cycle[0].x, self.cycle[0].y)]
        self.reset_segments()


class HamiltonGame(Game):
    snake: HamiltonSnake

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hc = HamiltonianCycle(self.width, self.height)
        self.cycle = self.hc.cycle

        self.apple_cycle_position = None
        self.path: HPath | None = None

        self.future_path_segments: list[SnakeFuturePathSegmentSprite] = []

    def tick(self):
        if self.is_over:
            return False

        if not self.path or self.path.path_counter >= self.path.path_length:
            self.calculate_path()

        if (not self.path) or (not self.path.path_length):
            next_pos = self.get_next_position()
            vel_x = next_pos.x - self.snake.body[0][0]
            vel_y = next_pos.y - self.snake.body[0][1]
        else:
            next_move = self.path.get_next_move()
            vel_x = next_move['x']
            vel_y = next_move['y']

        if vel_x == -1 and vel_y == 0:
            self.snake.change_direction(Direction.LEFT)
        elif vel_x == 1 and vel_y == 0:
            self.snake.change_direction(Direction.RIGHT)
        elif vel_x == 0 and vel_y == -1:
            self.snake.change_direction(Direction.UP)
        elif vel_x == 0 and vel_y == 1:
            self.snake.change_direction(Direction.DOWN)
        else:
            raise ValueError(f"Unknown velocity: {vel_x}, {vel_y}")

        return super().tick()

    def calculate_path(self):
        self.path = self.get_path_based_on_a_star()
        print(f"SNAKE: {self.snake.body[0]}, FOOD: {self.food}, SNAKE LENGTH: {len(self.snake.body)}, PATH: {self.path}")
        self.reset_future_path_segments()

    def reset_future_path_segments(self):
        for segment in self.future_path_segments:
            segment.kill()
        self.future_path_segments = []
        if not self.path or not self.path.path_length:
            return

        current_x, current_y = self.snake.body[0]
        self.future_path_segments.append(SSnakeFuturePathSegmentSprite((current_x, current_y), game=self))
        for i in range(self.path.path_counter, self.path.path_length):
            diff_x = self.path.nodes_in_path[i + 1].x - self.path.nodes_in_path[i].x
            diff_y = self.path.nodes_in_path[i + 1].y - self.path.nodes_in_path[i].y

            current_x += diff_x
            current_y += diff_y

            segment = SSnakeFuturePathSegmentSprite((current_x, current_y), game=self)
            self.future_path_segments.append(segment)

    def add_snake(self, snake: HamiltonSnake):
        super().add_snake(snake)
        snake.reset_on_hamiltonian(self.hc, self.cycle)
        self.spawn_food()

    def spawn_food(self) -> bool:
        is_spawn = super().spawn_food()
        if is_spawn:
            self.calculate_path()
        return is_spawn

    def get_path_based_on_a_star(self):
        for n in self.cycle:
            n.reset_for_a_star()
        self.apple_cycle_position = self.hc.get_node_no(self.food[0], self.food[1])

        start_node = self.cycle[self.hc.get_node_no(self.snake.body[0][0], self.snake.body[0][1])]
        big_list: list[HPath] = []

        winning_path = None

        starting_path = HPath(start_node, self.cycle[self.apple_cycle_position])

        big_list.append(starting_path)

        while True:
            if len(big_list) == 0:
                return winning_path
            current_path = big_list.pop(0)
            if winning_path and current_path.path_length >= winning_path.path_length:
                continue

            if current_path.distance_to_apple == 0:
                if winning_path is None or current_path.path_length < winning_path.path_length:
                    winning_path = current_path.clone()
                continue

            final_node_in_path = current_path.get_last_node()

            if not final_node_in_path.already_visited or current_path.path_length < final_node_in_path.shortest_distance_to_this_point:
                final_node_in_path.already_visited = True
                final_node_in_path.shortest_distance_to_this_point = current_path.path_length

                for n in final_node_in_path.edges:
                    if self.over_takes_tail(n, final_node_in_path, current_path.get_snake_tail_position_after_following_path(self)):
                        if n.cycle_no != final_node_in_path.cycle_no + 1:
                            continue

                    p = current_path.clone()
                    p.add_to_tail(n)
                    if p.get_last_node().already_visited and p.path_length > p.get_last_node().shortest_distance_to_this_point:
                        continue
                    big_list.append(p)

            big_list.sort(key=lambda x: x.distance_to_apple + x.path_length)

    def get_next_position(self):
        apple_cycle_position = self.hc.get_node_no(self.food[0], self.food[1])
        possible_next_positions = self.hc.get_possible_positions_from(self.snake.body[0][0], self.snake.body[0][1])
        min_distance = 100000
        min_index = 0
        for i in range(len(possible_next_positions)):
            distance = apple_cycle_position - possible_next_positions[i]
            while distance < 0:
                distance += len(self.cycle)
            if self.over_takes_tail(self.cycle[possible_next_positions[i]]):
                continue
            if distance < min_distance:
                min_distance = distance
                min_index = i
        if min_distance == 100000:
            return self.cycle[(self.hc.get_node_no(self.snake.body[0][0], self.snake.body[0][1]) + 1) % len(self.cycle)]
        return self.cycle[possible_next_positions[min_index]]

    def over_takes_tail(self, new_pos: HNode, h: HNode | None = None, t: Vector | HNode | None = None):
        min_distance_between_head_and_tail = 50
        head = h.cycle_no if h else self.hc.get_node_no(self.snake.body[0][0], self.snake.body[0][1])
        actual_tail = self.hc.get_node_no(t.x, t.y) if t else self.hc.get_node_no(self.tail_blocks[0].x, self.tail_blocks[0].y)
        if self.get_distance_between_points(head, actual_tail) <= min_distance_between_head_and_tail + self.snake.add_count:
            return True
        tail = actual_tail - min_distance_between_head_and_tail - self.snake.add_count
        while tail < 0:
            tail += len(self.cycle)
        if self.get_distance_between_points(head, new_pos.cycle_no) >= self.get_distance_between_points(head, tail):
            return True
        return False

    def get_distance_between_points(self, from_, to):
        distance = to - from_
        while distance < 0:
            distance += len(self.cycle)
        return distance

    @property
    def tail_blocks(self):
        return [Vector(*pos) for pos in self.snake.body[1:]][::-1]



def main():
    # Initialize Pygame
    pygame.init()

    game_width = 40
    game_height = 20

    # Set up the screen
    # screen = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)
    screen = pygame.display.set_mode([game_width * DIVIDER, game_height * DIVIDER])

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
    SnakeFuturePathSegmentSprite.containers = all_sprites
    AppleSprite.containers = all_sprites

    # Set up the game
    game = HamiltonGame(game_width, game_height)
    print(f"Game: {game.width}x{game.height}")
    snake = HamiltonSnake()
    game.add_snake(snake)

    # Initialize the sprite
    SAppleSprite(game, width=DIVIDER, height=DIVIDER)

    # Main loop
    last_tick = time.time_ns()
    is_speeding = False
    while not game.is_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_speeding = not is_speeding

        screen.blit(background, (0, 0))

        if ((time.time_ns() - last_tick >= NANOS_PER_TICK) or is_speeding) and not game.is_over:
            last_tick += NANOS_PER_TICK if not is_speeding else 0
            if not game.tick():
                print("Game over!")
                print(f"Snake: {game.snake.body}, Food: {game.food}, Path: {game.path}")
                return

        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)
