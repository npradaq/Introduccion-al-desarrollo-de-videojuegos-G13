import random

import esper
import pygame

from src.ecs.components.Enemy.c_swarmer_state import CSwarmerState, SwarmerState

from src.ecs.components.c_animation import CAnimation

from src.ecs.components.c_transform import CTransform

from src.ecs.components.c_velocity import CVelocity

from src.ecs.systems.Enemy.s_shoot import shoot_projectile


def system_swarmer_state(
    world: esper.World, delta_time: float, swarmer_info: dict, bullet_info: dict, player_entity: int
) -> None:

    components = world.get_components(
        CSwarmerState, CAnimation, CTransform, CVelocity
    )

    for entity, (c_ss, c_anim, c_transform, c_velocity) in components:

        if c_ss.state == SwarmerState.CHASE:

            _do_enemy_swarmer_chase(
                world,
                delta_time,
                entity,
                c_ss,
                c_anim,
                c_transform,
                c_velocity,
                swarmer_info,
                bullet_info,
                player_entity,
            )


def _do_enemy_swarmer_chase(
    world: esper.World,
    delta_time: float,
    enemy_entity: int,
    c_ss: CSwarmerState,
    c_anim: CAnimation,
    c_transform: CTransform,
    c_velocity: CVelocity,
    swarmer_info: dict,
    bullet_info: dict,
    player_entity: int,
    
):

    _set_animation(c_anim, 0)

    # =====================================
    # validar jugador
    # =====================================

    if not world.entity_exists(player_entity):
        return

    player_transform = world.component_for_entity(player_entity, CTransform)

    # =====================================
    # dirección al jugador
    # =====================================

    to_player = player_transform.position - c_transform.position
    
    to_player = to_player + pygame.Vector2(random.uniform(-swarmer_info["acuracy_radius"], swarmer_info["acuracy_radius"]),
                                            random.uniform(-swarmer_info["acuracy_radius"], swarmer_info["acuracy_radius"]))*2

    direction = to_player.normalize()

    # =====================================
    # steering suave
    # =====================================

    desired_velocity = direction * swarmer_info["velocity_chase"]

    c_velocity.velocity += (
        (desired_velocity - c_velocity.velocity)
        * swarmer_info["steering_force"]
        * delta_time
    )

    # =====================================
    # disparo
    # =====================================

    shoot_projectile(
        world, player_entity, enemy_entity, delta_time, bullet_info
    )


def _set_animation(c_a: CAnimation, num_anim: int):

    if c_a.curret_anim == num_anim:
        return

    c_a.curret_anim = num_anim
    c_a.current_animation_time = 0

    c_a.curr_frame = c_a.animations_list[c_a.curret_anim].start
