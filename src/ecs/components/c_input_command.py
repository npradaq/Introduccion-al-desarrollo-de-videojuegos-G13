from enum import Enum


class CommandPhase(Enum):
    START = 0
    END = 1


class CInputCommand:
    def __init__(self, name: str, key: int) -> None:
        self.name = name
        self.key = key
        self.phase = CommandPhase.END
