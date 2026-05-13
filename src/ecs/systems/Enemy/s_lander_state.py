import random

import esper
import pygame

from src.ecs.components.Enemy.c_lander_state import CLanderState, LanderState
from src.ecs.components.Enemy.c_steer import CSteer
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_astronauta import CTagAstronauta

def system_lander_state(world: esper.World, delta_time: float, lander_info: dict, screen_height: int, screen_width: int) -> None:
    components = world.get_components(CLanderState, CAnimation, CTransform, CVelocity)

    for entity, (c_ls, c_anim, c_transform, c_velocity) in components:
        if c_ls.state == LanderState.PATROL:
            _do_enemy_lander_patrol(world, entity, delta_time, c_ls, c_anim, c_transform, c_velocity, lander_info)
        elif c_ls.state == LanderState.DESCEND:
            _do_enemy_lander_descend(world, entity, c_ls, c_anim, c_transform, c_velocity, lander_info)
        elif c_ls.state == LanderState.ABDUCT:
            _do_enemy_lander_abduct(world, entity, c_anim, c_transform, c_velocity, lander_info, screen_height, screen_width)
        

def _do_enemy_lander_patrol(world: esper.World, enemy_entity:int, delta_time:float, c_ls: CLanderState,
                             c_anim: CAnimation, c_transform: CTransform, c_velocity: CVelocity, 
                             lander_info: dict):
    _set_animation(c_anim, 0)

    # ==========================================
    # Comprobar si hay astronauta cerca para empezar a descender
    # ==========================================

    astro_components = world.get_components(CTagAstronauta, CTransform)

    for entity, (ctag_astro, t_astro) in astro_components:
        distance_to_astro = (t_astro.position - c_transform.position).length()

        if distance_to_astro < lander_info["descend_distance"]:
            c_ls.astronaute_being_abducted = entity
            c_ls.state = LanderState.DESCEND
            return
        
    # ==========================================
    # Movimiento de patrulla
    # ==========================================

    csteer = world.component_for_entity(enemy_entity, CSteer)

    if csteer.target_position is None:
        csteer.target_position = pygame.Vector2(
            random.uniform(-lander_info["patrol_area_width"], lander_info["patrol_area_width"]) + c_transform.position.x,
            random.uniform(-lander_info["patrol_area_height"],  lander_info["patrol_area_height"] + 30) + c_transform.position.y
        )
    
    to_target = (csteer.target_position - c_transform.position)

    distance = to_target.length()

    if distance < lander_info["patrol_target_radius"]:

        csteer.target_position = pygame.Vector2(
            random.uniform(-lander_info["patrol_area_width"], lander_info["patrol_area_width"]) + c_transform.position.x,
            random.uniform(-lander_info["patrol_area_height"] + 10,  lander_info["patrol_area_height"] + 30) + c_transform.position.y
        )

    direction = to_target.normalize()

    desired_velocity = direction * lander_info["velocity_patrol"]

    c_velocity.velocity += (desired_velocity - c_velocity.velocity) * lander_info["steering_force"] * delta_time


def _do_enemy_lander_descend(world: esper.World, enemy_entity:int, c_ls: CLanderState, c_anim: CAnimation,
                             c_transform: CTransform, c_velocity: CVelocity, lander_info: dict):
    
    _set_animation(c_anim, 0)

    # ==========================================
    # Mover hacia el astronauta a velocidad constante
    # ==========================================

    a_t = world.component_for_entity(c_ls.astronaute_being_abducted, CTransform)
    a_s = world.component_for_entity(c_ls.astronaute_being_abducted, CSurface)
    astro_rect = a_s.surface.get_rect(center=a_t.position)
    
    l_s = world.component_for_entity(enemy_entity, CSurface)
    lander_rect = l_s.surface.get_rect(center=c_transform.position)

    direction = (a_t.position - c_transform.position).normalize()
    c_velocity.velocity = direction * lander_info["velocity_descend"]

    if (lander_rect.colliderect(astro_rect)):
        c_ls.state = LanderState.ABDUCT

def _do_enemy_lander_abduct(world: esper.World, enemy_entity:int , c_anim: CAnimation,
                            c_transform: CTransform, c_velocity: CVelocity, 
                            lander_info: dict, screen_height: int, screen_width: int):
    _set_animation(c_anim, 0)

    # ==========================================
    # Mover hacia arriba al astronauta a velocidad constante
    # ==========================================

    c_velocity.velocity = pygame.Vector2(0, -lander_info["velocity_abduct"])

    if c_transform.position.y >= screen_height + 50:
        world.delete_entity(enemy_entity)


def _set_animation(c_a: CAnimation, num_anim:int):
    if c_a.curret_anim == num_anim:
        return
    c_a.curret_anim = num_anim
    c_a.current_animation_time = 0
    c_a.curr_frame = c_a.animations_list[c_a.curret_anim].start


    

    