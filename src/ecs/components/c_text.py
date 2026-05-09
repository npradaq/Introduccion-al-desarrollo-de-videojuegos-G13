import pygame


class CText:
    def __init__(self, text: str, font_path: str, size: int,
                 color: tuple[int, int, int]) -> None:
        self.text = text
        self.font_path = font_path
        self.size = size
        self.color = color
        self.surface: pygame.Surface | None = None
        self.visible = True
