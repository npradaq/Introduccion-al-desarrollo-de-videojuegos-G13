class CEnemySpawner:
    def __init__(self, lander_cfg: dict, enemy_start_delay: float,
                 world_width: int, screen_h: int) -> None:
        self.lander_cfg = lander_cfg
        self.enemy_start_delay = enemy_start_delay
        self.world_width = world_width
        self.screen_h = screen_h
        self.elapsed: float = 0.0
        self.spawn_timer: float = 0.0
        self.total_spawned: int = 0
