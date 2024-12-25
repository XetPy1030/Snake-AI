from enum import Enum
from random import random


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


TCoord = tuple[int, int]


class Snake:
    def __init__(self, start_coord: TCoord = (0, 0)):
        self.direction = Direction.RIGHT
        self.body = [start_coord]

    def move(self):
        head = self.body[0]
        if self.direction == Direction.UP:
            new_head = (head[0], head[1] - 1)
        elif self.direction == Direction.DOWN:
            new_head = (head[0], head[1] + 1)
        elif self.direction == Direction.LEFT:
            new_head = (head[0] - 1, head[1])
        elif self.direction == Direction.RIGHT:
            new_head = (head[0] + 1, head[1])
        else:
            raise ValueError(f"Unknown direction: {self.direction}")
        self.body = [new_head] + self.body[:-1]

    def change_direction(self, direction: Direction):
        if self.direction == Direction.UP and direction == Direction.DOWN:
            return
        if self.direction == Direction.DOWN and direction == Direction.UP:
            return
        if self.direction == Direction.LEFT and direction == Direction.RIGHT:
            return
        if self.direction == Direction.RIGHT and direction == Direction.LEFT:
            return
        self.direction = direction

    def grow(self):
        self.body.append(self.body[-1])


class Game:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.snake = None
        self.food = None
        self.is_over = False

    def tick(self):
        self.snake.move()

        # Проверяем, не столкнулась ли змейка со стеной или с собой
        if not self.check_collision():
            self.is_over = True
            return False

        # Проверяем, съела ли змейка еду
        if self.snake.body[0] == self.food:
            self.snake.grow()
            if not self.spawn_food():
                self.is_over = True
                return False

        return True

    def add_snake(self, snake: Snake):
        if self.snake is not None:
            raise ValueError("Snake already added")

        self.snake = snake
        self.spawn_food()

    def spawn_food(self) -> bool:
        if len(self.snake.body) == self.width * self.height:
            return False

        while True:
            new_food = (int(random() * self.width), int(random() * self.height))
            if new_food not in self.snake.body:
                self.food = new_food
                break

        return True

    def check_collision(self) -> bool:
        head = self.snake.body[0]
        if head[0] < 0 or head[0] >= self.width:
            return False
        if head[1] < 0 or head[1] >= self.height:
            return False
        if head in self.snake.body[1:]:
            return False
        return True