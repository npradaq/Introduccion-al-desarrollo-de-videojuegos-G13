class ScenesService:
    def __init__(self) -> None:
        self._scene_manager = None

    def init(self, scene_manager) -> None:
        self._scene_manager = scene_manager

    def switch_to(self, scene_name: str, payload: dict | None = None) -> None:
        if self._scene_manager is None:
            return
        self._scene_manager.switch_to(scene_name, payload)
