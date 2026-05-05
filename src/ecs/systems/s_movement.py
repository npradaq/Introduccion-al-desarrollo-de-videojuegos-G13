import esper

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity


def system_movement(world: esper.World, dt: float) -> None:
    components = world.get_components(CTransform, CVelocity)
    for _, (c_transform, c_velocity) in components:
        c_transform.position.x += c_velocity.velocity.x * dt
        c_transform.position.y += c_velocity.velocity.y * dt
