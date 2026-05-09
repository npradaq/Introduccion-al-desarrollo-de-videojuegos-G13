import pygame


class CSurface:
    def __init__(self, size: pygame.Vector2, color: pygame.Color) -> None:
        self.surface = pygame.Surface((size.x, size.y))
        self.surface.fill(color)
        self.area = self.surface.get_rect()
        self.color = color
        self.visible = True

    @classmethod
    def from_surface(cls, surface: pygame.Surface) -> "CSurface":
        instance = cls.__new__(cls)
        instance.surface = surface
        instance.area = surface.get_rect()
        instance.color = pygame.Color(255, 255, 255)
        instance.visible = True
        return instance
