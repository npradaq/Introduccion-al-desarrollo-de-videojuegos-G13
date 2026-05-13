import pygame


class CSteer:
    def __init__(self, target_position: pygame.Vector2 | None) -> None:
        self.target_position = target_position