import random

import esper
import pygame

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_astronaut_state import AstronautPhase, CAstronautState
from src.ecs.components.c_lander_state import CLanderState, LanderPhase
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut
from src.ecs.components.tags.c_tag_lander_enemy import CTagLanderEnemy
from src.ecs.components.tags.c_tag_mutant_enemy import CTagMutantEnemy
from src.engine.service_locator import ServiceLocator


def _find_nearest_landed_astronaut(world: esper.World, lander_x: float,
                                    detection_range: float) -> int | None:
    best_id = None
    best_dist = float("inf")
    for astro_id, (at, _) in world.get_components(CTransform, CTagAstronaut):
        if not world.has_component(astro_id, CAstronautState):
            continue
        astro_state = world.component_for_entity(astro_id, CAstronautState)
        if astro_state.phase != AstronautPhase.LANDED:
            continue
        dist = abs(at.position.x - lander_x)
        if dist <= detection_range and dist < best_dist:
            best_dist = dist
            best_id = astro_id
    return best_id


def _patrol(lander_t: CTransform, lander_v: CVelocity, lander_state: CLanderState,
            dt: float, world_width: int, screen_h: int, lander_cfg: dict) -> None:
    speed = lander_cfg.get("velocity_patrol", 40)

    # Assign initial velocity on first tick
    if lander_v.velocity.length() == 0:
        lander_v.velocity.x = random.choice((-1, 1)) * speed
        lander_v.velocity.y = random.uniform(-speed * 0.5, speed * 0.5)

    lander_state.patrol_timer += dt
    if lander_state.patrol_timer >= lander_state.patrol_change_interval:
        lander_state.patrol_timer = 0.0
        lander_state.patrol_change_interval = random.uniform(1.5, 3.5)
        lander_v.velocity.x = random.choice((-1, 1)) * speed
        lander_v.velocity.y = random.uniform(-speed * 0.5, speed * 0.5)

    # Clamp vertical to upper portion of game area
    if lander_t.position.y < screen_h * 0.05:
        lander_v.velocity.y = abs(lander_v.velocity.y)
    elif lander_t.position.y > screen_h * 0.6:
        lander_v.velocity.y = -abs(lander_v.velocity.y)

    # Wrap horizontally
    if world_width > 0:
        if lander_t.position.x < 0:
            lander_t.position.x += world_width
        elif lander_t.position.x >= world_width:
            lander_t.position.x -= world_width


def _descend(world: esper.World, lander_t: CTransform, lander_v: CVelocity,
             lander_s: CSurface, lander_state: CLanderState,
             lander_cfg: dict) -> None:
    astro_id = lander_state.target_astronaut_id
    if astro_id is None:
        lander_state.phase = LanderPhase.PATROL
        return

    try:
        astro_t = world.component_for_entity(astro_id, CTransform)
        astro_state = world.component_for_entity(astro_id, CAstronautState)
    except Exception:
        lander_state.phase = LanderPhase.PATROL
        lander_state.target_astronaut_id = None
        return

    if astro_state.phase != AstronautPhase.LANDED:
        lander_state.phase = LanderPhase.PATROL
        lander_state.target_astronaut_id = None
        return

    speed = lander_cfg.get("velocity_descend", 60)
    target_y = astro_t.position.y - lander_s.area.h
    diff_x = astro_t.position.x - lander_t.position.x
    diff_y = target_y - lander_t.position.y
    dist = (diff_x ** 2 + diff_y ** 2) ** 0.5

    if dist > 2:
        lander_v.velocity.x = (diff_x / dist) * speed
        lander_v.velocity.y = (diff_y / dist) * speed
    else:
        lander_v.velocity = pygame.Vector2(0, 0)
        lander_t.position.y = target_y
        lander_t.position.x = astro_t.position.x

        astro_state.phase = AstronautPhase.CAPTURED
        world.component_for_entity(astro_id, CVelocity).velocity = pygame.Vector2(0, 0)
        if world.has_component(astro_id, CAnimation):
            world.component_for_entity(astro_id, CAnimation).paused = True

        sound = lander_cfg.get("sound_capture", "")
        if sound:
            ServiceLocator.sounds_service.play(sound)

        lander_state.phase = LanderPhase.ABDUCT


def _abduct(world: esper.World, lander_t: CTransform, lander_v: CVelocity,
            lander_s: CSurface, lander_state: CLanderState,
            lander_ent: int, lander_cfg: dict) -> tuple | None:
    """Returns (lander_ent, position, astro_id) if transformation should trigger."""
    astro_id = lander_state.target_astronaut_id
    speed = lander_cfg.get("velocity_abduct", 50)
    lander_v.velocity = pygame.Vector2(0, -speed)

    if astro_id is not None:
        try:
            astro_t = world.component_for_entity(astro_id, CTransform)
            astro_t.position.x = lander_t.position.x
            astro_t.position.y = lander_t.position.y + lander_s.area.h
        except Exception:
            lander_state.target_astronaut_id = None

    if lander_t.position.y <= 0:
        return (lander_ent, lander_t.position.copy(), astro_id)
    return None


def system_lander(world: esper.World, dt: float, screen_h: int,
                  world_width: int, player_entity: int | None,
                  lander_cfg: dict, mutant_cfg: dict) -> None:
    from src.create.prefab_creator import create_mutant_enemy

    transformations: list[tuple[int, pygame.Vector2, int | None]] = []

    for lander_ent, (lt, lv, ls, lstate) in world.get_components(
            CTransform, CVelocity, CSurface, CLanderState):
        if not world.has_component(lander_ent, CTagLanderEnemy):
            continue

        if lstate.phase == LanderPhase.PATROL:
            _patrol(lt, lv, lstate, dt, world_width, screen_h, lander_cfg)
            if lstate.initial_patrol_remaining > 0:
                lstate.initial_patrol_remaining -= dt
            else:
                detection_range = lander_cfg.get("astronaut_detection_range", 120)
                astro_id = _find_nearest_landed_astronaut(
                    world, lt.position.x, detection_range)
                if astro_id is not None:
                    lstate.target_astronaut_id = astro_id
                    lstate.phase = LanderPhase.DESCEND
                    lv.velocity = pygame.Vector2(0, 0)

        elif lstate.phase == LanderPhase.DESCEND:
            _descend(world, lt, lv, ls, lstate, lander_cfg)

        elif lstate.phase == LanderPhase.ABDUCT:
            result = _abduct(world, lt, lv, ls, lstate, lander_ent, lander_cfg)
            if result is not None:
                transformations.append(result)

    # Process mutations after the loop to avoid modifying world mid-iteration
    for lander_ent, pos, astro_id in transformations:
        sound = lander_cfg.get("sound_mutate", "")
        if sound:
            ServiceLocator.sounds_service.play(sound)
        if astro_id is not None:
            world.delete_entity(astro_id)
        world.delete_entity(lander_ent)
        create_mutant_enemy(world, mutant_cfg, pos)

    # Mutants chase the player
    if player_entity is None:
        return
    try:
        player_t = world.component_for_entity(player_entity, CTransform)
    except Exception:
        return

    mutant_speed = mutant_cfg.get("velocity_chase", 90)
    for m_ent, (mt, mv) in world.get_components(CTransform, CVelocity):
        if not world.has_component(m_ent, CTagMutantEnemy):
            continue
        direction = player_t.position - mt.position
        dist = direction.length()
        if dist > 0:
            mv.velocity = direction.normalize() * mutant_speed
