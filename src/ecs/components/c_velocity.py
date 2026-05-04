import pygame


class CVelocity:
    def __init__(self, velocity: pygame.Vector2) -> None:
        self.velocity = pygame.Vector2(velocity.x, velocity.y)
