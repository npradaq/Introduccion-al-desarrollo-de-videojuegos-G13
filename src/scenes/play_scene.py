import pygame

from src.create.prefab_creator import (
    create_bullet_player, create_input_player, create_player, create_starfield
)
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_attach_to import system_attach_to
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_parallax import system_parallax
from src.ecs.systems.s_player_input import system_player_input
from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_bullet import system_screen_bullet
from src.ecs.systems.s_screen_player_bounds import system_screen_player_bounds
from src.engine.config_loader import (
    load_bullets_config, load_interface_config, load_level_config,
    load_player_config, load_world_config
)
from src.engine.service_locator import ServiceLocator
from src.scenes.scene import Scene


class PlayScene(Scene):
    def __init__(self, screen_w: int, screen_h: int) -> None:
        super().__init__()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self._loaded = False
        self.is_paused = False
        self.player_entity: int | None = None
        self.player_velocity: CVelocity | None = None
        self.player_config: dict = {}
        self.bullets_config: dict = {}
        self.world_config: dict = {}
        self.level_config: dict = {}
        self.interface_config: dict = {}
        self._pause_blink_time = 0.0

    def on_enter(self, payload: dict | None = None) -> None:
        if not self._loaded:
            self.player_config = load_player_config("assets/cfg/player.json")
            self.bullets_config = load_bullets_config(
                "assets/cfg/bullets.json"
            )
            self.world_config = load_world_config("assets/cfg/world.json")
            self.level_config = load_level_config("assets/cfg/level_01.json")
            self.interface_config = load_interface_config(
                "assets/cfg/interface.json"
            )
            self._loaded = True

        self.world.clear_database()
        self.is_paused = False
        self._pause_blink_time = 0.0

        create_starfield(
            self.world, self.world_config, self.screen_w, self.screen_h
        )

        self.player_entity = create_player(
            self.world, self.player_config,
            self.level_config["player_spawn"]
        )
        self.player_velocity = self.world.component_for_entity(
            self.player_entity, CVelocity
        )

        create_input_player(self.world)

        fanfare = self.level_config.get("fanfare_sound")
        if fanfare:
            ServiceLocator.sounds_service.play(fanfare)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self.is_paused = not self.is_paused
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
            ServiceLocator.scenes_service.switch_to("MENU")
            return
        system_player_input(self.world, event, self._do_action)

    def _do_action(self, c_input: CInputCommand) -> None:
        if self.is_paused or self.player_velocity is None:
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

    def update(self, dt: float) -> None:
        if self.is_paused:
            self._pause_blink_time += dt
            return

        system_movement(self.world, dt)
        system_attach_to(self.world)
        system_parallax(
            self.world, self.player_velocity, self.screen_w, dt
        )
        system_screen_player_bounds(
            self.world, self.screen_w, self.screen_h
        )
        system_screen_bullet(self.world, dt)
        system_player_state(self.world)
        system_animation(self.world, dt)

        self.world._clear_dead_entities()

    def draw(self, screen: pygame.Surface) -> None:
        system_rendering(self.world, screen, hide_player=self.is_paused)

        hud_cfg = self.interface_config.get("hud", {})
        font_path = self.interface_config.get("font", "")
        for key in ("score_label", "score_value"):
            cfg = hud_cfg.get(key)
            if cfg is None:
                continue
            font = ServiceLocator.fonts_service.get(font_path, cfg["size"])
            text = cfg.get("text", "0")
            color = cfg["color"]
            surf = font.render(
                text, True, (color["r"], color["g"], color["b"])
            )
            pos = cfg["position"]
            screen.blit(surf, (pos["x"], pos["y"]))

        if self.is_paused:
            pause_cfg = self.interface_config.get("pause", {})
            blink_rate = pause_cfg.get("blink_rate", 2.0)
            visible = (self._pause_blink_time * blink_rate) % 2 < 1
            if visible:
                font = ServiceLocator.fonts_service.get(
                    font_path, pause_cfg.get("size", 16)
                )
                color = pause_cfg.get(
                    "color", {"r": 255, "g": 255, "b": 255}
                )
                surf = font.render(
                    pause_cfg.get("text", "PAUSED"), True,
                    (color["r"], color["g"], color["b"])
                )
                w, h = screen.get_size()
                screen.blit(
                    surf,
                    ((w - surf.get_width()) // 2,
                     (h - surf.get_height()) // 2)
                )
