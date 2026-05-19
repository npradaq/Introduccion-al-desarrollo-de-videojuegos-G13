import random

import esper
import pygame

from src.create.prefab_creator_enemy import create_enemy_bullet
from src.ecs.components import c_transform
from src.ecs.components.Enemy.c_shoot_delay import CShootDelay
from src.ecs.components.c_transform import CTransform


def shoot_projectile(world:esper.World, player_entity: int, enemy_entity, delta_time: float, bullet_info: dict):
    c_shoot_delay = world.component_for_entity(enemy_entity, CShootDelay)
    
    c_shoot_delay.time_since_last_shot += delta_time

    if c_shoot_delay.time_since_last_shot >= c_shoot_delay.shoot_delay:
        player_transform = world.component_for_entity(player_entity, CTransform)
        enemy_transform = world.component_for_entity(enemy_entity, CTransform)
        distance_to_player = enemy_transform.position.distance_to(player_transform.position)
        to_player = player_transform.position - enemy_transform.position


        if distance_to_player <= c_shoot_delay.shoot_detection_distance:
            direction = to_player.normalize()
            accuracy_offset = pygame.Vector2(
                random.uniform(-c_shoot_delay.acuracy_radius, c_shoot_delay.acuracy_radius),
                random.uniform(-c_shoot_delay.acuracy_radius, c_shoot_delay.acuracy_radius)
            )
            final_direction = (direction).normalize() * c_shoot_delay.bullet_velocity
            
            create_enemy_bullet(world, enemy_transform.position, final_direction, bullet_info)

            c_shoot_delay.time_since_last_shot = 0.0