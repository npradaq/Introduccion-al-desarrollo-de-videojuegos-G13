import esper

from src.ecs.components.c_lifetime import CLifetime
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_bullet_player import CTagBulletPlayer


def system_screen_bullet(world: esper.World, dt: float,
                         camera_x: float, screen_w: int) -> None:
    for entity, c_lifetime in world.get_component(CLifetime):
        c_lifetime.time_left -= dt
        if c_lifetime.time_left <= 0:
            world.delete_entity(entity)
            continue

        if not world.has_component(entity, CTagBulletPlayer):
            continue
        try:
            pos_x = world.component_for_entity(entity, CTransform).position.x
        except Exception:
            continue
        screen_x = (pos_x - camera_x) % screen_w if screen_w > 0 else pos_x
        if screen_x > screen_w:
            world.delete_entity(entity)
