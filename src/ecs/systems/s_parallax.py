import esper

from src.ecs.components.c_parallax import CParallax
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity


def system_parallax(world: esper.World, player_velocity: CVelocity,
                    screen_w: int, dt: float) -> None:
    components = world.get_components(CTransform, CParallax)
    for _, (c_transform, c_parallax) in components:
        c_transform.position.x -= player_velocity.velocity.x * c_parallax.factor * dt
        if c_transform.position.x < 0:
            c_transform.position.x += screen_w
        elif c_transform.position.x >= screen_w:
            c_transform.position.x -= screen_w
