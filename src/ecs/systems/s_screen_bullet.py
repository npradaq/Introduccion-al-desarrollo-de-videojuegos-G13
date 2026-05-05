import esper

from src.ecs.components.c_lifetime import CLifetime


def system_screen_bullet(world: esper.World, dt: float) -> None:
    components = world.get_component(CLifetime)
    for entity, c_lifetime in components:
        c_lifetime.time_left -= dt
        if c_lifetime.time_left <= 0:
            world.delete_entity(entity)
