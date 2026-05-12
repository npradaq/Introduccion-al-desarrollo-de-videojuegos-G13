from enum import Enum, auto


class LanderPhase(Enum):
    PATROL = auto()
    DESCEND = auto()
    ABDUCT = auto()


class CLanderState:
    def __init__(self, initial_patrol_duration: float = 0.0) -> None:
        self.phase = LanderPhase.PATROL
        self.target_astronaut_id: int | None = None
        self.patrol_timer: float = 0.0
        self.patrol_change_interval: float = 2.0
        self.initial_patrol_remaining: float = initial_patrol_duration
