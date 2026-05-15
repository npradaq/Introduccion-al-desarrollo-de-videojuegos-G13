import pygame
import esper

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_terrain import CTerrain
from src.ecs.components.tags.c_tag_lander_enemy import CTagLanderEnemy
from src.ecs.components.tags.c_tag_mutant_enemy import CTagMutantEnemy
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut


def system_minimap(world, screen: pygame.Surface, camera_x: float, world_width: int,
                   screen_w: int, screen_h: int, interface_cfg: dict) -> None:
    """
    Render a minimap showing terrain, enemies, and astronauts.

    The minimap displays 3 screens of content: one behind + current + one ahead.
    """
    mm = interface_cfg.get("hud", {}).get("minimap", {})
    if not mm:
        return

    mm_x = mm.get("x", 80)
    mm_y = mm.get("y", 3)
    mm_w = mm.get("width", 160)
    mm_h = mm.get("height", 26)

    border_cfg = mm.get("border_color", {"r": 0, "g": 0, "b": 255})
    border_color = pygame.Color(border_cfg["r"], border_cfg["g"], border_cfg["b"])

    terrain_cfg = mm.get("terrain_color", {"r": 255, "g": 165, "b": 0})
    terrain_color = pygame.Color(terrain_cfg["r"], terrain_cfg["g"], terrain_cfg["b"])

    enemy_cfg = mm.get("enemy_color", {"r": 255, "g": 50, "b": 50})
    enemy_color = pygame.Color(enemy_cfg["r"], enemy_cfg["g"], enemy_cfg["b"])

    astro_cfg = mm.get("astronaut_color", {"r": 50, "g": 255, "b": 50})
    astro_color = pygame.Color(astro_cfg["r"], astro_cfg["g"], astro_cfg["b"])

    viewport_cfg = mm.get("viewport_color", {"r": 255, "g": 255, "b": 255})
    viewport_color = pygame.Color(viewport_cfg["r"], viewport_cfg["g"], viewport_cfg["b"])

    minimap_rect = pygame.Rect(mm_x, mm_y, mm_w, mm_h)

    # Draw background
    pygame.draw.rect(screen, pygame.Color(0, 0, 0), minimap_rect)
    pygame.draw.rect(screen, border_color, minimap_rect, 1)

    # Get terrain heights
    terrain_heights = []
    for _, (c_terrain,) in world.get_components(CTerrain):
        terrain_heights = c_terrain.heights
        break

    if not terrain_heights:
        return

    # Draw terrain
    minimap_start = camera_x - screen_w
    minimap_range = 3 * screen_w

    for mx in range(mm_w):
        world_x = minimap_start + mx * minimap_range / mm_w
        world_x_idx = int(world_x) % world_width
        terrain_y = terrain_heights[world_x_idx]

        # Scale terrain y to minimap height (0 to mm_h)
        my = int((terrain_y / screen_h) * mm_h)

        # Clamp to minimap bounds
        if 0 <= my < mm_h:
            screen.set_at((mm_x + mx, mm_y + my), terrain_color)

    # Draw enemies (Lander + Mutant)
    for _, (c_transform, _) in world.get_components(CTransform, CTagLanderEnemy):
        _draw_minimap_entity(screen, c_transform, minimap_start, minimap_range,
                            mm_x, mm_y, mm_w, mm_h, screen_h, enemy_color)

    for _, (c_transform, _) in world.get_components(CTransform, CTagMutantEnemy):
        _draw_minimap_entity(screen, c_transform, minimap_start, minimap_range,
                            mm_x, mm_y, mm_w, mm_h, screen_h, enemy_color)

    # Draw astronauts
    for _, (c_transform, _) in world.get_components(CTransform, CTagAstronaut):
        _draw_minimap_entity(screen, c_transform, minimap_start, minimap_range,
                            mm_x, mm_y, mm_w, mm_h, screen_h, astro_color)

    # Draw viewport indicator (where the camera is looking)
    viewport_start_rel = camera_x - minimap_start
    viewport_pixel = int((viewport_start_rel / minimap_range) * mm_w)
    viewport_width = int((screen_w / minimap_range) * mm_w)
    viewport_width = max(1, viewport_width)

    if 0 <= viewport_pixel < mm_w:
        pygame.draw.rect(screen, viewport_color,
                        (mm_x + viewport_pixel, mm_y + 1, viewport_width, mm_h - 2), 1)


def _draw_minimap_entity(screen: pygame.Surface, c_transform: CTransform,
                         minimap_start: float, minimap_range: float,
                         mm_x: int, mm_y: int, mm_w: int, mm_h: int,
                         screen_h: int, color: pygame.Color) -> None:
    """Helper to draw an entity on the minimap."""
    pos = c_transform.position

    # Calculate relative position within minimap range
    rel_x = pos.x - minimap_start
    mx = int((rel_x / minimap_range) * mm_w)
    my = int((pos.y / screen_h) * mm_h)

    # Draw if within minimap bounds
    if 0 <= mx < mm_w and 0 <= my < mm_h:
        pygame.draw.rect(screen, color, (mm_x + mx, mm_y + my, 2, 2))
