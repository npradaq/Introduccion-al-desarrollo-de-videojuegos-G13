import esper
import pygame

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_burner import CTagBurner
from src.ecs.components.tags.c_tag_bullet_player import CTagBulletPlayer
from src.ecs.components.tags.c_tag_player import CTagPlayer


def system_rendering(world: esper.World, screen: pygame.Surface,
                     hide_player: bool = False) -> None:
    components = world.get_components(CTransform, CSurface)
    for entity, (c_transform, c_surface) in components:
        if hide_player and (
            world.has_component(entity, CTagPlayer)
            or world.has_component(entity, CTagBulletPlayer)
            or world.has_component(entity, CTagBurner)
        ):
            continue
        screen.blit(c_surface.surface, c_transform.position, c_surface.area)
