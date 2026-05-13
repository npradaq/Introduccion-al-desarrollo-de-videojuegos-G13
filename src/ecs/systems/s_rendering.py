import esper
import pygame

from src.ecs.components.c_parallax import CParallax
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_hud import CTagHUD
from src.engine.service_locator import ServiceLocator


def system_rendering(world: esper.World, screen: pygame.Surface,
                     camera_x: float = 0, world_width: int = 0) -> None:
    screen_w = screen.get_width()
    components = world.get_components(CTransform, CSurface)
    for entity, (c_transform, c_surface) in components:
        if not c_surface.visible:
            continue
        use_camera = (
            world_width > 0
            and not world.has_component(entity, CParallax)
            and not world.has_component(entity, CTagHUD)
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

    text_components = world.get_components(CTransform, CText)
    for entity, (c_transform, c_text) in text_components:
        if not c_text.visible:
            continue
        if c_text.surface is None:
            font = ServiceLocator.fonts_service.get(c_text.font_path, c_text.size)
            c_text.surface = font.render(c_text.text, True, c_text.color)
        screen.blit(c_text.surface, c_transform.position)
