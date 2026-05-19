import esper
import pygame

from src.ecs.components.Enemy.c_lander_state import CLanderState, LanderState
from src.ecs.components.c_astronaut_state import AstronautPhase, CAstronautState
from src.ecs.components.c_lifetime import CLifetime
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet_player import CTagBulletPlayer
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
from src.ecs.components.tags.c_tag_particle import CTagParticle
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.engine.service_locator import ServiceLocator


def _spawn_explosion(world: esper.World, position: pygame.Vector2,
                     explosion_cfg: dict) -> None:
    speed = explosion_cfg.get("particle_speed", 60)
    max_dist = explosion_cfg.get("max_distance", 24)
    color_cfg = explosion_cfg.get("color", {"r": 255, "g": 255, "b": 255})
    color = pygame.Color(color_cfg["r"], color_cfg["g"], color_cfg["b"])
    lifetime = max_dist / max(speed, 1)

    for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        ent = world.create_entity()
        world.add_component(ent, CTransform(pygame.Vector2(position)))
        world.add_component(ent, CVelocity(pygame.Vector2(dx * speed, dy * speed)))
        world.add_component(ent, CSurface(pygame.Vector2(2, 2), color))
        world.add_component(ent, CLifetime(lifetime))
        world.add_component(ent, CTagParticle())


def _free_captured_astronaut(world: esper.World, astro_id: int,
                              falling_velocity: float, sound_fall: str) -> None:
    try:
        astro_state = world.component_for_entity(astro_id, CAstronautState)
    except Exception:
        return
    if astro_state.phase != AstronautPhase.CAPTURED:
        return
    astro_state.phase = AstronautPhase.RESCUED
    world.component_for_entity(astro_id, CVelocity).velocity.y = falling_velocity
    if sound_fall:
        ServiceLocator.sounds_service.play(sound_fall)


def system_collision(world: esper.World, explosion_cfg: dict,
                     lander_cfg: dict, mutant_cfg: dict,
                     astronaut_cfg: dict, points_per_enemy: int) -> int:
    score_delta = 0
    bullets_to_delete: set[int] = set()
    enemies_to_delete: dict[int, bool] = {}  # entity -> is_lander

    bullet_rects: list[tuple[int, pygame.Rect]] = []
    for b_ent, (bt, bs) in world.get_components(CTransform, CSurface):
        if world.has_component(b_ent, CTagBulletPlayer):
            bullet_rects.append((
                b_ent,
                pygame.Rect(int(bt.position.x), int(bt.position.y),
                            bs.area.w, bs.area.h)
            ))

    if not bullet_rects:
        return 0

    for e_ent, (et, es, etag) in world.get_components(CTransform, CSurface, CTagEnemy):
        is_lander = etag.enemy_type == "Lander"
        is_mutant = etag.enemy_type == "Mutant"
        if not (is_lander or is_mutant):
            continue
        if e_ent in enemies_to_delete:
            continue

        e_rect = pygame.Rect(int(et.position.x), int(et.position.y),
                             es.area.w, es.area.h)
        for b_ent, b_rect in bullet_rects:
            if b_ent in bullets_to_delete:
                continue
            if e_rect.colliderect(b_rect):
                bullets_to_delete.add(b_ent)
                enemies_to_delete[e_ent] = is_lander
                score_delta += points_per_enemy
                cfg = lander_cfg if is_lander else mutant_cfg
                sound = cfg.get("sound_die", "")
                if sound:
                    ServiceLocator.sounds_service.play(sound)
                _spawn_explosion(world, et.position.copy(), explosion_cfg)
                break

    # Free astronauts from killed landers before deleting the entity
    falling_vel = astronaut_cfg.get("falling_velocity", 60)
    sound_fall = astronaut_cfg.get("sound_fall", "")
    for e_ent, is_lander in enemies_to_delete.items():
        if is_lander and world.has_component(e_ent, CLanderState):
            lstate = world.component_for_entity(e_ent, CLanderState)
            if (lstate.astronaute_being_abducted is not None
                    and lstate.state == LanderState.ABDUCT):
                _free_captured_astronaut(world, lstate.astronaute_being_abducted,
                                         falling_vel, sound_fall)

    for ent in bullets_to_delete:
        world.delete_entity(ent)
    for ent in enemies_to_delete:
        world.delete_entity(ent)

    return score_delta

def system_enemy_bullet_player_collision(world: esper.World, explosion_cfg: dict) -> None:
    b_components = world.get_components(CTransform, CSurface, CTagEnemyBullet)
    player_components = world.get_components(CTransform, CSurface, CTagPlayer)
    
    for b_ent, (b_transform, b_surface, _) in b_components:
        bullet_rect = pygame.Rect(int(b_transform.position.x), int(b_transform.position.y),
                                  b_surface.area.w, b_surface.area.h)
        
        for p_ent, (p_transform, p_surface, _) in player_components:
            player_rect = pygame.Rect(int(p_transform.position.x), int(p_transform.position.y),
                                      p_surface.area.w, p_surface.area.h)
            
            if bullet_rect.colliderect(player_rect):
                world.delete_entity(b_ent)
                pos = p_transform.position + pygame.Vector2(p_surface.area.w / 2, p_surface.area.h / 2)
                _spawn_explosion(world, pos, explosion_cfg)
                
                #TODO: Handle player damage or death here