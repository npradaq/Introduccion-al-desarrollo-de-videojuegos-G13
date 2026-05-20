class CPlayGameState:
    def __init__(self, player_entity: int, score_entity: int | None,
                 game_over_entity: int | None, screen_w: int,
                 game_over_sound: str, lives: int = 3,
                 game_over_blink_rate: float = 2.0) -> None:
        self.player_entity = player_entity
        self.score_entity = score_entity
        self.game_over_entity = game_over_entity
        self.screen_w = screen_w
        self.game_over_sound = game_over_sound
        self.lives = lives
        self.game_over_blink_rate = game_over_blink_rate
        self.camera_x: float = 0.0
        self.score: int = 0
        self.game_over: bool = False
        self.game_over_blink_timer: float = 0.0
