import esper

from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_velocity import CVelocity


def system_player_state(world: esper.World) -> None:
    components = world.get_components(CVelocity, CPlayerState)
    for _, (c_velocity, c_player_state) in components:
        moving = c_velocity.velocity.length_squared() > 0
        if c_player_state.state == PlayerState.IDLE and moving:
            c_player_state.state = PlayerState.MOVE
        elif c_player_state.state == PlayerState.MOVE and not moving:
            c_player_state.state = PlayerState.IDLE
