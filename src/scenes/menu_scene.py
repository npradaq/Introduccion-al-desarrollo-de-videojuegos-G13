import pygame

from src.create.prefab_creator import create_image, create_text
from src.engine.scene import Scene
from src.engine.service_locator import ServiceLocator
from src.ecs.systems.s_rendering import system_rendering


class MenuScene(Scene):
    def __init__(self, screen_w: int, screen_h: int) -> None:
        super().__init__()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.interface_cfg: dict = {}
        self._loaded = False

    def on_enter(self, payload: dict | None = None) -> None:
        if not self._loaded:
            self.interface_cfg = ServiceLocator.config_service.get(
                "assets/cfg/interface.json"
            )
            self._loaded = True

        self.world.clear_database()
        menu = self.interface_cfg.get("menu", {})
        font_path = self.interface_cfg.get("font", "")

        logo_path = menu.get("logo_image")
        if logo_path:
            logo_pos = menu.get("logo_position", {"x": 0, "y": 0})
            create_image(self.world, logo_path, logo_pos)

        for instr in menu.get("instructions", []):
            create_text(
                self.world,
                instr["text"],
                font_path,
                instr["size"],
                instr["color"],
                instr["position"]
            )

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_RETURN, pygame.K_KP_ENTER
        ):
            ServiceLocator.scenes_service.switch_to("PLAY")

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        system_rendering(self.world, screen)
