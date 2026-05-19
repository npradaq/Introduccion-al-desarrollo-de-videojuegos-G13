import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy_bullet import CTagEnemyBullet
from src.ecs.components.tags.c_tag_player import CTagPlayer


def system_enemy_bullet_player_collision(world: esper.World, explosion_cfg: dict) -> None:
    b_components = world.get_components(CTransform, CSurface, CTagEnemyBullet)
    player_components = world.get_components(CTransform, CSurface, CTagPlayer)
    