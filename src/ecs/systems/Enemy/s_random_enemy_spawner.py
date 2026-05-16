import esper
import pygame
import random
import math

from src.create.prefab_creator_enemy import create_enemy

from src.ecs.components.Enemy.c_random_enemy_spawner import CRandomEnemySpawner
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy



def system_random_enemy_spawner(
        world: esper.World,
        delta_time: float,
        elapsed_time: float,
        player_entity: int,
        enemies_info: dict,
        world_width: int,
        world_height: int
        ) -> None:

    # ==========================================
    # obtener jugador
    # ==========================================

    player_transform = world.component_for_entity(player_entity, CTransform)

    player_pos = player_transform.position

    # ==========================================
    # contar enemigos actuales
    # ==========================================

    current_enemy_count = len(
        world.get_component(CTagEnemy)
    )

    # ==========================================
    # procesar spawners
    # ==========================================

    for ent, (c_spawner) in world.get_component(
        CRandomEnemySpawner
    ):

        spawner_info = c_spawner.spawner_info

        # ==========================
        # actualizar timer
        # ==========================

        c_spawner.spawn_timer -= delta_time

        if c_spawner.spawn_timer > 0:
            continue

        # reiniciar timer
        c_spawner.spawn_timer = (
            spawner_info["spawn_interval"]
        )

        # ==========================
        # calcular máximo permitido
        # ==========================

        max_enemies = (
            spawner_info["initial_max_enemies"] + int(elapsed_time * spawner_info["max_enemies_growth"])
        )

        # ==========================
        # no hacer spawn si ya llegó
        # al máximo
        # ==========================

        if current_enemy_count >= max_enemies:
            continue

        # ==========================
        # escoger tipo enemigo
        # ==========================

        enemy_type = random.choice(
            spawner_info["enemy_types"]
        )

        enemy_info = (
            enemies_info[enemy_type]
        )

        # ==========================
        # generar posición válida
        # ==========================

        spawn_pos = None

        while spawn_pos is None:

            candidate_pos = pygame.Vector2(
                random.uniform(0, world_width),
                random.uniform(0, world_height)
            )

            distance_to_player = (
                candidate_pos - player_pos
            ).length()

            if distance_to_player >= spawner_info[
                "spawn_radius_from_player"
            ]:
                spawn_pos = candidate_pos

        # ==========================
        # crear enemigo
        # ==========================

        create_enemy(
            world,
            spawn_pos,
            enemy_info,
            enemy_type
        )