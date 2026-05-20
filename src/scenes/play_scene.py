import random

import pygame

from src.create.prefab_creator import (
    create_astronaut_spawner, create_bullet_player, create_hud,
    create_input_player, create_input_scene, create_pause_text,
    create_play_game_state, create_player, create_starfield, create_terrain
)
from src.create.prefab_creator_enemy import create_fixed_enemy_spawner, create_random_enemy_spawner
from src.ecs.components.Enemy.c_fixed_enemy_spawner import CEnemySpawner as CFixedEnemySpawner
from src.ecs.components.Enemy.c_random_enemy_spawner import CRandomEnemySpawner
from src.ecs.components.c_astronaut_spawner import CAstronautSpawner
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_lifetime import CLifetime
from src.ecs.components.c_play_game_state import CPlayGameState
from src.ecs.components.c_player_state import CPlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_terrain import CTerrain
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_attach_to import CAttachTo
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut
from src.ecs.components.tags.c_tag_bullet_player import CTagBulletPlayer
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_hud import CTagHUD
from src.ecs.components.tags.c_tag_particle import CTagParticle
from src.ecs.systems.Enemy.s_baiter_state import system_baiter_state
from src.ecs.systems.Enemy.s_bomber_state import system_bomber_state
from src.ecs.systems.Enemy.s_fixed_enemy_spawner import system_fixed_enemy_spawner
from src.ecs.systems.Enemy.s_lander_state import system_lander_state
from src.ecs.systems.Enemy.s_mutant_state import system_mutant_state
from src.ecs.systems.Enemy.s_pod_state import system_pod_state
from src.ecs.systems.Enemy.s_random_enemy_spawner import system_random_enemy_spawner
from src.ecs.systems.Enemy.s_swarmer_state import system_swarmer_state
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_astronaut import system_astronaut
from src.ecs.systems.s_astronaut_spawner import system_astronaut_spawner
from src.ecs.systems.s_attach_to import system_attach_to
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_burner import system_burner
from src.ecs.systems.s_collision import (
    system_collision,
    system_bullet_pod_collision,
    system_enemy_bomb_player_collision,
    system_enemy_bullet_player_collision,
    system_player_bullet_hits_captured_astronaut,
    system_player_crash,
)
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_parallax import system_parallax
from src.ecs.systems.s_play_game_state import system_play_game_state
from src.ecs.systems.s_player_input import system_player_input
from src.ecs.systems.s_player_rescue import system_player_rescue
from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_hud import system_hud
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_bullet import system_screen_bullet
from src.ecs.systems.s_screen_player_bounds import system_screen_player_bounds
from src.ecs.systems.s_terrain_rendering import system_terrain_rendering
from src.ecs.systems.s_minimap import system_minimap
from src.engine.scene import Scene
from src.engine.service_locator import ServiceLocator


class PlayScene(Scene):
    # Escena principal de juego: carga recursos, controla el bucle
    # de actualización y administra estados como vidas y puntaje.
    def __init__(self, screen_w: int, screen_h: int) -> None:
        super().__init__()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.is_paused = False
        self._game_over = False
        self.camera_x: float = 0.0
        self.player_entity: int | None = None
        self.player_velocity: CVelocity | None = None
        # Estado del jugador, configuración cargada y contadores.
        self.player_config: dict = {}
        self.bullets_config: dict = {}
        self.world_config: dict = {}
        self.level_config: dict = {}
        self.interface_config: dict = {}
        self.astronauts_config: dict = {}
        self.enemies_config: dict = {}
        self.scores_config: dict = {}
        self._pause_entity: int | None = None
        self._terrain_entity: int | None = None
        self._game_state_entity: int | None = None

        self.world_width: int = 0
        self.lives: int = 3
        self.total_time: float = 0.0
        self._game_over_entity: int | None = None
        self.spawner_config: dict = {}

        # Pausa tras la muerte del jugador: deja correr solo la animación
        # de la explosión antes de reiniciar enemigos y astronautas.
        self._death_pause_timer: float = 0.0
        self._death_pause_duration: float = 3.0
        self._pending_game_over: bool = False

    def on_enter(self, payload: dict | None = None) -> None:
        self.player_config = ServiceLocator.config_service.get(
            "assets/cfg/player.json"
        )
        self.bullets_config = ServiceLocator.config_service.get(
            "assets/cfg/bullets.json"
        )
        self.world_config = ServiceLocator.config_service.get(
            "assets/cfg/world.json"
        )
        self.level_config = ServiceLocator.config_service.get(
            "assets/cfg/level_01.json"
        )
        self.interface_config = ServiceLocator.config_service.get(
            "assets/cfg/interface.json"
        )
        self.astronauts_config = ServiceLocator.config_service.get(
            "assets/cfg/astronauts.json"
        )
        self.enemies_config = ServiceLocator.config_service.get(
            "assets/cfg/enemies.json"
        )
        self.scores_config = ServiceLocator.config_service.get(
            "assets/cfg/scores.json"
        )
        self.spawner_config = ServiceLocator.config_service.get(
            "assets/cfg/spawner.json"
        )

        base_world_w = self.level_config.get("world", {}).get("width", self.screen_w)
        repeats = self.world_config.get("world_repeats", 1)
        self.world_width = base_world_w * repeats

        self.world.clear_database()
        self.is_paused = False
        self._game_over = False
        # Reiniciar vidas y temporizadores al comenzar nivel.
        self.camera_x = 0.0
        self.lives = self.level_config.get("lives", 3)
        self.total_time = 0.0
        self._death_pause_timer = 0.0
        self._pending_game_over = False
        self._death_pause_duration = self.level_config.get("death_pause_duration", 3.0)

        astronaut_count = self.level_config.get("astronauts_count", 10)
        spawn_duration = self.level_config.get("astronaut_spawn_duration", 5.0)
        spawn_times = sorted(
            random.uniform(0, spawn_duration) for _ in range(astronaut_count)
        )

        create_starfield(
            self.world, self.world_config, self.screen_w, self.screen_h
        )

        self._terrain_entity, terrain_heights = create_terrain(
            self.world, self.world_config, self.world_width, self.screen_h
        )

        astro_cfg = self.astronauts_config.get("Astronaut", {})
        astro_img = ServiceLocator.images_service.get(astro_cfg["image"])
        astro_sprite_h = astro_img.get_height()

        create_astronaut_spawner(
            self.world, spawn_times, astro_cfg,
            self.world_width, terrain_heights, astro_sprite_h, self.screen_h
        )

        self.player_entity = create_player(
            self.world, self.player_config,
            self.level_config["player_spawn"]
        )
        self.player_velocity = self.world.component_for_entity(
            self.player_entity, CVelocity
        )

        create_input_player(self.world)
        create_input_scene(self.world)

        score_entity = create_hud(self.world, self.interface_config)
        self._pause_entity = create_pause_text(
            self.world, self.interface_config, self.screen_w, self.screen_h
        )
        self._game_over_entity = self._create_game_over_text()

        game_over_sound = self.interface_config.get(
            "game_over", {}
        ).get("sound", "assets/snd/game_over.ogg")
        self._game_state_entity = create_play_game_state(
            self.world, self.player_entity, score_entity, self._game_over_entity,
            self.screen_w, game_over_sound, self.lives
        )

        create_fixed_enemy_spawner(
            self.world, self.level_config["enemy_spawn_events"], self.enemies_config
        )
        create_random_enemy_spawner(self.world, self.spawner_config)

        fanfare = self.level_config.get("fanfare_sound")
        if fanfare:
            ServiceLocator.sounds_service.play(fanfare)

    def _create_game_over_text(self) -> int:
        go_cfg = self.interface_config.get("game_over", {})
        font_path = self.interface_config.get("font", "")
        text = go_cfg.get("text", "GAME OVER")
        size = go_cfg.get("size", 16)
        color = go_cfg.get("color", {"r": 255, "g": 0, "b": 0})
        rgb = (color["r"], color["g"], color["b"])

        font = ServiceLocator.fonts_service.get(font_path, size)
        text_surface = font.render(text, True, rgb)
        center_x = (self.screen_w - text_surface.get_width()) // 2
        center_y = (self.screen_h - text_surface.get_height()) // 2

        entity = self.world.create_entity()
        self.world.add_component(entity, CTransform(pygame.Vector2(center_x, center_y)))
        c_text = CText(text, font_path, size, rgb)
        c_text.surface = text_surface
        c_text.visible = False
        self.world.add_component(entity, c_text)
        self.world.add_component(entity, CTagHUD())
        return entity

    def process_event(self, event: pygame.event.Event) -> None:
        system_player_input(self.world, event, self._do_action)

    def _do_action(self, c_input: CInputCommand) -> None:
        # Manejo de entrada de usuario: pausa, volver al menú y control del jugador.
        if c_input.name == "PAUSE":
            if c_input.phase == CommandPhase.START and not self._game_over:
                self.is_paused = not self.is_paused
                if self._pause_entity is not None:
                    c_text = self.world.component_for_entity(
                        self._pause_entity, CText
                    )
                    c_text.visible = self.is_paused
            return
        elif c_input.name == "BACK_TO_MENU":
            if c_input.phase == CommandPhase.START:
                ServiceLocator.scenes_service.switch_to("MENU")
            return
        elif c_input.name == "MENU_SELECT":
            if c_input.phase == CommandPhase.START and self._game_over:
                # Enter en pantalla de Game Over vuelve al menú principal.
                ServiceLocator.scenes_service.switch_to("MENU")
            return

        if self.is_paused or self._game_over or self.player_velocity is None:
            return
        speed = self.player_config["input_velocity"]
        # El parámetro input_velocity define la velocidad de movimiento del jugador.

        if c_input.name == "PLAYER_LEFT":
            if c_input.phase == CommandPhase.START:
                self.player_velocity.velocity.x = -speed
            elif (c_input.phase == CommandPhase.END
                  and self.player_velocity.velocity.x < 0):
                self.player_velocity.velocity.x = 0
        elif c_input.name == "PLAYER_RIGHT":
            if c_input.phase == CommandPhase.START:
                self.player_velocity.velocity.x = speed
            elif (c_input.phase == CommandPhase.END
                  and self.player_velocity.velocity.x > 0):
                self.player_velocity.velocity.x = 0
        elif c_input.name == "PLAYER_UP":
            if c_input.phase == CommandPhase.START:
                self.player_velocity.velocity.y = -speed
            elif (c_input.phase == CommandPhase.END
                  and self.player_velocity.velocity.y < 0):
                self.player_velocity.velocity.y = 0
        elif c_input.name == "PLAYER_DOWN":
            if c_input.phase == CommandPhase.START:
                self.player_velocity.velocity.y = speed
            elif (c_input.phase == CommandPhase.END
                  and self.player_velocity.velocity.y > 0):
                self.player_velocity.velocity.y = 0
        elif c_input.name == "PLAYER_FIRE":
            if c_input.phase == CommandPhase.START:
                self._fire()

    def _fire(self) -> None:
        # Dispara una bala desde la posición actual del jugador.
        if self.player_entity is None:
            return
        player_t = self.world.component_for_entity(
            self.player_entity, CTransform
        )
        player_s = self.world.component_for_entity(
            self.player_entity, CSurface
        )
        player_state = self.world.component_for_entity(
            self.player_entity, CPlayerState
        )
        create_bullet_player(
            self.world, self.bullets_config["player_bullet"],
            player_t.position, (player_s.area.w, player_s.area.h),
            player_state.horizontal_direction
        )

    def _start_death_sequence(self, will_game_over: bool) -> None:
        # Inicia la pausa tras la muerte del jugador. Decrementa la vida,
        # spawnea una explosión prolongada en la posición de la nave y elimina
        # al jugador. El reinicio (o game over) se hace al expirar la pausa.
        if self._death_pause_timer > 0:
            return
        self._pending_game_over = will_game_over
        self._death_pause_timer = self._death_pause_duration

        explosion_center: pygame.Vector2 | None = None
        if self.player_entity is not None and self.world.entity_exists(self.player_entity):
            try:
                p_transform = self.world.component_for_entity(self.player_entity, CTransform)
                p_surface = self.world.component_for_entity(self.player_entity, CSurface)
                explosion_center = p_transform.position + pygame.Vector2(
                    p_surface.area.w / 2, p_surface.area.h / 2
                )
            except Exception:
                explosion_center = None

        if explosion_center is not None:
            self._spawn_player_explosion(explosion_center)

        self.lives = max(0, self.lives - 1)
        if self._game_state_entity is not None:
            gs = self.world.component_for_entity(self._game_state_entity, CPlayGameState)
            gs.lives = self.lives
            gs.player_entity = -1

        if self.player_entity is not None:
            for ent, (c_attach,) in list(self.world.get_components(CAttachTo)):
                if c_attach.parent_id == self.player_entity:
                    self.world.delete_entity(ent)
            if self.world.entity_exists(self.player_entity):
                self.world.delete_entity(self.player_entity)
        self.player_entity = None
        self.player_velocity = None

    def _spawn_player_explosion(self, position: pygame.Vector2) -> None:
        # Genera partículas con lifetime largo para cubrir la pausa de muerte.
        explosion_cfg = self.enemies_config.get("explosion", {})
        color_cfg = explosion_cfg.get("color", {"r": 255, "g": 255, "b": 255})
        color = pygame.Color(color_cfg["r"], color_cfg["g"], color_cfg["b"])
        lifetime = self._death_pause_duration * 0.85

        speeds = (30, 50, 70, 90)
        directions = (
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (-1, 1), (1, -1), (-1, -1),
        )
        for speed in speeds:
            for dx, dy in directions:
                ent = self.world.create_entity()
                self.world.add_component(ent, CTransform(pygame.Vector2(position)))
                self.world.add_component(
                    ent, CVelocity(pygame.Vector2(dx * speed, dy * speed))
                )
                self.world.add_component(ent, CSurface(pygame.Vector2(2, 2), color))
                self.world.add_component(ent, CLifetime(lifetime))
                self.world.add_component(ent, CTagParticle())

    def _tick_death_pause(self, dt: float) -> None:
        # Avanza solo partículas (transform + lifetime) y la animación general.
        self._death_pause_timer -= dt

        for ent, (c_transform, c_velocity) in list(
            self.world.get_components(CTransform, CVelocity)
        ):
            if self.world.has_component(ent, CTagParticle):
                c_transform.position.x += c_velocity.velocity.x * dt
                c_transform.position.y += c_velocity.velocity.y * dt

        for ent, c_lifetime in list(self.world.get_component(CLifetime)):
            if self.world.has_component(ent, CTagParticle):
                c_lifetime.time_left -= dt
                if c_lifetime.time_left <= 0:
                    self.world.delete_entity(ent)

        if self._death_pause_timer <= 0:
            if self._pending_game_over:
                self._do_game_over()
            else:
                self._respawn_after_death()

        self.world._clear_dead_entities()

    def _respawn_after_death(self) -> None:
        # Borra enemigos, astronautas y proyectiles; reinicia spawners y revive al jugador.
        for ent, _ in list(self.world.get_component(CTagEnemy)):
            self.world.delete_entity(ent)
        for ent, _ in list(self.world.get_component(CTagAstronaut)):
            self.world.delete_entity(ent)
        for ent, _ in list(self.world.get_component(CTagBulletPlayer)):
            self.world.delete_entity(ent)
        for ent, _ in list(self.world.get_component(CTagParticle)):
            self.world.delete_entity(ent)

        for ent, _ in list(self.world.get_component(CAstronautSpawner)):
            self.world.delete_entity(ent)
        for ent, _ in list(self.world.get_component(CFixedEnemySpawner)):
            self.world.delete_entity(ent)
        for ent, _ in list(self.world.get_component(CRandomEnemySpawner)):
            self.world.delete_entity(ent)

        self.total_time = 0.0

        terrain_heights: list[float] = []
        for _, (c_terrain,) in self.world.get_components(CTerrain):
            terrain_heights = c_terrain.heights
            break

        astronaut_count = self.level_config.get("astronauts_count", 10)
        spawn_duration = self.level_config.get("astronaut_spawn_duration", 5.0)
        spawn_times = sorted(
            random.uniform(0, spawn_duration) for _ in range(astronaut_count)
        )
        astro_cfg = self.astronauts_config.get("Astronaut", {})
        astro_img = ServiceLocator.images_service.get(astro_cfg["image"])
        astro_sprite_h = astro_img.get_height()

        create_astronaut_spawner(
            self.world, spawn_times, astro_cfg,
            self.world_width, terrain_heights, astro_sprite_h, self.screen_h
        )
        create_fixed_enemy_spawner(
            self.world, self.level_config["enemy_spawn_events"], self.enemies_config
        )
        create_random_enemy_spawner(self.world, self.spawner_config)

        self.player_entity = create_player(
            self.world, self.player_config,
            self.level_config["player_spawn"]
        )
        self.player_velocity = self.world.component_for_entity(
            self.player_entity, CVelocity
        )

        if self._game_state_entity is not None:
            gs = self.world.component_for_entity(self._game_state_entity, CPlayGameState)
            gs.player_entity = self.player_entity

    def _do_game_over(self) -> None:
        # Activa el game over directamente: el sistema sólo manejará el parpadeo.
        self._game_over = True
        if self._game_state_entity is not None:
            gs = self.world.component_for_entity(self._game_state_entity, CPlayGameState)
            gs.lives = 0
            gs.game_over = True
            if gs.game_over_entity is not None:
                try:
                    self.world.component_for_entity(gs.game_over_entity, CText).visible = True
                except Exception:
                    pass
            if gs.game_over_sound:
                ServiceLocator.sounds_service.play(gs.game_over_sound)

    def update(self, dt: float) -> None:
        # Ciclo principal de actualización: fisicas, enemigos, controles y HUD.
        if self.is_paused:
            system_blink(self.world, dt)
            return
        if self._game_over:
            system_play_game_state(self.world, 0, dt)
            return

        if self._death_pause_timer > 0:
            self._tick_death_pause(dt)
            return

        system_astronaut_spawner(self.world, dt)
        self.total_time += dt

        system_movement(self.world, dt)
        system_attach_to(self.world)
        system_parallax(
            self.world, self.player_velocity, self.screen_w, dt # type: ignore
        )
        system_screen_player_bounds(
            self.world, self.screen_w, self.screen_h, self.world_width
        )
        system_screen_bullet(self.world, dt, self.camera_x, self.screen_w)

        lander_cfg = self.enemies_config.get("Lander", {})
        mutant_cfg = self.enemies_config.get("Mutant", {})
        astro_cfg = self.astronauts_config.get("Astronaut", {})
        explosion_cfg = self.enemies_config.get("explosion", {})
        if system_player_bullet_hits_captured_astronaut(self.world):
            self._start_death_sequence(will_game_over=self.lives <= 1)
            return

        if system_player_crash(self.world, explosion_cfg):
            self._start_death_sequence(will_game_over=self.lives <= 1)
            return
        points_per_enemy = self.scores_config.get("points_per_enemy", 150)
        points_per_rescued = self.scores_config.get("points_per_rescued_astronaut", 250)
        font_path = self.interface_config.get("font", "")

        score_delta = system_collision(
            self.world, explosion_cfg, lander_cfg, mutant_cfg,
            astro_cfg, points_per_enemy, self.world_width
        )
        score_delta += system_player_rescue(
            self.world, points_per_rescued,
            self.camera_x, self.world_width, astro_cfg, font_path
        )
        score_delta += system_astronaut(
            self.world, astro_cfg, points_per_rescued,
            self.camera_x, self.world_width, font_path
        )

        system_play_game_state(self.world, score_delta, dt)

        if self._game_state_entity is not None:
            gs = self.world.component_for_entity(
                self._game_state_entity, CPlayGameState
            )
            self._game_over = gs.game_over
            self.camera_x = gs.camera_x
            self.lives = gs.lives

        # El puntaje aumenta por destruir enemigos y rescatar astronautas.
        system_player_state(self.world)
        system_burner(self.world)
        system_lander_state(self.world, dt, self.enemies_config["Lander"], self.bullets_config["enemy_bullet"], self.player_entity, self.screen_h, self.world_width) # type: ignore
        system_mutant_state(self.world, dt, self.enemies_config["Mutant"], self.bullets_config["enemy_bullet"], self.player_entity) # type: ignore
        system_baiter_state(self.world, dt, self.enemies_config["Baiter"], self.bullets_config["enemy_bullet"], self.player_entity) # type: ignore
        system_bomber_state(self.world, dt, self.enemies_config["Bomber"], self.screen_h, self.world_width)
        system_pod_state(self.world, dt, self.enemies_config["Pod"], self.player_entity) # type: ignore
        system_swarmer_state(self.world, dt, self.enemies_config["Swarmer"], self.bullets_config["enemy_bullet"], self.player_entity)  # type: ignore
        system_enemy_bomb_player_collision(self.world, explosion_cfg)
        system_enemy_bullet_player_collision(self.world, explosion_cfg)
        system_bullet_pod_collision(self.world, explosion_cfg)
        
        system_player_state(self.world)
        system_fixed_enemy_spawner(self.world, self.total_time)
        if self.player_entity is not None:
            system_random_enemy_spawner(self.world, dt, self.total_time, self.player_entity,
                                         self.enemies_config, self.screen_w, self.screen_h)
        system_animation(self.world, dt)

        self.world._clear_dead_entities()

    def draw(self, screen: pygame.Surface) -> None:
        header_h = self.interface_config.get("hud", {}).get("header_height", 32)
        game_surface = screen.subsurface(
            pygame.Rect(0, header_h, self.screen_w, self.screen_h)
        )
        system_terrain_rendering(self.world, game_surface, self.camera_x, self.world_width)
        system_rendering(self.world, game_surface, self.camera_x, self.world_width)
        system_hud(self.world, screen, self.interface_config, self.lives)
        system_minimap(self.world, screen, self.camera_x, self.world_width,
                      self.screen_w, self.screen_h, self.interface_config,
                      self.player_entity)
