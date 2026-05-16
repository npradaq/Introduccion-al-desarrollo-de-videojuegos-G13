from enum import Enum
import pygame

class CLanderState:
    def __init__(self) -> None:
        self.state = LanderState.PATROL
        self.astronaute_being_abducted = -1
        self.initial_patrol_remaining = 3.0
        self.astronaute_being_abducted = None


class LanderState(Enum):
    PATROL = 1
    DESCEND = 2
    ABDUCT = 3