import pygame


class SoundsService:
    def __init__(self) -> None:
        self._sounds: dict[str, pygame.mixer.Sound] = {}

    def play(self, path: str) -> None:
        if not path:
            return
        try:
            if path not in self._sounds:
                self._sounds[path] = pygame.mixer.Sound(path)
            self._sounds[path].play()
        except Exception:
            pass
