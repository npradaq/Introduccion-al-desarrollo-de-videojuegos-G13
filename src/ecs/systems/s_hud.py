import esper
import pygame

from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.engine.service_locator import ServiceLocator


def system_hud(world: esper.World, screen: pygame.Surface,
               interface_cfg: dict, lives: int) -> None:
    hud_cfg = interface_cfg.get("hud", {})
    font_path = interface_cfg.get("font", "")
    header_h = hud_cfg.get("header_height", 32)
    screen_w = screen.get_width()

    pygame.draw.rect(screen, (0, 0, 0), (0, 0, screen_w, header_h))

    lc = hud_cfg.get("header_line_color", {"r": 0, "g": 0, "b": 255})
    pygame.draw.line(screen, (lc["r"], lc["g"], lc["b"]),
                     (0, header_h - 1), (screen_w, header_h - 1))

    text_components = world.get_components(CTransform, CText)
    for _, (c_transform, c_text) in text_components:
        if not c_text.visible:
            continue
        if c_text.surface is None:
            font = ServiceLocator.fonts_service.get(c_text.font_path, c_text.size)
            c_text.surface = font.render(c_text.text, True, c_text.color)
        screen.blit(c_text.surface, c_transform.position)

    lives_cfg = hud_cfg.get("lives", {})
    lives_img = ServiceLocator.images_service.get(
        lives_cfg.get("image", "assets/img/interface_lives.png")
    )
    lx = lives_cfg.get("x", 88)
    ly = lives_cfg.get("y", 21)
    spacing = lives_cfg.get("spacing", 16)
    for i in range(lives):
        screen.blit(lives_img, (lx + i * spacing, ly))

    enemy_count = (len(list(world.get_component(CTagEnemy))))
    astro_count = len(list(world.get_component(CTagAstronaut)))

    _draw_counter(screen, font_path, hud_cfg.get("enemies_count", {}), enemy_count)
    _draw_counter(screen, font_path, hud_cfg.get("astronauts_count", {}), astro_count)


def _draw_counter(screen: pygame.Surface, font_path: str,
                  cfg: dict, value: int) -> None:
    if not cfg:
        return
    size = cfg.get("size", 6)
    x = cfg.get("x", 0)
    y = cfg.get("y", 0)
    c = cfg.get("color", {"r": 255, "g": 255, "b": 255})
    color = (c["r"], c["g"], c["b"])
    font = ServiceLocator.fonts_service.get(font_path, size)
    label_surf = font.render(cfg.get("label", ""), True, color)
    screen.blit(label_surf, (x, y))
    value_surf = font.render(str(value), True, (255, 255, 255))
    screen.blit(value_surf, (x, y + label_surf.get_height() + 2))
