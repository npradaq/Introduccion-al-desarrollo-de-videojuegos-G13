from enum import Enum
import pygame

class CBomberState:
    def __init__(self) -> None:
        self.state = BomberState.ROAM
        self.target_position = pygame.Vector2(0, 0)
        self.bomb_drop_time = 0.0


class BomberState(Enum):
    ROAM = 1