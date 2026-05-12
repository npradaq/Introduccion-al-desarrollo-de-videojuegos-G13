import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_lander_enemy import CTagLanderEnemy
from src.ecs.components.tags.c_tag_mutant_enemy import CTagMutantEnemy

def system_enemy_wraparound(world: esper.World, screen_height: int):
    # This system checks if any enemy has moved beyond the bottom of the screen. If so, it wraps the enemy back to the top of the screen.
    enemy_components = world.get_components(CTransform, CSurface)
    for entity, (c_transform, c_surface) in enemy_components:
        if not (
            world.has_component(entity, CTagLanderEnemy)
            or world.has_component(entity, CTagMutantEnemy)
        ):
            continue
        if c_transform.position.y > screen_height:
            c_transform.position.y = -c_surface.area.h
        