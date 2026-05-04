import pygame


class FontsService:
    def __init__(self) -> None:
        self._fonts: dict[tuple, pygame.font.Font] = {}

    def get(self, path: str, size: int) -> pygame.font.Font:
        key = (path, size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.Font(path, size)
        return self._fonts[key]
