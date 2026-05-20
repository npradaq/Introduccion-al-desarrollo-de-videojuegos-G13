from enum import Enum


class CPodState:
    def __init__(self, swarmer_count: int) -> None:
        self.state = PodState.CHASE
        self.swarmer_count = swarmer_count


class PodState(Enum):
    CHASE = 1