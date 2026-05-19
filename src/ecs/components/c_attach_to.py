import pygame


class CAttachTo:
    def __init__(self, parent_id: int, offset: pygame.Vector2) -> None:
        self.parent_id = parent_id
        self.offset = pygame.Vector2(offset.x, offset.y)
        self.initial_offset = pygame.Vector2(offset.x, offset.y)
