import esper

from src.ecs.components.c_play_game_state import CPlayGameState
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.engine.service_locator import ServiceLocator


def system_play_game_state(world: esper.World, score_delta: int) -> None:
    for _, (state,) in world.get_components(CPlayGameState):
        state.score += score_delta

        try:
            player_t = world.component_for_entity(state.player_entity, CTransform)
            state.camera_x = player_t.position.x - state.screen_w / 2
        except Exception:
            pass

        if state.score_entity is not None:
            try:
                c_text = world.component_for_entity(state.score_entity, CText)
                new_text = str(state.score)
                if c_text.text != new_text:
                    c_text.text = new_text
                    c_text.surface = None
            except Exception:
                pass

        if not state.game_over and state.score >= state.game_over_score:
            state.game_over = True
            ServiceLocator.sounds_service.play(state.game_over_sound)
            if state.game_over_entity is not None:
                try:
                    world.component_for_entity(
                        state.game_over_entity, CText
                    ).visible = True
                except Exception:
                    pass
