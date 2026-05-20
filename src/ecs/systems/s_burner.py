import esper

from src.ecs.components.c_animation import CAnimation, AnimationData
from src.ecs.components.c_attach_to import CAttachTo
from src.ecs.components.c_burner import CBurner
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_burner import CTagBurner
from src.ecs.components.tags.c_tag_player import CTagPlayer


def system_burner(world: esper.World) -> None:
    player_list = list(world.get_components(CPlayerState, CTagPlayer))
    if not player_list:
        return
    player_ent, (c_player_state, _) = player_list[0]
    is_moving = c_player_state.state == PlayerState.MOVE

    for _, (c_burner, c_attach, c_surface, c_anim) in world.get_components(
        CBurner, CAttachTo, CSurface, CAnimation
    ):
        if c_attach.parent_id != player_ent:
            continue

        new_surf = c_burner.moving_surface if is_moving else c_burner.idle_surface
        if c_surface.surface is new_surf:
            continue

        anim_cfg = c_burner.moving_anim_cfg if is_moving else c_burner.idle_anim_cfg
        c_surface.surface = new_surf
        c_surface.area = new_surf.get_rect()
        c_anim.number_frames = anim_cfg["number_frames"]
        for info in anim_cfg["list"]:
            c_anim.animations_list.append(AnimationData(info["name"], info["start"], info["end"], info["framerate"]))
        first = anim_cfg["list"][0]
        c_anim.curret_anim = first["start"]
        c_anim.curr_frame = first["start"]
        c_anim.current_animation_time = 0.0
