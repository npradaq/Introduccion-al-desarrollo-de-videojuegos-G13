from dataclasses import dataclass
import pygame

@dataclass
class CTerrain:
    surface: pygame.Surface
    heights: list[float]
    world_width: int
