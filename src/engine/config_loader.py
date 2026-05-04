import json


def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_window_config(path: str) -> dict:
    return _read_json(path)


def load_interface_config(path: str) -> dict:
    return _read_json(path)


def load_player_config(path: str) -> dict:
    return _read_json(path)


def load_enemies_config(path: str) -> dict:
    return _read_json(path)


def load_bullets_config(path: str) -> dict:
    return _read_json(path)


def load_world_config(path: str) -> dict:
    return _read_json(path)


def load_level_config(path: str) -> dict:
    return _read_json(path)
