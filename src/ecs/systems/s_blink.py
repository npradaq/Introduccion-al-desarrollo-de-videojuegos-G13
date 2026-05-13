import esper

from src.ecs.components.c_can_blink import CCanBlink
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_text import CText


def system_blink(world: esper.World, dt: float) -> None:
    blink_components = world.get_components(CCanBlink, CSurface)
    for entity, (c_blink, c_surface) in blink_components:
        c_blink._blink_time += dt
        c_surface.visible = (c_blink._blink_time * c_blink.blink_rate) % 2 < 1

    blink_text_components = world.get_components(CCanBlink, CText)
    for entity, (c_blink, c_text) in blink_text_components:
        c_blink._blink_time += dt
        c_text.visible = (c_blink._blink_time * c_blink.blink_rate) % 2 < 1
