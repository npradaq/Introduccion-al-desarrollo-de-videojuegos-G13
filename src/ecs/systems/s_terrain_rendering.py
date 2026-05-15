import esper
import pygame
from src.ecs.components.c_terrain import CTerrain


def system_terrain_rendering(world, game_surface: pygame.Surface,
                             camera_x: float, world_width: int,) -> None:

    for _, (c_terrain,) in world.get_components(CTerrain):
        offset_x = -(int(camera_x) % world_width)
        game_surface.blit(c_terrain.surface, (offset_x, 0))
        if offset_x + world_width < game_surface.get_width():
            game_surface.blit(c_terrain.surface, (offset_x + world_width, 0))
        break
