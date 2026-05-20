import asyncio

import pygame

from src.engine.scene_manager import SceneManager
from src.engine.service_locator import ServiceLocator
from src.scenes.menu_scene import MenuScene
from src.scenes.play_scene import PlayScene


class GameEngine:
    def __init__(self, scale: int = 1) -> None:
        window_cfg = ServiceLocator.config_service.get("assets/cfg/window.json")

        title = window_cfg.get("title", "Defender")
        size = window_cfg.get("size", {})
        self.game_width = int(size.get("w", 320))
        self.game_height = int(size.get("h", 256))
        self.hud_height = int(window_cfg.get("hud_height", 0))
        self.scale = max(1, scale)
        self.screen_width = self.game_width * self.scale
        self.screen_height = (self.game_height + self.hud_height) * self.scale
        bg = window_cfg.get("bg_color", {})
        self.bg_color = (
            int(bg.get("r", 0)),
            int(bg.get("g", 0)),
            int(bg.get("b", 0)),
        )

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(title)
        self.game_surface = pygame.Surface(
            (self.game_width, self.game_height + self.hud_height)
        )
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.framerate = int(window_cfg.get("framerate", 60))
        self.delta_time = 0.0

        self.scene_manager = SceneManager()
        ServiceLocator.scenes_service.init(self.scene_manager)

        self._register_scenes()

    def _register_scenes(self) -> None:
        self.scene_manager.register(
            "MENU", MenuScene(self.game_width, self.game_height)
        )
        self.scene_manager.register(
            "PLAY", PlayScene(self.game_width, self.game_height)
        )

    async def run(self) -> None:
        self.scene_manager.switch_to("MENU")
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            await asyncio.sleep(0)
        self._clean()

    def _calculate_time(self) -> None:
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0

    def _process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.is_running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                # Presionar 'q' cierra el juego completamente.
                self.is_running = False
            else:
                self.scene_manager.process_event(event)

    def _update(self) -> None:
        self.scene_manager.update(self.delta_time)

    def _draw(self) -> None:
        self.game_surface.fill(self.bg_color)
        self.scene_manager.draw(self.game_surface)
        if self.scale > 1:
            scaled_surface = pygame.transform.scale(
                self.game_surface,
                (self.screen_width, self.screen_height)
            )
            self.screen.blit(scaled_surface, (0, 0))
        else:
            self.screen.blit(self.game_surface, (0, 0))
        pygame.display.flip()

    def _clean(self) -> None:
        pygame.quit()
