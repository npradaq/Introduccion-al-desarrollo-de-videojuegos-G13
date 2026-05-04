import esper
import pygame

from src.ecs.components.c_input_command import CInputCommand, CommandPhase


def system_player_input(world: esper.World, event: pygame.event.Event,
                        do_action_callback) -> None:
    inputs = world.get_component(CInputCommand)
    for _, c_input in inputs:
        if event.type == pygame.KEYDOWN and event.key == c_input.key:
            c_input.phase = CommandPhase.START
            do_action_callback(c_input)
        elif event.type == pygame.KEYUP and event.key == c_input.key:
            c_input.phase = CommandPhase.END
            do_action_callback(c_input)
