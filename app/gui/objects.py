from functools import partial

from app.game_core import Snake
from app.gui.config import DIVIDER
from app.sprites import SnakeSegmentSprite, AppleSprite, SnakeFuturePathSegmentSprite

SSnakeSegmentSprite = partial(SnakeSegmentSprite, width=DIVIDER, height=DIVIDER)
SSnakeFuturePathSegmentSprite = partial(SnakeFuturePathSegmentSprite, width=DIVIDER, height=DIVIDER)
SAppleSprite = partial(AppleSprite, width=DIVIDER, height=DIVIDER)


class GUISnake(Snake):
    def __init__(self):
        super().__init__()
        self.segments = [SSnakeSegmentSprite(position, is_head=(i == 0)) for i, position in enumerate(self.body)]

    def reset_segments(self):
        for segment in self.segments:
            segment.kill()
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
