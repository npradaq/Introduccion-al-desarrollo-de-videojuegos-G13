class CCanBlink:
    def __init__(self, blink_rate: float) -> None:
        self.blink_rate = blink_rate
        self._blink_time: float = 0.0
