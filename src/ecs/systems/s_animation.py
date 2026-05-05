import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_surface import CSurface


def system_animation(world: esper.World, dt: float) -> None:
    components = world.get_components(CAnimation, CSurface)
    for _, (c_animation, c_surface) in components:
        anim = c_animation.animations_dict[c_animation.current_animation]
        c_animation.current_animation_time += dt
        frame_duration = 1.0 / max(anim.framerate, 1)
        if c_animation.current_animation_time >= frame_duration:
            c_animation.current_animation_time = 0.0
            c_animation.current_frame += 1
            if c_animation.current_frame > anim.end:
                c_animation.current_frame = anim.start
                c_animation.finished = True
            else:
                c_animation.finished = False
        frame_width = c_surface.surface.get_width() / max(c_animation.number_frames, 1)
        c_surface.area.x = int(frame_width * c_animation.current_frame)
        c_surface.area.w = int(frame_width)
