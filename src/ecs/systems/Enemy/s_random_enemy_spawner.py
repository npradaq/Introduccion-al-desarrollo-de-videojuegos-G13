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
        wave_info = c_spawner.spawner_info["Waves"][c_spawner.current_wave+1]
        
        # ==========================
        # Comprobar condiciones de cambio de oleada
        # ==========================
        if(wave_info["wave_number"] != 5):
            if (
                c_spawner.enemies_death_count >= wave_info["enemies_to_spawn"] or
                c_spawner.elapsed_wave_time >= wave_info["time_completion"]
            ):
                c_spawner.current_wave += 1
                c_spawner.enemies_death_count = 0
                c_spawner.spawned_enemies_count = 0
                c_spawner.spawn_timer = 0.0
                c_spawner.elapsed_wave_time = 0.0
                
                _new_wave(world, wave_info, world_width, world_height, player_pos, enemies_info)
                
                
                continue    

        # ==========================
        # actualizar timer
        # ==========================

        c_spawner.spawn_timer -= delta_time
        c_spawner.elapsed_wave_time += delta_time

        if c_spawner.spawn_timer > 0:
            continue

        # reiniciar timer
        c_spawner.spawn_timer = (
            wave_info["spawn_interval"]
        )

        # ==========================
        # verificar si se puede spawnear más enemigos
        # ==========================

        if c_spawner.spawned_enemies_count >= wave_info["enemies_to_spawn"]:
            continue

        # ==========================
        # escoger tipo enemigo
        # ==========================
        
        enemy_chosen = True
        cicles = 0
        
        enemy_type = ""
        
        while(enemy_chosen):
            if(cicles > 5):
                enemy_type = wave_info["enemy_types"][0]
                break
            choices = wave_info["enemy_types"]
            weights = wave_info["enemy_spawn_chances"]
            
            enemy_type = random.choices(
                choices,
                weights=weights,
                k=1
            )[0]
            
            cicles += 1
            
            
            if wave_info["time_enemy_buffer"][enemy_type] >= elapsed_time:
                enemy_chosen = False
            
            
        
        enemy_info = enemies_info[enemy_type]

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

            if distance_to_player >= wave_info  [
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
        
def _new_wave(world: esper.World, wave_info: dict, world_width: int, world_height: int,
              player_pos: pygame.Vector2, enemy_info: dict):
    
    print(f"New wave: {wave_info['wave_number']}")
    
    components = world.get_components(CTagEnemy, CTransform)
    
    for entity, (c_tag_enemy, c_transform) in components:
        world.delete_entity(entity)
        
    enemies_spawned = 0

    while enemies_spawned < wave_info["initial_enemies_to_spawn"]:
        spawn_pos = None

        while spawn_pos is None:

            candidate_pos = pygame.Vector2(
                random.uniform(0, world_width),
                random.uniform(0, world_height)
            )

            distance_to_player = (
                candidate_pos - player_pos
            ).length()

            if distance_to_player >= wave_info  [
                "spawn_radius_from_player"
            ]:
                spawn_pos = candidate_pos

        create_enemy(
            world,
            spawn_pos,
            enemy_info["Lander"],
            "Lander"
        )
        
        enemies_spawned += 1
        
    
    