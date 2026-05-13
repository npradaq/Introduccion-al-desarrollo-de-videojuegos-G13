import esper

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut


def system_astronaut(world: esper.World, screen_h: int) -> None:
    landing_y = int(screen_h * 0.85)
    components = world.get_components(CTransform, CVelocity, CTagAstronaut)
    for ent, (c_transform, c_velocity, _) in components:
        if c_transform.position.y >= landing_y:
            c_transform.position.y = landing_y
            c_velocity.velocity.y = 0
