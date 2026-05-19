import random

import esper
import pygame

from src.create.prefab_creator_enemy import create_enemy
from src.ecs.components.Enemy.c_lander_state import CLanderState, LanderState

from src.ecs.components.Enemy.c_steer import CSteer

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_astronaut_state import AstronautPhase, CAstronautState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut
from src.ecs.systems.Enemy.s_shoot import shoot_projectile
from src.engine.service_locator import ServiceLocator
from src.engine.services.config_service import ConfigService


def system_lander_state(
    world: esper.World,
    delta_time: float,
    lander_info: dict,
    bullet_info: dict,
    player_entity: int,
    screen_height: int,
    screen_width: int,
) -> None:

    components = world.get_components(CLanderState, CAnimation, CTransform, CVelocity)

    for entity, (c_ls, c_anim, c_transform, c_velocity) in components:

        if c_ls.state == LanderState.PATROL:

            _do_enemy_lander_patrol(
                world,
                entity,
                delta_time,
                c_ls,
                c_anim,
                c_transform,
                c_velocity,
                lander_info,
                screen_height,
                screen_width,
                player_entity,
                bullet_info
            )

        elif c_ls.state == LanderState.DESCEND:

            _do_enemy_lander_descend(
                world, entity, c_ls, c_anim, c_transform, c_velocity, lander_info
            )

        elif c_ls.state == LanderState.ABDUCT:

            _do_enemy_lander_abduct(
                world,
                entity,
                c_ls,
                c_anim,
                c_transform,
                c_velocity,
                lander_info,
                screen_height,
                screen_width,
            )


def _find_nearest_astronaut(
    world: esper.World, lander_position: pygame.Vector2, detection_distance: float
):

    nearest_entity = None
    nearest_distance = float("inf")

    astro_components = world.get_components(CTagAstronaut, CTransform)

    for entity, (_, t_astro) in astro_components:

        distance = (t_astro.position - lander_position).length()

        if distance < detection_distance and distance < nearest_distance:

            nearest_distance = distance
            nearest_entity = entity

    return nearest_entity


def _do_enemy_lander_patrol(
    world: esper.World,
    enemy_entity: int,
    delta_time: float,
    c_ls: CLanderState,
    c_anim: CAnimation,
    c_transform: CTransform,
    c_velocity: CVelocity,
    lander_info: dict,
    screen_height: int,
    world_width: int,
    player_entity: int,
    bullet_info: dict
):

    _set_animation(c_anim, 0)
    
    shoot_projectile(world, player_entity, enemy_entity, delta_time, bullet_info) 

    csteer = world.component_for_entity(enemy_entity, CSteer)

    # ==========================================
    # Delay inicial antes de buscar astronautas
    # ==========================================

    if c_ls.initial_patrol_remaining > 0:

        c_ls.initial_patrol_remaining -= delta_time

    else:

        nearest_astro = _find_nearest_astronaut(
            world, c_transform.position, lander_info["astronaut_detection_range"]
        )

        if nearest_astro is not None:
            
            astro_state = world.component_for_entity(nearest_astro, CAstronautState)
            
            if astro_state.phase == AstronautPhase.LANDED:

                c_ls.astronaute_being_abducted = nearest_astro

                c_ls.state = LanderState.DESCEND

                return

    # ==========================================
    # Generar target inicial
    # ==========================================

    if csteer.target_position is None:

        csteer.target_position = pygame.Vector2(
            random.uniform(
                -lander_info["patrol_area_width"], lander_info["patrol_area_width"]
            )
            + c_transform.position.x,
            random.uniform(
                -lander_info["patrol_area_height"], lander_info["patrol_area_height"]
            )
            + c_transform.position.y,
        )

    # ==========================================
    # Mantener patrol en banda vertical
    # ==========================================

    upper_limit = screen_height * lander_info["patrol_upper_limit"]

    lower_limit = screen_height * lander_info["patrol_lower_limit"]

    if c_transform.position.y < upper_limit:

        csteer.target_position.y = max(csteer.target_position.y, upper_limit + 50)

    elif c_transform.position.y > lower_limit:

        csteer.target_position.y = min(csteer.target_position.y, lower_limit - 50)

    # ==========================================
    # Horizontal wrapping
    # ==========================================

    if c_transform.position.x < 0:

        c_transform.position.x += world_width

    elif c_transform.position.x >= world_width:

        c_transform.position.x -= world_width

    # ==========================================
    # Movimiento de patrulla
    # ==========================================

    to_target = csteer.target_position - c_transform.position

    distance = to_target.length()

    if distance < lander_info["patrol_target_radius"]:

        csteer.target_position = pygame.Vector2(
            random.uniform(
                -lander_info["patrol_area_width"], lander_info["patrol_area_width"]
            )
            + c_transform.position.x,
            random.uniform(
                -lander_info["patrol_area_height"], lander_info["patrol_area_height"]
            )
            + c_transform.position.y,
        )

        return

    direction = to_target.normalize()

    desired_velocity = direction * lander_info["velocity_patrol"]

    c_velocity.velocity += (
        (desired_velocity - c_velocity.velocity)
        * lander_info["steering_force"]
        * delta_time
    )


def _do_enemy_lander_descend(
    world: esper.World,
    enemy_entity: int,
    c_ls: CLanderState,
    c_anim: CAnimation,
    c_transform: CTransform,
    c_velocity: CVelocity,
    lander_info: dict,
):

    _set_animation(c_anim, 0)

    # ==========================================
    # Validar astronauta
    # ==========================================

    if c_ls.astronaute_being_abducted is None or not world.entity_exists(
        c_ls.astronaute_being_abducted
    ):
        

        c_ls.state = LanderState.PATROL
        c_ls.astronaute_being_abducted = None

        return
    
    astro_state = world.component_for_entity(c_ls.astronaute_being_abducted, CAstronautState)
    
    if astro_state.phase != AstronautPhase.LANDED:

        c_ls.state = LanderState.PATROL
        c_ls.astronaute_being_abducted = None

        return

    # ==========================================
    # Obtener componentes astronauta
    # ==========================================

    a_t = world.component_for_entity(c_ls.astronaute_being_abducted, CTransform)

    a_s = world.component_for_entity(c_ls.astronaute_being_abducted, CSurface)

    astro_rect = a_s.surface.get_rect(center=a_t.position)

    l_s = world.component_for_entity(enemy_entity, CSurface)

    lander_rect = l_s.surface.get_rect(center=c_transform.position)

    # ==========================================
    # Movimiento descendente suave
    # ==========================================

    to_astro = a_t.position - c_transform.position

    distance = to_astro.length()

    if distance > 0:

        direction = to_astro.normalize()

        desired_velocity = direction * lander_info["velocity_descend"]

        c_velocity.velocity += (desired_velocity - c_velocity.velocity) * lander_info[
            "descend_steering_force"
        ]

    # ==========================================
    # Colisión astronauta
    # ==========================================

    if lander_rect.colliderect(astro_rect):

        c_ls.state = LanderState.ABDUCT
        
        astro_state = world.component_for_entity(c_ls.astronaute_being_abducted, CAstronautState)
        astro_state.phase = AstronautPhase.CAPTURED


def _do_enemy_lander_abduct(
        world: esper.World,
        enemy_entity: int,
        c_ls: CLanderState,
        c_anim: CAnimation,
        c_transform: CTransform,
        c_velocity: CVelocity,
        lander_info: dict,
        screen_height: int,
        screen_width: int):

    _set_animation(c_anim, 0)

    # ==========================================
    # Movimiento vertical
    # ==========================================

    desired_velocity = pygame.Vector2(
        0,
        -lander_info["velocity_abduct"]
    )

    c_velocity.velocity += (
        desired_velocity
        - c_velocity.velocity
    ) * lander_info["abduct_steering_force"]

    # ==========================================
    # Mantener astronauta pegado
    # ==========================================

    if (
        c_ls.astronaute_being_abducted is not None
        and
        world.entity_exists(
            c_ls.astronaute_being_abducted
        )
    ):

        astro_t = world.component_for_entity(
            c_ls.astronaute_being_abducted,
            CTransform
        )

        lander_surface = world.component_for_entity(
            enemy_entity,
            CSurface
        )

        astro_t.position.x = c_transform.position.x

        astro_t.position.y = (
            c_transform.position.y
            +
            lander_surface.surface.get_height()
        )

    # ==========================================
    # Eliminar fuera de pantalla
    # ==========================================

    if c_transform.position.y <= -50:

        if (
            c_ls.astronaute_being_abducted is not None
            and
            world.entity_exists(
                c_ls.astronaute_being_abducted
            )
        ):

            world.delete_entity(
                c_ls.astronaute_being_abducted
            )

        world.delete_entity(enemy_entity)
        
        create_enemy(world, c_transform.position, 
                     ServiceLocator.config_service.get("assets/cfg/enemies.json")["Mutant"], "Mutant")


def _set_animation(c_a: CAnimation, num_anim: int):

    if c_a.curret_anim == num_anim:
        return

    c_a.curret_anim = num_anim
    c_a.current_animation_time = 0

    c_a.curr_frame = c_a.animations_list[c_a.curret_anim].start
