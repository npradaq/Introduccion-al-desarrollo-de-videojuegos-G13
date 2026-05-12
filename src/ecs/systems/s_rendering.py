import esper
import pygame

from src.ecs.components.c_parallax import CParallax
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_hud import CTagHUD


def system_rendering(world: esper.World, screen: pygame.Surface,
                     camera_x: float = 0, world_width: int = 0) -> None:
    screen_w = screen.get_width()
    components = world.get_components(CTransform, CSurface)
    for entity, (c_transform, c_surface) in components:
        if not c_surface.visible:
            continue
        if world.has_component(entity, CTagHUD):
            continue
        use_camera = (
            world_width > 0
            and not world.has_component(entity, CParallax)
        )
        if use_camera:
            sx = (c_transform.position.x - camera_x) % world_width
            if sx > screen_w:
                sx -= world_width
            if -c_surface.area.w <= sx <= screen_w:
                screen.blit(c_surface.surface, (sx, c_transform.position.y),
                            c_surface.area)
        else:
            screen.blit(c_surface.surface, c_transform.position, c_surface.area)
