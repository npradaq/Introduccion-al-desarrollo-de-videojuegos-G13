import random

import esper
import pygame

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_attach_to import CAttachTo
from src.ecs.components.c_burner import CBurner
from src.ecs.components.c_can_blink import CCanBlink
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_lifetime import CLifetime
from src.ecs.components.c_parallax import CParallax
from src.ecs.components.c_player_state import CPlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_terrain import CTerrain
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_astronaut_state import AstronautPhase, CAstronautState
from src.ecs.components.c_lander_state import CLanderState
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut
from src.ecs.components.tags.c_tag_burner import CTagBurner
from src.ecs.components.tags.c_tag_lander_enemy import CTagLanderEnemy
from src.ecs.components.tags.c_tag_mutant_enemy import CTagMutantEnemy
from src.ecs.components.tags.c_tag_bullet_player import CTagBulletPlayer
from src.ecs.components.tags.c_tag_hud import CTagHUD
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_star import CTagStar
from src.ecs.components.tags.c_tag_terrain import CTagTerrain
from src.engine.perlin import octave_noise1d, seed
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
        idle_surface = ServiceLocator.images_service.get(burner_path)
        moving_surface = ServiceLocator.images_service.get(
            player_cfg.get("burner_moving_image", burner_path)
        )
        burner_offset_cfg = player_cfg.get("burner_offset", {"x": 0, "y": 0})
        burner_offset = pygame.Vector2(
            burner_offset_cfg["x"], burner_offset_cfg["y"]
        )
        idle_anim_cfg = player_cfg.get("burner_animations")
        moving_anim_cfg = player_cfg.get("burner_moving_animations", idle_anim_cfg)

        burner_entity = world.create_entity()
        world.add_component(burner_entity, CTransform(position + burner_offset))
        world.add_component(burner_entity, CSurface.from_surface(idle_surface))
        if idle_anim_cfg:
            world.add_component(burner_entity, CAnimation(idle_anim_cfg))
        world.add_component(burner_entity, CBurner(
            idle_surface, moving_surface, idle_anim_cfg, moving_anim_cfg
        ))
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


def create_input_scene(world: esper.World) -> None:
    mappings = [
        ("PAUSE", pygame.K_p),
        ("BACK_TO_MENU", pygame.K_BACKSPACE),
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


def create_text(world: esper.World, text: str, font_path: str, size: int,
                color: dict, position: dict) -> int:
    pos = pygame.Vector2(position.get("x", 0), position.get("y", 0))
    rgb = (color.get("r", 255), color.get("g", 255), color.get("b", 255))

    entity = world.create_entity()
    world.add_component(entity, CTransform(pos))
    world.add_component(entity, CText(text, font_path, size, rgb))
    return entity


def create_image(world: esper.World, image_path: str,
                 position: dict) -> int:
    surface = ServiceLocator.images_service.get(image_path)
    pos = pygame.Vector2(position.get("x", 0), position.get("y", 0))

    entity = world.create_entity()
    world.add_component(entity, CTransform(pos))
    world.add_component(entity, CSurface.from_surface(surface))
    return entity


def create_hud(world: esper.World, interface_cfg: dict) -> int | None:
    """Returns the score_value entity ID for live updates."""
    hud_cfg = interface_cfg.get("hud", {})
    font_path = interface_cfg.get("font", "")
    score_entity: int | None = None

    for key in ("score_label", "score_value"):
        cfg = hud_cfg.get(key)
        if cfg is None:
            continue
        pos = pygame.Vector2(cfg["position"]["x"], cfg["position"]["y"])
        c = cfg["color"]
        rgb = (c["r"], c["g"], c["b"])
        entity = world.create_entity()
        world.add_component(entity, CTransform(pos))
        world.add_component(entity, CText(cfg.get("text", ""), font_path, cfg["size"], rgb))
        world.add_component(entity, CTagHUD())
        if key == "score_value":
            score_entity = entity

    return score_entity


def create_pause_text(world: esper.World, interface_cfg: dict,
                      screen_w: int, screen_h: int) -> int:
    pause_cfg = interface_cfg.get("pause", {})
    font_path = interface_cfg.get("font", "")

    text = pause_cfg.get("text", "PAUSED")
    size = pause_cfg.get("size", 16)
    color = pause_cfg.get("color", {"r": 255, "g": 255, "b": 255})
    blink_rate = pause_cfg.get("blink_rate", 2.0)

    rgb = (color.get("r", 255), color.get("g", 255), color.get("b", 255))

    entity = world.create_entity()
    font = ServiceLocator.fonts_service.get(font_path, size)
    text_surface = font.render(text, True, rgb)
    text_w = text_surface.get_width()
    text_h = text_surface.get_height()
    center_x = (screen_w - text_w) // 2
    center_y = (screen_h - text_h) // 2

    world.add_component(entity, CTransform(pygame.Vector2(center_x, center_y)))
    world.add_component(entity, CText(text, font_path, size, rgb))
    world.add_component(entity, CCanBlink(blink_rate))
    world.add_component(entity, CTagHUD())

    c_text = world.component_for_entity(entity, CText)
    c_text.surface = text_surface
    c_text.visible = False

    return entity


def create_astronaut(world: esper.World, astronaut_cfg: dict,
                     position: pygame.Vector2) -> int:
    surface = ServiceLocator.images_service.get(astronaut_cfg["image"])

    entity = world.create_entity()
    world.add_component(entity, CTransform(position))
    world.add_component(entity, CVelocity(pygame.Vector2(0, 0)))
    world.add_component(entity, CSurface.from_surface(surface))
    world.add_component(entity, CAnimation(astronaut_cfg["animations"]))
    state = CAstronautState(position.y)
    state.phase = AstronautPhase.LANDED
    world.add_component(entity, state)
    world.add_component(entity, CTagAstronaut())

    return entity


def create_astronauts(world: esper.World, astronaut_cfg: dict, count: int,
                      screen_h: int, screen_w: int) -> None:
    levels = astronaut_cfg.get("levels", [0.70, 0.80, 0.90])
    spacing = screen_w // (count + 1)

    for i in range(count):
        x = spacing * (i + 1)
        level_ratio = levels[i % len(levels)]
        pos = pygame.Vector2(x, screen_h * level_ratio)
        create_astronaut(world, astronaut_cfg, pos)


def create_lander_enemy(world: esper.World, lander_enemy_cfg: dict,
                        position: pygame.Vector2) -> int:
    surface = ServiceLocator.images_service.get(lander_enemy_cfg["image"])

    patrol_min = lander_enemy_cfg.get("initial_patrol_min", 2.0)
    patrol_max = lander_enemy_cfg.get("initial_patrol_max", 10.0)
    initial_patrol = random.uniform(patrol_min, patrol_max)

    entity = world.create_entity()
    world.add_component(entity, CTransform(position))
    world.add_component(entity, CVelocity(pygame.Vector2(0, 0)))
    world.add_component(entity, CSurface.from_surface(surface))
    world.add_component(entity, CAnimation(lander_enemy_cfg["animations"]))
    world.add_component(entity, CLanderState(initial_patrol_duration=initial_patrol))
    world.add_component(entity, CTagLanderEnemy())

    return entity


def create_terrain(world: esper.World, world_cfg: dict,
                   world_width: int, screen_h: int,) -> tuple[int, list[float]]:

    amplitude = world_cfg.get("planet_terrain_amplitude", 22)
    base_ratio = world_cfg.get("planet_terrain_base_ratio", 0.78)
    waves = world_cfg.get("planet_terrain_waves", 5)
    octaves = world_cfg.get("planet_terrain_octaves", 2)
    min_ratio = world_cfg.get("planet_terrain_min_ratio", 0.52)
    colors = world_cfg.get("planet_terrain_colors", [{"r": 255, "g": 90, "b": 90}])

    seed(random.randint(0, 2**31 - 1))
    base_y = screen_h * base_ratio
    frequency = waves / world_width
    min_y = screen_h * min_ratio

    heights = []
    for x in range(world_width):
        n = octave_noise1d(
            x * frequency,
            octaves=octaves,
            frequency=1.0,
            amplitude=float(amplitude),
            persistence=0.5,
            lacunarity=2.0,
        )
        h = base_y + n
        heights.append(max(h, min_y))

    color_cfg = random.choice(colors)
    fill_color = pygame.Color(color_cfg["r"], color_cfg["g"], color_cfg["b"])
    outline_color = pygame.Color(
        min(color_cfg["r"] + 80, 255),
        min(color_cfg["g"] + 80, 255),
        min(color_cfg["b"] + 80, 255),
    )

    surf = pygame.Surface((world_width, screen_h))
    poly_pts = [(x, int(heights[x])) for x in range(world_width)]
    poly_pts += [(world_width - 1, screen_h), (0, screen_h)]
    pygame.draw.polygon(surf, fill_color, poly_pts)
    pygame.draw.lines(
        surf,
        outline_color,
        False,
        [(x, int(heights[x])) for x in range(world_width)],
        1,
    )

    entity = world.create_entity()
    world.add_component(
        entity,
        CTerrain(surface=surf, heights=heights, world_width=world_width),
    )
    world.add_component(entity, CTagTerrain())
    return entity, heights


def create_mutant_enemy(world: esper.World, mutant_enemy_cfg: dict,
                        position: pygame.Vector2) -> int:
    surface = ServiceLocator.images_service.get(mutant_enemy_cfg["image"])

    entity = world.create_entity()
    world.add_component(entity, CTransform(position))
    world.add_component(entity, CVelocity(pygame.Vector2(0, 0)))
    world.add_component(entity, CSurface.from_surface(surface))
    world.add_component(entity, CAnimation(mutant_enemy_cfg["animations"]))
    world.add_component(entity, CTagMutantEnemy())

    return entity
