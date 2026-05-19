import random

import esper
import pygame

from src.ecs.components.Enemy.c_chase import CChase
from src.ecs.components.Enemy.c_mutant_state import CMutantState, MutantState
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.Enemy.s_shoot import shoot_projectile


def system_mutant_state(world: esper.World, delta_time: float, mutant_info: dict, bullet_info:dict, player_entity: int) -> None:
    components = world.get_components(CMutantState, CAnimation, CTransform, CVelocity)

    for entity, (c_ms, c_anim, c_transform, c_velocity) in components:
        if c_ms.state == MutantState.CHASE:
            _do_enemy_mutant_chase(world, delta_time, entity, c_ms, c_anim, c_transform, c_velocity, mutant_info, player_entity, bullet_info)

def _do_enemy_mutant_chase(world: esper.World, delta_time: float, enemy_entity: int,  c_ms: CMutantState, c_anim: CAnimation, 
                           c_transform: CTransform, c_velocity: CVelocity, mutant_info: dict, player_entity: int, bullet_info: dict) -> None:

    _set_animation(c_anim, 0)
    
    shoot_projectile(world, player_entity, enemy_entity, delta_time, bullet_info)

    player_transform = world.component_for_entity(player_entity, CTransform)

    c_chase = world.component_for_entity(enemy_entity, CChase)

    # =====================================
    # dirección al jugador
    # =====================================

    to_player = (player_transform.position - c_transform.position)

    distance = to_player.length()

    if distance == 0:
        return

    chase_direction = to_player.normalize()

    # =====================================
    # timer de jerk
    # =====================================

    c_chase.direction_timer -= delta_time

    if c_chase.direction_timer <= 0:

        c_chase.direction_timer = random.uniform(mutant_info["jerk_interval_min"],
                                                  mutant_info["jerk_interval_max"])

        # intensidad aumenta al acercarse
        proximity_factor = max( 0, 1 - (distance / mutant_info["max_jerk_distance"]))

        jerk_strength = random.uniform(mutant_info["jerk_strength_min"],
                                        mutant_info["jerk_strength_max"]) * proximity_factor

        # perpendicular aleatoria
        perpendicular = pygame.Vector2(-chase_direction.y, chase_direction.x)

        if random.random() < 0.5:
            perpendicular *= -1

        c_chase.jerk_direction = (perpendicular * jerk_strength)

    # =====================================
    # movimiento final
    # =====================================

    desired_velocity = (chase_direction * mutant_info["velocity_chase"]) + c_chase.jerk_direction

    c_velocity.velocity += (desired_velocity - c_velocity.velocity) * mutant_info["steering_force"] * delta_time





def _set_animation(c_a: CAnimation, num_anim:int):
    if c_a.curret_anim == num_anim:
        return
    c_a.curret_anim = num_anim
    c_a.current_animation_time = 0
    c_a.curr_frame = c_a.animations_list[c_a.curret_anim].start
