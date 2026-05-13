from enum import Enum, auto


class AstronautPhase(Enum):
    FALLING = auto()
    LANDED = auto()
    CAPTURED = auto()
    RESCUED = auto()


class CAstronautState:
    def __init__(self, land_y: float) -> None:
        self.phase = AstronautPhase.FALLING
        self.land_y: float = land_y
