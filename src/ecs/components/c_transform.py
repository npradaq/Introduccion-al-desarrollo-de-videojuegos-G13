import pygame


class CTransform:
    def __init__(self, position: pygame.Vector2) -> None:
        self.position = pygame.Vector2(position.x, position.y)
