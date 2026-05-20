import random

import esper
import pygame

from src.create.prefab_creator_enemy import create_enemy_bomb
from src.ecs.components.Enemy.c_bomber_state import BomberState, CBomberState
from src.ecs.components.Enemy.c_steer import CSteer
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity


def system_bomber_state(
    world: esper.World,
    delta_time: float,
    bomber_info: dict,
    world_height: int,
    world_width: int,
) -> None:
    components = world.get_components(CBomberState, CAnimation, CTransform, CVelocity)

    for entity, (c_bs, c_anim, c_transform, c_velocity) in components:
        if c_bs.state == BomberState.ROAM:
            _do_enemy_bomber_roam(
                world,
                delta_time,
                entity,
                c_bs,
                c_anim,
                c_transform,
                c_velocity,
                bomber_info,
                world_height,
                world_width,
            )


def _do_enemy_bomber_roam(
    world: esper.World,
    delta_time: float,
    enemy_entity: int,
    c_bs: CBomberState,
    c_anim: CAnimation,
    c_transform: CTransform,
    c_velocity: CVelocity,
    bomber_info: dict,
    world_height: int,
    world_width: int,
):
    _set_animation(c_anim, 0)

    # =====================================
    # lógica de movimiento
    # =====================================

    c_steer = world.component_for_entity(enemy_entity, CSteer)

    # =====================================
    # generar target inicial
    # =====================================

    if c_steer.target_position is None:

        margin = bomber_info["target_area_margin"]

        c_steer.target_position = pygame.Vector2(
            random.uniform(margin, world_width - margin),
            random.uniform(margin, world_height - margin),
        )

    # =====================================
    # movimiento hacia target
    # =====================================

    to_target = c_steer.target_position - c_transform.position

    distance = c_transform.position.distance_to(c_steer.target_position)

    # =====================================
    # cambiar target
    # =====================================

    if distance < bomber_info["radius_target_change"]:

        margin = bomber_info["target_area_margin"]

        c_steer.target_position = pygame.Vector2(
            random.uniform(margin, world_width - margin),
            random.uniform(margin, world_height - margin),
        )

        return

    # =====================================
    # steering suave
    # =====================================

    direction = to_target.normalize()

    desired_velocity = direction * bomber_info["velocity_roam"]

    c_velocity.velocity += (
        (desired_velocity - c_velocity.velocity)
        * bomber_info["steering_force"]
        * delta_time
    )

    # =====================================
    # lógica de lanzamiento de bombas
    # =====================================
    c_bs.bomb_drop_time -= delta_time

    if c_bs.bomb_drop_time <= 0:
        c_bs.bomb_drop_time = bomber_info["bomb_drop_rate"]
        create_enemy_bomb(world, c_transform.position)


def _set_animation(c_a: CAnimation, num_anim: int):

    if c_a.curret_anim == num_anim:
        return

    c_a.curret_anim = num_anim
    c_a.current_animation_time = 0

    c_a.curr_frame = c_a.animations_list[c_a.curret_anim].start
