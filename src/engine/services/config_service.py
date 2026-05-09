import json


class ConfigService:
    def __init__(self) -> None:
        self._cache: dict[str, dict] = {}

    def get(self, path: str) -> dict:
        if path not in self._cache:
            with open(path, encoding="utf-8") as f:
                self._cache[path] = json.load(f)
        return self._cache[path]
