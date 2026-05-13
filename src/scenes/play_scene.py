import random

import pygame

from src.create.prefab_creator import (
    create_astronaut, create_bullet_player, create_hud,
    create_input_player, create_input_scene, create_lander_enemy,
    create_pause_text, create_player, create_starfield, create_terrain
)
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_hud import CTagHUD
from src.ecs.components.tags.c_tag_lander_enemy import CTagLanderEnemy
from src.ecs.components.tags.c_tag_mutant_enemy import CTagMutantEnemy
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_astronaut import system_astronaut
from src.ecs.systems.s_attach_to import system_attach_to
from src.ecs.systems.s_blink import system_blink
from src.ecs.systems.s_burner import system_burner
from src.ecs.systems.s_collision import system_collision
from src.ecs.systems.s_lander import system_lander
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_parallax import system_parallax
from src.ecs.systems.s_player_input import system_player_input
from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_hud import system_hud
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_bullet import system_screen_bullet
from src.ecs.systems.s_screen_player_bounds import system_screen_player_bounds
from src.ecs.systems.s_terrain_rendering import system_terrain_rendering
from src.engine.scene import Scene
from src.engine.service_locator import ServiceLocator


class PlayScene(Scene):
    def __init__(self, screen_w: int, screen_h: int) -> None:
        super().__init__()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self._loaded = False
        self.is_paused = False
        self._game_over = False
        self.player_entity: int | None = None
        self.player_velocity: CVelocity | None = None
        self.player_config: dict = {}
        self.bullets_config: dict = {}
        self.world_config: dict = {}
        self.level_config: dict = {}
        self.interface_config: dict = {}
        self.astronauts_config: dict = {}
        self.enemies_config: dict = {}
        self.scores_config: dict = {}
        self._pause_entity: int | None = None
        self._game_over_entity: int | None = None
        self._score_entity: int | None = None
        self._terrain_entity: int | None = None

        self.world_width: int = 0
        self.camera_x: float = 0.0
        self.lives: int = 3
        self.score: int = 0

        self._game_timer: float = 0.0
        self._astro_spawn_times: list[float] = []
        self._enemy_spawn_timer: float = 0.0
        self._total_enemies_spawned: int = 0

        self.terrain_heights: list[float] = []
        self._astro_sprite_h: int = 0

    def on_enter(self, payload: dict | None = None) -> None:
        if not self._loaded:
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
            self._loaded = True

        base_world_w = self.level_config.get("world", {}).get("width", self.screen_w)
        repeats = self.world_config.get("world_repeats", 1)
        self.world_width = base_world_w * repeats

        self.world.clear_database()
        self.is_paused = False
        self._game_over = False
        self.camera_x = 0.0
        self.score = 0
        self._game_timer = 0.0
        self._total_enemies_spawned = 0
        self._enemy_spawn_timer = 0.0

        astronaut_count = self.level_config.get("astronauts_count", 10)
        spawn_duration = self.level_config.get("astronaut_spawn_duration", 5.0)
        self._astro_spawn_times = sorted(
            random.uniform(0, spawn_duration) for _ in range(astronaut_count)
        )

        create_starfield(
            self.world, self.world_config, self.screen_w, self.screen_h
        )

        self._terrain_entity, self.terrain_heights = create_terrain(
            self.world, self.world_config, self.world_width, self.screen_h
        )

        astro_img = ServiceLocator.images_service.get(
            self.astronauts_config["Astronaut"]["image"]
        )
        self._astro_sprite_h = astro_img.get_height()

        self.player_entity = create_player(
            self.world, self.player_config,
            self.level_config["player_spawn"]
        )
        self.player_velocity = self.world.component_for_entity(
            self.player_entity, CVelocity
        )

        create_input_player(self.world)
        create_input_scene(self.world)
        self._score_entity = create_hud(self.world, self.interface_config)
        self._pause_entity = create_pause_text(
            self.world, self.interface_config, self.screen_w, self.screen_h
        )
        self._game_over_entity = self._create_game_over_text()

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

        if self.is_paused or self._game_over or self.player_velocity is None:
            return
        speed = self.player_config["input_velocity"]

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
        if self.player_entity is None:
            return
        player_t = self.world.component_for_entity(
            self.player_entity, CTransform
        )
        player_s = self.world.component_for_entity(
            self.player_entity, CSurface
        )
        create_bullet_player(
            self.world, self.bullets_config["player_bullet"],
            player_t.position, (player_s.area.w, player_s.area.h)
        )

    def _update_camera(self) -> None:
        if self.player_entity is None:
            return
        player_t = self.world.component_for_entity(
            self.player_entity, CTransform
        )
        self.camera_x = player_t.position.x - self.screen_w / 2

    def _spawn_astronauts(self) -> None:
        astro_cfg = self.astronauts_config.get("Astronaut", {})
        levels = astro_cfg.get("levels", [0.70, 0.80, 0.90])
        while (self._astro_spawn_times
               and self._game_timer >= self._astro_spawn_times[0]):
            x = random.uniform(0, self.world_width)
            xi = int(x) % self.world_width
            if self.terrain_heights:
                y = self.terrain_heights[xi] - self._astro_sprite_h
            else:
                level_ratio = random.choice(levels)
                y = self.screen_h * level_ratio
            create_astronaut(self.world, astro_cfg, pygame.Vector2(x, y))
            self._astro_spawn_times.pop(0)

    def _spawn_enemies(self, dt: float) -> None:
        lander_cfg = self.enemies_config.get("Lander", {})
        max_concurrent = lander_cfg.get("max_concurrent", 5)
        max_total = lander_cfg.get("max_total", 20)
        spawn_interval = lander_cfg.get("spawn_interval", 3.0)
        enemy_start_delay = self.level_config.get("enemy_start_delay", 5.0)

        if self._game_timer < enemy_start_delay:
            return
        if self._total_enemies_spawned >= max_total:
            return

        alive = len(list(self.world.get_component(CTagLanderEnemy)))
        if alive >= max_concurrent:
            return

        self._enemy_spawn_timer += dt
        if self._enemy_spawn_timer < spawn_interval:
            return
        self._enemy_spawn_timer = 0.0

        x = random.uniform(0, self.world_width)
        y = random.uniform(self.screen_h * 0.05, self.screen_h * 0.5)
        create_lander_enemy(self.world, lander_cfg, pygame.Vector2(x, y))
        self._total_enemies_spawned += 1

    def _trigger_game_over(self) -> None:
        self._game_over = True
        sound = self.interface_config.get("game_over", {}).get("sound", "assets/snd/game_over.ogg")
        ServiceLocator.sounds_service.play(sound)
        if self._game_over_entity is not None:
            self.world.component_for_entity(
                self._game_over_entity, CText
            ).visible = True

    def _update_score_display(self) -> None:
        if self._score_entity is None:
            return
        c_text = self.world.component_for_entity(self._score_entity, CText)
        new_text = str(self.score)
        if c_text.text != new_text:
            c_text.text = new_text
            c_text.surface = None

    def update(self, dt: float) -> None:
        if self.is_paused:
            system_blink(self.world, dt)
            return
        if self._game_over:
            return

        self._game_timer += dt
        self._spawn_astronauts()
        self._spawn_enemies(dt)

        system_movement(self.world, dt)
        system_attach_to(self.world)
        system_parallax(
            self.world, self.player_velocity, self.screen_w, dt
        )
        system_screen_player_bounds(
            self.world, self.screen_w, self.screen_h, self.world_width
        )
        system_screen_bullet(self.world, dt)

        lander_cfg = self.enemies_config.get("Lander", {})
        mutant_cfg = self.enemies_config.get("Mutant", {})
        astro_cfg = self.astronauts_config.get("Astronaut", {})
        explosion_cfg = self.enemies_config.get("explosion", {})
        points_per_enemy = self.scores_config.get("points_per_enemy", 150)
        points_per_rescued = self.scores_config.get("points_per_rescued_astronaut", 250)
        game_over_score = self.scores_config.get("game_over_score", 2000)

        system_lander(
            self.world, dt, self.screen_h, self.world_width,
            self.player_entity, lander_cfg, mutant_cfg
        )

        self.score += system_collision(
            self.world, explosion_cfg, lander_cfg, mutant_cfg,
            astro_cfg, points_per_enemy
        )

        self.score += system_astronaut(
            self.world, astro_cfg, points_per_rescued
        )

        system_player_state(self.world)
        system_burner(self.world)
        system_animation(self.world, dt)
        self._update_camera()
        self._update_score_display()

        if self.score >= game_over_score:
            self._trigger_game_over()

        self.world._clear_dead_entities()

    def draw(self, screen: pygame.Surface) -> None:
        header_h = self.interface_config.get("hud", {}).get("header_height", 32)
        game_surface = screen.subsurface(
            pygame.Rect(0, header_h, self.screen_w, self.screen_h)
        )
        system_terrain_rendering(self.world, game_surface, self.camera_x, self.world_width)
        system_rendering(self.world, game_surface, self.camera_x, self.world_width)
        system_hud(self.world, screen, self.interface_config, self.lives)
