"""from typing import List


class Animation:
    def __init__(self, name: str, start: int, end: int, framerate: int) -> None:
        self.name = name
        self.start = start
        self.end = end
        self.framerate = 1.0/framerate


class CAnimation:
    def __init__(self, animations_info: dict) -> None:
        self.number_frames = animations_info["number_frames"]

        self.animations: List[Animation] = []

        for anim in animations_info["list"]:
            anim_data = Animation(anim["name"], anim["start"], anim["end"], anim["framerate"])
            self.animations.append(anim_data)

        first = animations_info["list"][0]
        self.current_animation = 0
        self.current_frame = 0
        self.current_animation_time = 0.0
        self.finished = False"""

from typing import List

class CAnimation:
    def __init__(self, animations:dict) -> None:
        self.number_frames = animations["number_frames"]
        self.animations_list: List[AnimationData] = []
        for anim in animations["list"]:
            anim_data = AnimationData(anim["name"], anim["start"], anim["end"], anim["framerate"])
            self.animations_list.append(anim_data)

        self.curret_anim = 0
        self.current_animation_time = 0.0
        self.curr_frame = self.animations_list[self.curret_anim].start




class AnimationData:
    def __init__(self, name:str, start:int, end:int, framerate:float) -> None:
        self.name = name
        self.start = start
        self.end = end
        self.framerate = 1.0/framerate
