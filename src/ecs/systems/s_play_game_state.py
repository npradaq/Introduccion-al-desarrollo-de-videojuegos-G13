import esper

from src.ecs.components.c_astronaut_spawner import CAstronautSpawner
from src.ecs.components.c_play_game_state import CPlayGameState
from src.ecs.components.c_text import CText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_astronaut import CTagAstronaut
from src.engine.service_locator import ServiceLocator


def _trigger_game_over(world: esper.World, state: CPlayGameState) -> None:
    state.game_over = True
    ServiceLocator.sounds_service.play(state.game_over_sound)
    if state.game_over_entity is not None:
        try:
            world.component_for_entity(state.game_over_entity, CText).visible = True
        except Exception:
            pass


def system_play_game_state(world: esper.World, score_delta: int, dt: float) -> None:
    for _, (state,) in world.get_components(CPlayGameState):
        if state.game_over:
            if state.game_over_entity is not None:
                state.game_over_blink_timer += dt
                try:
                    c_text = world.component_for_entity(state.game_over_entity, CText)
                    c_text.visible = (
                        state.game_over_blink_timer * state.game_over_blink_rate
                    ) % 2 < 1
                except Exception:
                    pass
            return

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

        if state.lives <= 0:
            _trigger_game_over(world, state)
            return

        spawners = list(world.get_components(CAstronautSpawner))
        if spawners:
            spawner = spawners[0][1][0]
            all_spawned = spawner.total_to_spawn > 0 and len(spawner.spawn_times) == 0
            no_astronauts = len(list(world.get_component(CTagAstronaut))) == 0
            if all_spawned and no_astronauts:
                _trigger_game_over(world, state)
