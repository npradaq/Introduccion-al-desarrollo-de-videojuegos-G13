import esper
import pygame

from src.create.prefab_creator_enemy import spawn_swarmers_on_pod_death
from src.ecs.components.Enemy.c_lander_state import CLanderState, LanderState
from src.ecs.components.Enemy.c_pod_state import CPodState
from src.ecs.components.c_astronaut_state import AstronautPhase, CAstronautState
from src.ecs.components.c_lifetime import CLifetime
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_terrain import CTerrain
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut
from src.ecs.components.tags.c_tag_bullet_player import CTagBulletPlayer
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_enemy_bomb import CTagEnemyBomb
from src.ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
from src.ecs.components.tags.c_tag_particle import CTagParticle
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_terrain import CTagTerrain
from src.engine.service_locator import ServiceLocator


def _spawn_explosion(world: esper.World, position: pygame.Vector2,
                     explosion_cfg: dict) -> None:
    # Crea partículas de explosión usando la configuración de efecto.
    speed = explosion_cfg.get("particle_speed", 60)
    max_dist = explosion_cfg.get("max_distance", 24)
    # particle_speed afecta la rapidez de las partículas.
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
    # Libera al astronauta capturado cuando el lander es destruido.
    try:
        astro_state = world.component_for_entity(astro_id, CAstronautState)
    except Exception:
        return
    if astro_state.phase != AstronautPhase.CAPTURED:
        return
    # falling_velocity controla qué tan rápido cae el astronauta liberado.
    astro_state.phase = AstronautPhase.RESCUED

    try:
        astro_transform = world.component_for_entity(astro_id, CTransform)
        astro_surface = world.component_for_entity(astro_id, CSurface)
    except Exception:
        astro_transform = None
        astro_surface = None

    if astro_transform is not None and astro_surface is not None:
        terrain_y = None
        for _, (c_terrain,) in world.get_components(CTerrain,):
            if c_terrain.heights:
                x_index = int(astro_transform.position.x)
                x_index = max(0, min(x_index, len(c_terrain.heights) - 1))
                terrain_y = c_terrain.heights[x_index]
                break

        if terrain_y is not None:
            astro_state.land_y = terrain_y - astro_surface.area.h

    world.component_for_entity(astro_id, CVelocity).velocity.y = falling_velocity
    if sound_fall:
        ServiceLocator.sounds_service.play(sound_fall)


def _rects_collide_wrapped(r_a: pygame.Rect, r_b: pygame.Rect,
                           world_width: int) -> bool:
    for offset in (0, world_width, -world_width):
        if r_a.colliderect(r_b.move(offset, 0)):
            return True
    return False


def system_collision(world: esper.World, explosion_cfg: dict,
                     lander_cfg: dict, mutant_cfg: dict,
                     astronaut_cfg: dict, points_per_enemy: int,
                     world_width: int = 0) -> int:
    # Detecta colisiones entre balas del jugador y enemigos.
    score_delta = 0
    bullets_to_delete: set[int] = set()
    enemies_to_delete: dict[int, bool] = {}  # entity -> is_lander
    # points_per_enemy define el puntaje que da cada enemigo destruido.

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
        is_bomber = etag.enemy_type == "Bomber"
        is_baiter = etag.enemy_type == "Baiter"
        is_bomb = etag.enemy_type == "Bomb"
        is_bullet = etag.enemy_type == "Bullet"
        is_swarmer = etag.enemy_type == "Swarmer"
        is_enemy = (is_lander or is_mutant or is_bomber 
                    or is_baiter or is_bomb or is_bullet
                    or is_swarmer) 
        if not (is_enemy):
            continue
        if e_ent in enemies_to_delete:
            continue

        e_rect = pygame.Rect(int(et.position.x), int(et.position.y),
                             es.area.w, es.area.h)
        for b_ent, b_rect in bullet_rects:
            if b_ent in bullets_to_delete:
                continue
            # Comparar la bala con el rectángulo del enemigo (con wrap).
            if _rects_collide_wrapped(e_rect, b_rect, world_width):
                bullets_to_delete.add(b_ent)
                enemies_to_delete[e_ent] = etag.enemy_type
                score_delta += points_per_enemy
                is_lander = etag.enemy_type == "Lander"
                is_mutant = etag.enemy_type == "Mutant"
                cfg = None
                if is_lander:
                    cfg = lander_cfg
                elif is_mutant:
                    cfg = mutant_cfg
                sound = cfg.get("sound_die", "") if cfg else ""
                if sound:
                    ServiceLocator.sounds_service.play(sound)
                _spawn_explosion(world, et.position.copy(), explosion_cfg)
                break

    # Free astronauts from killed landers before deleting the entity
    falling_vel = astronaut_cfg.get("falling_velocity", 60)
    # falling_velocity define la velocidad de caída cuando un astronauta es liberado.
    sound_fall = astronaut_cfg.get("sound_fall", "")
    for e_ent, enemy_type in enemies_to_delete.items():
        if enemy_type == "Lander" and world.has_component(e_ent, CLanderState):
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


def _player_explosion(world: esper.World, position: pygame.Vector2,
                      explosion_cfg: dict) -> None:
    _spawn_explosion(world, position, explosion_cfg)


def system_player_bullet_hits_captured_astronaut(world: esper.World) -> bool:
    # Detecta si el jugador dispara a un astronauta capturado.
    bullets_to_delete: set[int] = set()
    bullet_rects: list[tuple[int, pygame.Rect]] = []
    for b_ent, (bt, bs) in world.get_components(CTransform, CSurface):
        if world.has_component(b_ent, CTagBulletPlayer):
            bullet_rects.append((
                b_ent,
                pygame.Rect(int(bt.position.x), int(bt.position.y), bs.area.w, bs.area.h)
            ))

    if not bullet_rects:
        return False
    # No hay balas del jugador, no hay penalización.

    captured_astro_entities = []
    for astro_ent, (at, asurf, astate) in world.get_components(
        CTransform, CSurface, CAstronautState
    ):
        if not world.has_component(astro_ent, CTagAstronaut):
            continue
        if astate.phase != AstronautPhase.CAPTURED:
            continue
        astro_rect = pygame.Rect(int(at.position.x), int(at.position.y), asurf.area.w, asurf.area.h)
        captured_astro_entities.append((astro_ent, astro_rect))

    for b_ent, b_rect in bullet_rects:
        for _, astro_rect in captured_astro_entities:
            if b_rect.colliderect(astro_rect):
                bullets_to_delete.add(b_ent)
                break

    for ent in bullets_to_delete:
        world.delete_entity(ent)

    return bool(bullets_to_delete)


def system_player_crash(world: esper.World, explosion_cfg: dict) -> bool:
    # Detecta si el jugador choca con un enemigo o con el terreno.
    # explosion_cfg controla el efecto visual de la explosión.
    players = list(world.get_components(CTransform, CSurface, CTagPlayer))
    if not players:
        return False

    _, (p_transform, p_surface, _) = players[0]
    player_rect = pygame.Rect(
        int(p_transform.position.x),
        int(p_transform.position.y),
        p_surface.area.w,
        p_surface.area.h,
    )

    # 1. Crash with enemies: if the player rectangle overlaps any enemy rectangle.
    for _, (e_transform, e_surface, _) in world.get_components(
        CTransform, CSurface, CTagEnemy
    ):
        enemy_rect = pygame.Rect(
            int(e_transform.position.x),
            int(e_transform.position.y),
            e_surface.area.w,
            e_surface.area.h,
        )
        if player_rect.colliderect(enemy_rect):
            _player_explosion(
                world,
                p_transform.position + pygame.Vector2(
                    p_surface.area.w / 2, p_surface.area.h / 2
                ),
                explosion_cfg,
            )
            return True

    # 2. Crash with terrain: if the bottom of the player goes below the terrain height.
    # Se desactiva esta parte: no termina el juego al tocar el terreno inferior.
    # for _, (c_terrain, _) in world.get_components(CTerrain, CTagTerrain):
    #     terrain_x = int(p_transform.position.x) % c_terrain.world_width
    #     terrain_y = c_terrain.heights[terrain_x]
    #     player_bottom = p_transform.position.y + p_surface.area.h
    #     if player_bottom >= terrain_y:
    #         _player_explosion(
    #             world,
    #             p_transform.position + pygame.Vector2(
    #                 p_surface.area.w / 2, p_surface.area.h / 2
    #             ),
    #             explosion_cfg,
    #         )
    #         return True

    # 3. Do not check astronauts here, so landing on them does not kill the player.
    return False


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
                
def system_enemy_bomb_player_collision(world: esper.World, explosion_cfg: dict) -> None:
    bomb_components = world.get_components(CTransform, CSurface, CTagEnemyBomb)
    player_components = world.get_components(CTransform, CSurface, CTagPlayer)
    
    for b_ent, (b_transform, b_surface, _) in bomb_components:
        bomb_rect = pygame.Rect(int(b_transform.position.x), int(b_transform.position.y),
                                  b_surface.area.w, b_surface.area.h)
        
        for p_ent, (p_transform, p_surface, _) in player_components:
            player_rect = pygame.Rect(int(p_transform.position.x), int(p_transform.position.y),
                                      p_surface.area.w, p_surface.area.h)
            
            if bomb_rect.colliderect(player_rect):
                world.delete_entity(b_ent)
                pos = p_transform.position + pygame.Vector2(p_surface.area.w / 2, p_surface.area.h / 2)
                _spawn_explosion(world, pos, explosion_cfg)
                
                #TODO: Handle player damage or death here
                
def system_bullet_pod_collision(world: esper.World, explosion_cfg: dict) -> None:
    bullet_components = world.get_components(CTransform, CSurface, CTagBulletPlayer)
    pod_components = world.get_components(CTransform, CSurface, CPodState)
    
    for b_ent, (b_transform, b_surface, _) in bullet_components:
        bullet_rect = pygame.Rect(int(b_transform.position.x), int(b_transform.position.y),
                                  b_surface.area.w, b_surface.area.h)
        
        for p_ent, (p_transform, p_surface, c_ps) in pod_components:
            pod_rect = pygame.Rect(int(p_transform.position.x), int(p_transform.position.y),
                                      p_surface.area.w, p_surface.area.h)
            
            if bullet_rect.colliderect(pod_rect):
                world.delete_entity(b_ent)
                world.delete_entity(p_ent)
                
                _spawn_explosion(world, p_transform.position.copy(), explosion_cfg)
                
                spawn_swarmers_on_pod_death(world, p_transform.position.copy(), c_ps.swarmer_count)
                
                