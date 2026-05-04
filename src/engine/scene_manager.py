import pygame


class SceneManager:
    def __init__(self) -> None:
        self._scenes: dict = {}
        self._active_scene = None
        self._active_name: str | None = None
        self._pending_switch: tuple[str, dict | None] | None = None

    def register(self, name: str, scene) -> None:
        self._scenes[name] = scene

    def switch_to(self, name: str, payload: dict | None = None) -> None:
        if name not in self._scenes:
            raise ValueError(f"Escena no registrada: {name}")
        self._pending_switch = (name, payload)

    def _apply_pending_switch(self) -> None:
        if self._pending_switch is None:
            return
        name, payload = self._pending_switch
        if self._active_scene is not None:
            self._active_scene.on_exit()
        self._active_scene = self._scenes[name]
        self._active_name = name
        self._active_scene.on_enter(payload)
        self._pending_switch = None

    def process_event(self, event: pygame.event.Event) -> None:
        if self._active_scene is not None:
            self._active_scene.process_event(event)

    def update(self, dt: float) -> None:
        self._apply_pending_switch()
        if self._active_scene is not None:
            self._active_scene.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        if self._active_scene is not None:
            self._active_scene.draw(screen)

    @property
    def active_name(self) -> str | None:
        return self._active_name
