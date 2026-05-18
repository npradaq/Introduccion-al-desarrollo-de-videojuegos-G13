import pygame
import esper
import random

from src.create.prefab_creator_enemy import create_enemy
from src.ecs.components.Enemy.c_fixed_enemy_spawner import CEnemySpawner

def system_fixed_enemy_spawner(world: esper.World, tiempo_acumulado: float):

    c_es: CEnemySpawner
    for entity, (c_es) in world.get_component(CEnemySpawner):
        dse = c_es.dataSpawnEvents
        de = c_es.dataEnemies

        for event in dse:
            if event["time"] <= tiempo_acumulado and event["spawned"] == False:
                enemyType = event["enemy_type"]
                enemy_info = de[enemyType]

                pos = pygame.Vector2(event["position"]["x"], event["position"]["y"])
                
                create_enemy(world, pos, enemy_info, enemyType)
                
                event["spawned"] = True