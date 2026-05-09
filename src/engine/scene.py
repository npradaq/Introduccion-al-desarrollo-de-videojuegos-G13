import esper
import pygame


class Scene:
    def __init__(self) -> None:
        self.world: esper.World = esper.World()

    def on_enter(self, payload: dict | None = None) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def process_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        pass
