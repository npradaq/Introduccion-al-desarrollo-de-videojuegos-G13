from enum import Enum
import pygame

class CBaiterState:
    def __init__(self) -> None:
        self.state = BaiterState.APROACH
        self.target_position = pygame.Vector2(0, 0)
        self.dash_time = 0.0
        self.rest_time = 0.0


class BaiterState(Enum):
    APROACH = 1
    DASH = 2
    REST = 3