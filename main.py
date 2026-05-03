#!/usr/bin/python3
"""Entry point del clon de Defender (G13)."""

import asyncio

import pygame  # noqa: F401
import esper   # noqa: F401

from src.engine.game_engine import GameEngine


if __name__ == "__main__":
    engine = GameEngine()
    asyncio.run(engine.run())
