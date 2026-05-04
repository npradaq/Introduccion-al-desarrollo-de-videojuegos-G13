import random

import esper
import pygame

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_attach_to import CAttachTo
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_lifetime import CLifetime
from src.ecs.components.c_parallax import CParallax
from src.ecs.components.c_player_state import CPlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_burner import CTagBurner
from src.ecs.components.tags.c_tag_bullet_player import CTagBulletPlayer
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_star import CTagStar
from src.engine.service_locator import ServiceLocator


def create_player(world: esper.World, player_cfg: dict, spawn_cfg: dict) -> int:
    surface = ServiceLocator.images_service.get(player_cfg["image"])
    pos = spawn_cfg["position"]
    position = pygame.Vector2(pos["x"], pos["y"])

    entity = world.create_entity()
    world.add_component(entity, CTransform(position))
    world.add_component(entity, CVelocity(pygame.Vector2(0, 0)))
    world.add_component(entity, CSurface.from_surface(surface))
    world.add_component(entity, CTagPlayer())
    world.add_component(entity, CPlayerState())

    burner_path = player_cfg.get("burner_idle_image")
    if burner_path:
        burner_surface = ServiceLocator.images_service.get(burner_path)
        burner_offset_cfg = player_cfg.get("burner_offset", {"x": 0, "y": 0})
        burner_offset = pygame.Vector2(
            burner_offset_cfg["x"], burner_offset_cfg["y"]
        )

        burner_entity = world.create_entity()
        world.add_component(
            burner_entity, CTransform(position + burner_offset)
        )
        world.add_component(
            burner_entity, CSurface.from_surface(burner_surface)
        )
        burner_anim_info = player_cfg.get("burner_animations")
        if burner_anim_info:
            world.add_component(burner_entity, CAnimation(burner_anim_info))
        world.add_component(burner_entity, CAttachTo(entity, burner_offset))
        world.add_component(burner_entity, CTagBurner())

    return entity


def create_input_player(world: esper.World) -> None:
    mappings = [
        ("PLAYER_LEFT", pygame.K_LEFT),
        ("PLAYER_RIGHT", pygame.K_RIGHT),
        ("PLAYER_UP", pygame.K_UP),
        ("PLAYER_DOWN", pygame.K_DOWN),
        ("PLAYER_FIRE", pygame.K_SPACE),
    ]
    for name, key in mappings:
        entity = world.create_entity()
        world.add_component(entity, CInputCommand(name, key))


def create_bullet_player(world: esper.World, bullet_cfg: dict,
                         player_pos: pygame.Vector2,
                         player_size: tuple[int, int]) -> int:
    color_cfg = bullet_cfg.get("color", {"r": 255, "g": 255, "b": 255})
    color = pygame.Color(color_cfg["r"], color_cfg["g"], color_cfg["b"])
    size_cfg = bullet_cfg.get("size", {"w": 12, "h": 2})
    size = pygame.Vector2(size_cfg["w"], size_cfg["h"])

    velocity_x = bullet_cfg.get("velocity", 400)
    pos = pygame.Vector2(
        player_pos.x + player_size[0],
        player_pos.y + player_size[1] / 2 - size.y / 2
    )

    entity = world.create_entity()
    world.add_component(entity, CTransform(pos))
    world.add_component(entity, CVelocity(pygame.Vector2(velocity_x, 0)))
    world.add_component(entity, CSurface(size, color))
    world.add_component(entity, CTagBulletPlayer())
    world.add_component(entity, CLifetime(bullet_cfg.get("lifetime", 1.5)))

    sound = bullet_cfg.get("sound")
    if sound:
        ServiceLocator.sounds_service.play(sound)
    return entity


def create_starfield(world: esper.World, world_cfg: dict,
                     screen_w: int, screen_h: int) -> None:
    colors = world_cfg.get("star_colors", [{"r": 255, "g": 255, "b": 255}])
    count = world_cfg.get("stars_number", 50)
    parallax = world_cfg.get("stars_parallax_factor", 1.0)
    for _ in range(count):
        x = random.randint(0, screen_w - 1)
        y = random.randint(0, screen_h - 1)
        color_cfg = random.choice(colors)
        color = pygame.Color(color_cfg["r"], color_cfg["g"], color_cfg["b"])
        size = pygame.Vector2(1, 1)

        entity = world.create_entity()
        world.add_component(entity, CTransform(pygame.Vector2(x, y)))
        world.add_component(entity, CVelocity(pygame.Vector2(0, 0)))
        world.add_component(entity, CSurface(size, color))
        world.add_component(entity, CParallax(parallax))
        world.add_component(entity, CTagStar())
