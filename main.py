#!/usr/bin/python3
"""Entry point del clon de Defender (G13)."""

import argparse
import asyncio

import pygame  # noqa: F401
import esper   # noqa: F401

from src.engine.game_engine import GameEngine


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sentinel - Defender Clone"
    )
    parser.add_argument(
        "--scale", "-s",
        type=int,
        default=2,
        help="Scale factor for display (default: 1). Useful for local development."
    )
    args = parser.parse_args()

    engine = GameEngine(scale=args.scale)
    asyncio.run(engine.run())


if __name__ == "__main__":
    main()
