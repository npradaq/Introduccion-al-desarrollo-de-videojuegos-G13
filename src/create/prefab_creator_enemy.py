import random

import esper
import pygame

from src.create.prefab_creator import create_sprite
from src.ecs.components.Enemy.c_baiter_state import CBaiterState
from src.ecs.components.Enemy.c_bomber_state import CBomberState
from src.ecs.components.Enemy.c_chase import CChase
from src.ecs.components.Enemy.c_fixed_enemy_spawner import CEnemySpawner
from src.ecs.components.Enemy.c_lander_state import CLanderState
from src.ecs.components.Enemy.c_mutant_state import CMutantState
from src.ecs.components.Enemy.c_random_enemy_spawner import CRandomEnemySpawner
from src.ecs.components.Enemy.c_shoot_delay import CShootDelay
from src.ecs.components.Enemy.c_steer import CSteer
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_enemy_bomb import CTagEnemyBomb
from src.ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
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
            _create_enemy_baiter(world, enemy_entity, enemy_info)
        case("Pod"):
            _create_enemy_pod(world, enemy_entity, enemy_info)
        case("Swarmer"):
            _create_enemy_swarmer(world, enemy_entity, enemy_info)
        case("Bomber"):
            _create_enemy_bomber(world, enemy_entity, enemy_info)
        case _:
            print(f"Enemy type {enemy_type} not recognized.")

def _create_enemy_lander(world: esper.World, enemy_entity: int, enemy_info: dict):
    world.add_component(enemy_entity, CLanderState())
    world.add_component(enemy_entity, CSteer(None))
    world.add_component(enemy_entity, CShootDelay(enemy_info["fire_rate"], enemy_info["acuracy_radius"],
                                                  enemy_info["shoot_detection_distance"], enemy_info["bullet_velocity"]))

def _create_enemy_mutant(world: esper.World, enemy_entity: int, enemy_info: dict):
    world.add_component(enemy_entity, CChase())
    world.add_component(enemy_entity, CMutantState())
    world.add_component(enemy_entity, CShootDelay(enemy_info["fire_rate"], enemy_info["acuracy_radius"],
                                                  enemy_info["shoot_detection_distance"], enemy_info["bullet_velocity"]))
    
def _create_enemy_baiter(world: esper.World, enemy_entity: int, enemy_info: dict):
    world.add_component(enemy_entity, CBaiterState())
    world.add_component(enemy_entity, CShootDelay(enemy_info["fire_rate"], enemy_info["acuracy_radius"],
                                                  enemy_info["shoot_detection_distance"], enemy_info["bullet_velocity"]))

def _create_enemy_pod(world: esper.World, enemy_entity: int, enemy_info: dict):
    pass

def _create_enemy_swarmer(world: esper.World, enemy_entity: int, enemy_info: dict):
    pass

def _create_enemy_bomber(world: esper.World, enemy_entity: int, enemy_info: dict):
    world.add_component(enemy_entity, CBomberState())
    world.add_component(enemy_entity, CSteer(None))
    
def create_enemy_bomb(world: esper.World, pos: pygame.Vector2):
    bomb_data = ServiceLocator.config_service.get("assets/cfg/enemies.json")["Bomb"]
    bomb_surface = ServiceLocator.images_service.get(bomb_data["image"])
    bomb_entity = create_sprite(world, pos, pygame.Vector2(0,0), bomb_surface)
    world.add_component(bomb_entity, CTagEnemyBomb())
    world.add_component(bomb_entity, CAnimation(bomb_data["animations"]))
    world.add_component(bomb_entity, CTagEnemy("Bomb"))

def create_enemy_bullet(world: esper.World, pos: pygame.Vector2, direction: pygame.Vector2, bullet_info: dict):
    bullet_surface = ServiceLocator.images_service.get(bullet_info["image"])
    bullet_entity = create_sprite(world, pos, direction, bullet_surface)
    world.add_component(bullet_entity, CTagEnemyBullet())
    world.add_component(bullet_entity, CTagEnemy("Bullet"))

def create_fixed_enemy_spawner(world: esper.World, spawn_events: list[dict], enemy_data: dict):
    spawner_entity = world.create_entity()
    world.add_component(spawner_entity, CEnemySpawner(enemy_data, spawn_events))

def create_random_enemy_spawner(world: esper.World, spawner_info: dict):
    spawner_entity = world.create_entity()
    world.add_component(spawner_entity, CRandomEnemySpawner(spawner_info))
    




