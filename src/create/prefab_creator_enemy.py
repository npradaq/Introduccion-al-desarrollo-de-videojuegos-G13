import random

import esper
import pygame

from src.create.prefab_creator import create_sprite
from src.ecs.components.Enemy.c_chase import CChase
from src.ecs.components.Enemy.c_fixed_enemy_spawner import CEnemySpawner
from src.ecs.components.Enemy.c_lander_state import CLanderState
from src.ecs.components.Enemy.c_mutant_state import CMutantState
from src.ecs.components.Enemy.c_random_enemy_spawner import CRandomEnemySpawner
from src.ecs.components.Enemy.c_shoot_delay import CShootDelay
from src.ecs.components.Enemy.c_steer import CSteer
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.engine.service_locator import ServiceLocator


def create_enemy(world: esper.World, pos:pygame.Vector2, enemy_info:dict, enemy_type:str):
    enemy_surface = ServiceLocator.images_service.get(enemy_info["image"])
    enemy_entity = create_sprite(world, pos, pygame.Vector2(0,0), enemy_surface)
    world.add_component(enemy_entity, CTagEnemy(enemy_type))
    world.add_component(enemy_entity, CAnimation(enemy_info["animations"]))

    match enemy_type:
        case("Lander"):
            _create_enemy_lander(world, enemy_entity, enemy_info)
        case("Mutant"):
            _create_enemy_mutant(world, enemy_entity, enemy_info)
        case("Baiter"):
            pass
        case("Pod"):
            pass
        case("Swarmer"):
            pass
        case("Bomber"):
            pass
        case _:
            pass

def _create_enemy_lander(world: esper.World, enemy_entity: int, enemy_info: dict):
    world.add_component(enemy_entity, CLanderState())
    world.add_component(enemy_entity, CSteer(None))
    world.add_component(enemy_entity, CShootDelay(enemy_info["fire_rate"]))

def _create_enemy_mutant(world: esper.World, enemy_entity: int, enemy_info: dict):
    world.add_component(enemy_entity, CChase())
    world.add_component(enemy_entity, CMutantState())
    world.add_component(enemy_entity, CShootDelay(enemy_info["fire_rate"]))

def create_fixed_enemy_spawner(world: esper.World, spawn_events: list[dict], enemy_data: dict):
    spawner_entity = world.create_entity()
    world.add_component(spawner_entity, CEnemySpawner(enemy_data, spawn_events))

def create_random_enemy_spawner(world: esper.World, spawner_info: dict):
    spawner_entity = world.create_entity()
    world.add_component(spawner_entity, CRandomEnemySpawner(spawner_info))
    




