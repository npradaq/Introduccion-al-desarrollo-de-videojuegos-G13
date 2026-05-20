class CShootDelay:
    def __init__(self, shoot_delay: float, acuracy_rtadius: int, shoot_detection_distance: int, bullet_velocity:int) -> None:
        self.shoot_delay = shoot_delay
        self.time_since_last_shot = 0.0
        self.acuracy_radius = acuracy_rtadius
        self.shoot_detection_distance = shoot_detection_distance
        self.bullet_velocity = bullet_velocity
        