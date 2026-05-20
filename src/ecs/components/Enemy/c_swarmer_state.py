
from enum import Enum


class CSwarmerState:
    def __init__(self) -> None:
        self.state = SwarmerState.CHASE

class SwarmerState(Enum):
    CHASE = 1