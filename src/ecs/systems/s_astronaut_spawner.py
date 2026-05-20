import random

import esper
import pygame

from src.ecs.components.c_astronaut_spawner import CAstronautSpawner
from src.create.prefab_creator import create_astronaut


def system_astronaut_spawner(world: esper.World, dt: float) -> None:
    for _, (spawner,) in world.get_components(CAstronautSpawner):
        spawner.elapsed += dt
        while spawner.spawn_times and spawner.elapsed >= spawner.spawn_times[0]:
            x = random.uniform(0, spawner.world_width)
            xi = int(x) % spawner.world_width
            if spawner.terrain_heights:
                y = spawner.terrain_heights[xi] - spawner.astro_sprite_h
            else:
                levels = spawner.astro_cfg.get("levels", [0.70, 0.80, 0.90])
                y = spawner.screen_h * random.choice(levels)
            create_astronaut(world, spawner.astro_cfg, pygame.Vector2(x, y))
            spawner.spawn_times.pop(0)
