import pygame


class CBurner:
    def __init__(self, idle_surface: pygame.Surface, moving_surface: pygame.Surface,
                 idle_anim_cfg: dict, moving_anim_cfg: dict) -> None:
        self.idle_surface = idle_surface
        self.moving_surface = moving_surface
        self.idle_anim_cfg = idle_anim_cfg
        self.moving_anim_cfg = moving_anim_cfg
