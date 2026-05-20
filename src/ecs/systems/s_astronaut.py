import esper
import pygame

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_astronaut_state import AstronautPhase, CAstronautState
from src.ecs.components.c_attach_to import CAttachTo
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_terrain import CTerrain
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut
from src.engine.service_locator import ServiceLocator


def _get_terrain_heights(world: esper.World) -> list[float]:
    for _, (ct,) in world.get_components(CTerrain):
        return ct.heights
    return []


def system_astronaut(world: esper.World, astronaut_cfg: dict,
                     points_per_rescued: int, camera_x: float,
                     world_width: int, font_path: str,
                     popup_size: int = 6) -> int:
    from src.create.prefab_creator import create_score_popup

    score_delta = 0
    sound_rescued = astronaut_cfg.get("sound_rescued", "")
    terrain_heights = _get_terrain_heights(world)

    for ent, (ct, cv, cs, canim, cstate) in world.get_components(
            CTransform, CVelocity, CSurface, CAnimation, CAstronautState):
        if not world.has_component(ent, CTagAstronaut):
            continue

        if cstate.phase == AstronautPhase.FALLING:
            if ct.position.y >= cstate.land_y:
                ct.position.y = cstate.land_y
                cv.velocity.y = 0
                cstate.phase = AstronautPhase.LANDED

        elif cstate.phase == AstronautPhase.RESCUED:
            if ct.position.y >= cstate.land_y:
                ct.position.y = cstate.land_y
                cv.velocity.y = 0
                cstate.phase = AstronautPhase.LANDED
                score_delta += points_per_rescued
                if sound_rescued:
                    ServiceLocator.sounds_service.play(sound_rescued)
                screen_x = (ct.position.x - camera_x) % world_width
                create_score_popup(
                    world, screen_x + 8, ct.position.y - 12,
                    points_per_rescued, font_path, popup_size
                )

        elif cstate.phase == AstronautPhase.CARRYING:
            if cstate.just_picked_up:
                cstate.just_picked_up = False
                continue
            if not terrain_heights:
                continue
            xi = int(ct.position.x) % len(terrain_heights)
            land_y = terrain_heights[xi] - cs.area.h
            if ct.position.y >= land_y:
                if world.has_component(ent, CAttachTo):
                    world.remove_component(ent, CAttachTo)
                ct.position.y = land_y
                cstate.land_y = land_y
                cv.velocity = pygame.Vector2(0, 0)
                cstate.phase = AstronautPhase.LANDED
                canim.paused = False
                score_delta += points_per_rescued
                if sound_rescued:
                    ServiceLocator.sounds_service.play(sound_rescued)
                screen_x = (ct.position.x - camera_x) % world_width
                create_score_popup(
                    world, screen_x + 8, ct.position.y - 12,
                    points_per_rescued, font_path, popup_size
                )

    return score_delta
