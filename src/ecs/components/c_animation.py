class Animation:
    def __init__(self, name: str, start: int, end: int, framerate: int) -> None:
        self.name = name
        self.start = start
        self.end = end
        self.framerate = framerate


class CAnimation:
    def __init__(self, animations_info: dict) -> None:
        self.number_frames = animations_info["number_frames"]
        self.animations_dict: dict[str, Animation] = {}
        for anim_info in animations_info["list"]:
            anim = Animation(
                anim_info["name"], anim_info["start"],
                anim_info["end"], anim_info["framerate"]
            )
            self.animations_dict[anim.name] = anim
        first = animations_info["list"][0]
        self.current_animation = first["name"]
        self.current_frame = first["start"]
        self.current_animation_time = 0.0
        self.finished = False
