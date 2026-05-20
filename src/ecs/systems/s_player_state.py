import esper

from src.ecs.components.c_attach_to import CAttachTo
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_attach_to import CAttachTo
from src.ecs.components.tags.c_tag_burner import CTagBurner
from src.ecs.components.tags.c_tag_player import CTagPlayer


def system_player_state(world: esper.World) -> None:
    components = world.get_components(CVelocity, CPlayerState)
    for _, (c_velocity, c_player_state) in components:
        moving = c_velocity.velocity.length_squared() > 0
        if c_player_state.state == PlayerState.IDLE and moving:
            c_player_state.state = PlayerState.MOVE
        elif c_player_state.state == PlayerState.MOVE and not moving:
            c_player_state.state = PlayerState.IDLE

        if c_velocity.velocity.x < 0:
            c_player_state.horizontal_direction = -1
        elif c_velocity.velocity.x > 0:
            c_player_state.horizontal_direction = 1

        player_components = world.get_components(CSurface, CTagPlayer)
        for player_ent, (c_surface, _) in player_components:
            c_surface.flip_x = c_player_state.horizontal_direction < 0

            burner_components = world.get_components(CSurface, CAttachTo, CTagBurner)
            for _, (c_burner_surface, c_attach, _) in burner_components:
                if c_attach.parent_id != player_ent:
                    continue
                c_burner_surface.flip_x = c_player_state.horizontal_direction < 0
                if c_player_state.horizontal_direction < 0:
                    c_attach.offset.x = (
                        c_surface.area.w - c_burner_surface.area.w
                        - c_attach.initial_offset.x
                    )
                else:
                    c_attach.offset.x = c_attach.initial_offset.x
