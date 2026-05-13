class CShootDelay:
    def __init__(self, shoot_delay: float) -> None:
        self.shoot_delay = shoot_delay
        self.time_since_last_shot = 0.0