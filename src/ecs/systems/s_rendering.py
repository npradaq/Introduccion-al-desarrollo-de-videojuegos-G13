import esper
import pygame

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.engine.service_locator import ServiceLocator


def system_rendering(world: esper.World, screen: pygame.Surface) -> None:
    components = world.get_components(CTransform, CSurface)
    for entity, (c_transform, c_surface) in components:
        if not c_surface.visible:
            continue
        screen.blit(c_surface.surface, c_transform.position, c_surface.area)

    text_components = world.get_components(CTransform, CText)
    for entity, (c_transform, c_text) in text_components:
        if not c_text.visible:
            continue
        if c_text.surface is None:
            font = ServiceLocator.fonts_service.get(c_text.font_path, c_text.size)
            c_text.surface = font.render(c_text.text, True, c_text.color)
        screen.blit(c_text.surface, c_transform.position)
