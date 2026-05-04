import pygame

from src.engine.config_loader import load_interface_config
from src.engine.service_locator import ServiceLocator
from src.scenes.scene import Scene


class MenuScene(Scene):
    def __init__(self, screen_w: int, screen_h: int) -> None:
        super().__init__()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.interface_cfg: dict = {}
        self._loaded = False

    def on_enter(self, payload: dict | None = None) -> None:
        if not self._loaded:
            self.interface_cfg = load_interface_config(
                "assets/cfg/interface.json"
            )
            self._loaded = True

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_RETURN, pygame.K_KP_ENTER
        ):
            ServiceLocator.scenes_service.switch_to("PLAY")

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        menu = self.interface_cfg.get("menu", {})
        font_path = self.interface_cfg.get("font", "")

        logo_path = menu.get("logo_image")
        if logo_path:
            logo = ServiceLocator.images_service.get(logo_path)
            logo_pos = menu.get("logo_position", {"x": 0, "y": 0})
            screen.blit(logo, (logo_pos["x"], logo_pos["y"]))

        for instr in menu.get("instructions", []):
            font = ServiceLocator.fonts_service.get(font_path, instr["size"])
            color = instr["color"]
            surf = font.render(
                instr["text"], True,
                (color["r"], color["g"], color["b"])
            )
            pos = instr["position"]
            screen.blit(surf, (pos["x"], pos["y"]))
