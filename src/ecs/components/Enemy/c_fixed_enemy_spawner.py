class CEnemySpawner():
    def __init__(self, dataEnemies:dict, dataSpawnEvents: list[dict]) -> None:
        self.dataEnemies = dataEnemies

        self.dataSpawnEvents = dataSpawnEvents

        for event in self.dataSpawnEvents:
            event["spawned"] = False