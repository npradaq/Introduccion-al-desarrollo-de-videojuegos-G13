class CAstronautSpawner:
    def __init__(self, spawn_times: list[float], astro_cfg: dict,
                 world_width: int, terrain_heights: list[float],
                 astro_sprite_h: int, screen_h: int) -> None:
        self.spawn_times = spawn_times
        self.astro_cfg = astro_cfg
        self.world_width = world_width
        self.terrain_heights = terrain_heights
        self.astro_sprite_h = astro_sprite_h
        self.screen_h = screen_h
        self.elapsed: float = 0.0
