import pygame


class CSurface:
    def __init__(self, size: pygame.Vector2, color: pygame.Color) -> None:
        self.surface = pygame.Surface((size.x, size.y))
        self.surface.fill(color)
        self.area = self.surface.get_rect()
        self.color = color
        self.visible = True
        self.flip_x = False

    @classmethod
    def from_surface(cls, surface: pygame.Surface) -> "CSurface":
        """instance = cls.__new__(cls)
        instance.surface = surface
        instance.area = surface.get_rect()
        instance.color = pygame.Color(255, 255, 255)"""
        c_surf = cls(pygame.Vector2(0,0), pygame.Color(0,0,0))
        c_surf.surface = surface
        c_surf.area = surface.get_rect()
        c_surf.visible = True
        c_surf.flip_x = False
        return c_surf

    def get_area_relative (area: pygame.Rect, pos_topleft: pygame.Vector2): # type: ignore
        new_rect = area.copy()
        new_rect.topleft = pos_topleft.copy()
        return new_rect