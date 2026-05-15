import pygame
import esper

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_terrain import CTerrain
from src.ecs.components.tags.c_tag_lander_enemy import CTagLanderEnemy
from src.ecs.components.tags.c_tag_mutant_enemy import CTagMutantEnemy
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut


def system_minimap(world, screen: pygame.Surface, camera_x: float, world_width: int,
                   screen_w: int, screen_h: int, interface_cfg: dict, player_entity: int | None = None) -> None:
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

    # Draw terrain as smooth filled silhouette with interpolation
    minimap_start = camera_x - screen_w
    minimap_range = 3 * screen_w

    # Interpolate terrain: 2 samples per minimap pixel for smoothness
    samples_per_pixel = 2
    total_samples = mm_w * samples_per_pixel

    for i in range(total_samples):
        # Calculate world x with interpolation
        t = i / total_samples
        world_x = minimap_start + t * minimap_range

        # Linear interpolation between adjacent terrain points
        x_int = int(world_x)
        x_frac = world_x - x_int

        idx1 = x_int % world_width
        idx2 = (x_int + 1) % world_width

        h1 = terrain_heights[idx1]
        h2 = terrain_heights[idx2]

        # Interpolated height
        terrain_y = h1 + (h2 - h1) * x_frac

        # Scale to minimap height
        my = int((terrain_y / screen_h) * mm_h)
        my = max(0, min(my, mm_h - 1))

        # Map sample index to minimap pixel column
        mm_x_pixel = int((i / total_samples) * mm_w)
        if mm_x_pixel >= mm_w:
            mm_x_pixel = mm_w - 1

        # Draw filled column from terrain to bottom
        pygame.draw.line(screen, terrain_color,
                        (mm_x + mm_x_pixel, mm_y + my),
                        (mm_x + mm_x_pixel, mm_y + mm_h - 1))

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

    # Draw player indicator (yellow/gold)
    if player_entity is not None:
        try:
            c_transform = world.component_for_entity(player_entity, CTransform)
            _draw_minimap_entity(screen, c_transform, minimap_start, minimap_range,
                                mm_x, mm_y, mm_w, mm_h, screen_h,
                                pygame.Color(255, 255, 0))
        except (KeyError, IndexError):
            pass

    # Draw viewport indicator bracket - always centered (ship is always at mm_w//2)
    indicator_w = mm_w // 5
    half_w = indicator_w // 2
    center = mm_w // 2
    cap_h = 3

    vx0 = mm_x + center - half_w
    vx1 = mm_x + center + half_w

    # Top horizontal line + vertical caps
    pygame.draw.line(screen, viewport_color, (vx0, mm_y), (vx1, mm_y), 1)
    pygame.draw.line(screen, viewport_color, (vx0, mm_y), (vx0, mm_y + cap_h), 1)
    pygame.draw.line(screen, viewport_color, (vx1, mm_y), (vx1, mm_y + cap_h), 1)

    # Bottom horizontal line + vertical caps
    pygame.draw.line(screen, viewport_color, (vx0, mm_y + mm_h - 1), (vx1, mm_y + mm_h - 1), 1)
    pygame.draw.line(screen, viewport_color, (vx0, mm_y + mm_h - 1 - cap_h), (vx0, mm_y + mm_h - 1), 1)
    pygame.draw.line(screen, viewport_color, (vx1, mm_y + mm_h - 1 - cap_h), (vx1, mm_y + mm_h - 1), 1)


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
