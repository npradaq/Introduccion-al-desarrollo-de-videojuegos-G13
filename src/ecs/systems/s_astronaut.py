import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_astronaut_state import AstronautPhase, CAstronautState
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut
from src.engine.service_locator import ServiceLocator


def system_astronaut(world: esper.World, astronaut_cfg: dict,
                     points_per_rescued: int) -> int:
    """Returns score delta from rescued astronauts landing."""
    score_delta = 0
    sound_rescued = astronaut_cfg.get("sound_rescued", "")

    for ent, (ct, cv, canim, cstate) in world.get_components(
            CTransform, CVelocity, CAnimation, CAstronautState):
        if not world.has_component(ent, CTagAstronaut):
            continue

        if cstate.phase == AstronautPhase.FALLING:
            if ct.position.y >= cstate.land_y:
                ct.position.y = cstate.land_y
                cv.velocity.y = 0
                cstate.phase = AstronautPhase.LANDED

        elif cstate.phase == AstronautPhase.RESCUED:
            if ct.position.y >= cstate.land_y:
                ct.position.y = cstate.land_y
                cv.velocity.y = 0
                cstate.phase = AstronautPhase.LANDED
                score_delta += points_per_rescued
                if sound_rescued:
                    ServiceLocator.sounds_service.play(sound_rescued)

        # LANDED and CAPTURED: no position changes needed here

    return score_delta
