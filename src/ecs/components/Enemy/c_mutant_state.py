from enum import Enum
import pygame

class CMutantState:
    def __init__(self) -> None:
        self.state = MutantState.CHASE
        self.astronaute_being_abducted = -1


class MutantState(Enum):
    CHASE = 1