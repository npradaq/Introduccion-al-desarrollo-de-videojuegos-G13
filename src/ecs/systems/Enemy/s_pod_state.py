import esper
import pygame

from src.ecs.components.Enemy.c_pod_state import CPodState, PodState

from src.ecs.components.Enemy.c_chase import CChase

from src.ecs.components.c_animation import CAnimation

from src.ecs.components.c_transform import CTransform

from src.ecs.components.c_velocity import CVelocity


def system_pod_state(
    world: esper.World, delta_time: float, pod_info: dict, player_entity: int
) -> None:

    components = world.get_components(CPodState, CAnimation, CTransform, CVelocity)

    for entity, (c_ps, c_anim, c_transform, c_velocity) in components:

        if c_ps.state == PodState.CHASE:

            _do_enemy_pod_chase(
                world,
                delta_time,
                entity,
                c_ps,
                c_anim,
                c_transform,
                c_velocity,
                pod_info,
                player_entity,
            )


def _do_enemy_pod_chase(
    world: esper.World,
    delta_time: float,
    enemy_entity: int,
    c_ps: CPodState,
    c_anim: CAnimation,
    c_transform: CTransform,
    c_velocity: CVelocity,
    pod_info: dict,
    player_entity: int,
):

    _set_animation(c_anim, 0)

    # =====================================
    # obtener jugador
    # =====================================

    if not world.entity_exists(player_entity):
        return

    player_transform = world.component_for_entity(player_entity, CTransform)

    # =====================================
    # dirección al jugador
    # =====================================

    to_player = player_transform.position - c_transform.position

    distance = c_transform.position.distance_to(player_transform.position)

    direction = to_player.normalize()

    # =====================================
    # steering suave
    # =====================================

    desired_velocity = direction * pod_info["velocity_chase"]

    c_velocity.velocity += (
        (desired_velocity - c_velocity.velocity)
        * pod_info["steering_force"]
        * delta_time
    )


def _set_animation(c_a: CAnimation, num_anim: int):

    if c_a.curret_anim == num_anim:
        return

    c_a.curret_anim = num_anim
    c_a.current_animation_time = 0

    c_a.curr_frame = c_a.animations_list[c_a.curret_anim].start
