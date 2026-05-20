import random

import esper
import pygame

from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.tags.c_tag_lander_enemy import CTagLanderEnemy
from src.create.prefab_creator import create_lander_enemy


def system_enemy_spawner(world: esper.World, dt: float) -> None:
    for _, (spawner,) in world.get_components(CEnemySpawner):
        spawner.elapsed += dt
        if spawner.elapsed < spawner.enemy_start_delay:
            continue

        lander_cfg = spawner.lander_cfg
        max_concurrent = lander_cfg.get("max_concurrent", 5)
        max_total = lander_cfg.get("max_total", 20)
        spawn_interval = lander_cfg.get("spawn_interval", 3.0)

        if spawner.total_spawned >= max_total:
            continue

        alive = len(list(world.get_component(CTagLanderEnemy)))
        if alive >= max_concurrent:
            continue

        spawner.spawn_timer += dt
        if spawner.spawn_timer < spawn_interval:
            continue
        spawner.spawn_timer = 0.0

        x = random.uniform(0, spawner.world_width)
        y = random.uniform(spawner.screen_h * 0.05, spawner.screen_h * 0.5)
        create_lander_enemy(world, lander_cfg, pygame.Vector2(x, y))
        spawner.total_spawned += 1
