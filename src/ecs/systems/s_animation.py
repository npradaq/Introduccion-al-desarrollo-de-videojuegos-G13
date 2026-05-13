"""import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_enemy import CTagEnemy


def system_animation(world: esper.World, dt: float) -> None:
    components = world.get_components(CAnimation, CSurface)

    for _, (c_animation, c_surface) in components:

        anim = c_animation.animations[c_animation.current_animation]
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
        
        rect_surf = c_surface.surface.get_rect()
        c_surface.area.w = rect_surf.w / c_animation.number_frames
        c_surface.area.x = c_surface.area.w*c_animation.current_frame"""

import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_surface import CSurface

def system_animation(world:esper.World, delta_time: float):
    components = world.get_components(CSurface, CAnimation)

    for _, (c_s, c_a) in components:

        c_a.current_animation_time -= delta_time

        if c_a.current_animation_time <= 0:
            c_a.current_animation_time = c_a.animations_list[c_a.curret_anim].framerate

            c_a.curr_frame += 1

            if c_a.curr_frame > c_a.animations_list[c_a.curret_anim].end:
                c_a.curr_frame = c_a.animations_list[c_a.curret_anim].start

            rect_surf = c_s.surface.get_rect()
            c_s.area.w = rect_surf.w / c_a.number_frames
            c_s.area.x = c_s.area.w*c_a.curr_frame


