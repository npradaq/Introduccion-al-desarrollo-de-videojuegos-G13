

import random

import esper
import pygame
from src.ecs.components.Enemy.c_baiter_state import CBaiterState, BaiterState
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.Enemy.s_shoot import shoot_projectile


def system_baiter_state(world: esper.World, delta_time: float, baiter_info: dict, bullet_info:dict, player_entity: int) -> None:
    components = world.get_components(CBaiterState, CAnimation, CTransform, CVelocity)

    for entity, (c_bs, c_anim, c_transform, c_velocity) in components:
        if c_bs.state == BaiterState.APROACH:
            _do_enemy_baiter_approach(world, delta_time, entity, c_bs, c_anim, c_transform, c_velocity, baiter_info, player_entity)
        elif c_bs.state == BaiterState.DASH:
            _do_enemy_baiter_dash(world, delta_time, entity, c_bs, c_anim, c_transform, c_velocity, baiter_info, player_entity, bullet_info)
        elif c_bs.state == BaiterState.REST:
            _do_enemy_baiter_rest(world, delta_time, entity, c_bs, c_anim, c_transform, c_velocity, baiter_info, player_entity)
            
            
def _do_enemy_baiter_approach(world: esper.World, delta_time: float, enemy_entity: int, c_bs: CBaiterState, c_anim: CAnimation, c_transform: CTransform, c_velocity: CVelocity, baiter_info: dict, player_entity: int):
    _set_animation(c_anim, 0)
    
    # =====================================
    # Comprobamos si el jugador está dentro del rango de detección para dashear
    # =====================================

    player_transform = world.component_for_entity(player_entity, CTransform)

    to_player = ( -c_transform.position + player_transform.position )

    distance = player_transform.position.distance_to(c_transform.position)

    if distance <= baiter_info["dash_distance"]:
        c_bs.state = BaiterState.DASH
        
        target = (player_transform.position + pygame.Vector2(
            random.uniform(-baiter_info["dash_offset_radius"], baiter_info["dash_offset_radius"]),
            random.uniform(-baiter_info["dash_offset_radius"], baiter_info["dash_offset_radius"])
        ))
        
        c_bs.target_position = target
        c_bs.dash_time = 1.5
        
        return

    # =====================================
    # dirección al jugador
    # =====================================
    chase_direction = to_player.normalize()


    # =====================================
    # movimiento final
    # =====================================

    desired_velocity = (chase_direction * baiter_info["velocity_approach"])

    c_velocity.velocity += (desired_velocity - c_velocity.velocity) * baiter_info["steering_force"] * delta_time
   
   
def _do_enemy_baiter_dash(world: esper.World, delta_time: float, enemy_entity: int, c_bs: CBaiterState, c_anim: CAnimation, c_transform: CTransform, c_velocity: CVelocity, baiter_info: dict, player_entity: int, bullet_info: dict):
    _set_animation(c_anim, 0)
    
    shoot_projectile(world, player_entity, enemy_entity, delta_time, bullet_info)

    to_target = c_bs.target_position - c_transform.position
    
    c_bs.target_position = to_target.normalize() * 10 + c_bs.target_position

    dash_direction = to_target.normalize()
    c_velocity.velocity = dash_direction * baiter_info["velocity_dash"]
    
    if c_bs.dash_time <= 1:
        c_velocity.velocity = c_velocity.velocity * (c_bs.dash_time)
        
        
    
    
    c_bs.dash_time -= delta_time

    if c_bs.dash_time <= 0:
        c_bs.state = BaiterState.REST
        c_bs.rest_time = 4.0
        
def _do_enemy_baiter_rest(world: esper.World, delta_time: float, enemy_entity: int, c_bs: CBaiterState, c_anim: CAnimation, c_transform: CTransform, c_velocity: CVelocity, baiter_info: dict, player_entity: int):
    _set_animation(c_anim, 0)

    c_velocity.velocity = pygame.Vector2(0, 0)

    c_bs.rest_time -= delta_time

    if c_bs.rest_time <= 0:
        c_bs.state = BaiterState.APROACH
        
def _set_animation(c_a: CAnimation, num_anim: int):

    if c_a.curret_anim == num_anim:
        return

    c_a.curret_anim = num_anim
    c_a.current_animation_time = 0

    c_a.curr_frame = c_a.animations_list[c_a.curret_anim].start