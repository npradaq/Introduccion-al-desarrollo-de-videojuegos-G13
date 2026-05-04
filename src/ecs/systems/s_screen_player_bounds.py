import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_player import CTagPlayer


def system_screen_player_bounds(world: esper.World,
                                 screen_w: int, screen_h: int) -> None:
    components = world.get_components(CTransform, CSurface, CTagPlayer)
    for _, (c_transform, c_surface, _) in components:
        if c_transform.position.x < 0:
            c_transform.position.x = 0
        if c_transform.position.x + c_surface.area.w > screen_w:
            c_transform.position.x = screen_w - c_surface.area.w
        if c_transform.position.y < 0:
            c_transform.position.y = 0
        if c_transform.position.y + c_surface.area.h > screen_h:
            c_transform.position.y = screen_h - c_surface.area.h
