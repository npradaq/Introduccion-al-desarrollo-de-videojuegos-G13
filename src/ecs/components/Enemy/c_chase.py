import pygame


class CChase:
    def __init__(self):

        self.direction_timer = 0.0

        self.jerk_direction = pygame.Vector2(0, 0)