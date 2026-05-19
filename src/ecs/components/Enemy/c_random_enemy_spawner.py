class CRandomEnemySpawner:
    def __init__(self, spawner_info: dict):

        self.spawner_info = spawner_info
        self.spawn_timer = 0.0
        self.enemies_death_count = 0
        self.current_wave = -1
        self.spawned_enemies_count = 0
        self.elapsed_wave_time = 0.0