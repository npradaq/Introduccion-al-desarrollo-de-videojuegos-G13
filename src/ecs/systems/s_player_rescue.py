import esper
import pygame

from src.ecs.components.c_astronaut_state import AstronautPhase, CAstronautState
from src.ecs.components.c_attach_to import CAttachTo
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.engine.service_locator import ServiceLocator


def system_player_rescue(world: esper.World, points_per_rescued: int,
                         camera_x: float, world_width: int,
                         astro_cfg: dict, font_path: str,
                         popup_size: int = 6) -> int:
    from src.create.prefab_creator import create_score_popup

    player_entity: int | None = None
    player_rect: pygame.Rect | None = None
    player_h: int = 0
    player_w: int = 0

    for ent, (ct, cs) in world.get_components(CTransform, CSurface):
        if world.has_component(ent, CTagPlayer):
            player_entity = ent
            player_rect = pygame.Rect(
                int(ct.position.x), int(ct.position.y), cs.area.w, cs.area.h
            )
            player_h = cs.area.h
            player_w = cs.area.w
            break

    if player_entity is None or player_rect is None:
        return 0

    sound_rescued = astro_cfg.get("sound_rescued", "")
    score_delta = 0

    for ent, (ct, cs, cv, cstate) in world.get_components(
            CTransform, CSurface, CVelocity, CAstronautState):
        if not world.has_component(ent, CTagAstronaut):
            continue
        if cstate.phase != AstronautPhase.RESCUED:
            continue
        if world.has_component(ent, CAttachTo):
            continue

        astro_rect = pygame.Rect(
            int(ct.position.x), int(ct.position.y), cs.area.w, cs.area.h
        )
        collides = any(
            player_rect.colliderect(astro_rect.move(offset, 0))
            for offset in (0, world_width, -world_width)
        )
        if not collides:
            continue

        offset_x = (player_w - cs.area.w) / 2
        offset = pygame.Vector2(offset_x, float(player_h))
        world.add_component(ent, CAttachTo(player_entity, offset))
        cv.velocity = pygame.Vector2(0, 0)
        cstate.phase = AstronautPhase.CARRYING
        cstate.just_picked_up = True

        player_ct = world.component_for_entity(player_entity, CTransform)
        ct.position.x = player_ct.position.x + offset.x
        ct.position.y = player_ct.position.y + offset.y

        screen_x = (ct.position.x - camera_x) % world_width
        create_score_popup(world, screen_x + 8, ct.position.y - 12,
                           points_per_rescued, font_path, popup_size)
        if sound_rescued:
            ServiceLocator.sounds_service.play(sound_rescued)
        score_delta += points_per_rescued

    return score_delta
