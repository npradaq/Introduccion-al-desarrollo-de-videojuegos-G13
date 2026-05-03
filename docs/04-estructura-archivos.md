# Estructura de Archivos — Clon de Defender (G13)

Árbol planificado del repositorio. Se mantiene **alineado con el proyecto
de referencia ECS** que construimos durante el curso (mismas convenciones
de capas, naming `c_*`/`s_*`, `ServiceLocator`, `prefab_creator`, configs
JSON) y se extiende con `scenes/` y con sistemas/configuraciones
específicos de Defender.

```
Introduccion-al-desarrollo-de-videojuegos-G13/
│
├── docs/                                 # Documentos entregables
│   ├── guia-desarrollo.md
│   ├── 01-propuesta.md
│   ├── 02-arquitectura.md
│   ├── 03-diseno.md
│   ├── 04-estructura-archivos.md
│   ├── 05-plan-trabajo.md
│   ├── 06-plantilla-contribuciones.md
│   ├── 07-postmortem-grupal.md
│   ├── 08-postmortem-individual-template.md
│   └── 09-avance.md
│
├── assets/
│   ├── cfg/
│   │   ├── window.json                   # 320×256, 60fps, bg (YA EXISTE)
│   │   ├── interface.json                # textos HUD, fuente, pausa (YA EXISTE)
│   │   ├── world.json                    # estrellas + planeta + parallax (YA EXISTE)
│   │   ├── player.json                   # velocidad, inercia, sprites, sonidos
│   │   ├── lander.json                   # FSM Lander
│   │   ├── mutant.json                   # FSM Mutant
│   │   ├── astronaut.json                # FSM Astronauta
│   │   ├── bullets.json                  # player_bullet, enemy_bullet, missile
│   │   ├── level_01.json                 # timeline de spawns + #astronautas
│   │   ├── lives.json                    # (bonus) vidas iniciales + threshold
│   │   └── scores.json                   # (bonus) high score inicial 21270
│   ├── img/                              # PNG sprites
│   ├── snd/                              # OGG (web-friendly)
│   └── fnt/
│       └── PressStart2P.ttf
│
├── src/
│   ├── __init__.py
│   │
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── game_engine.py
│   │   ├── scene_manager.py
│   │   ├── config_loader.py
│   │   ├── service_locator.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── images_service.py
│   │       ├── sounds_service.py
│   │       ├── fonts_service.py
│   │       └── scenes_service.py
│   │
│   ├── scenes/
│   │   ├── __init__.py
│   │   ├── scene.py                      # base abstracta
│   │   ├── menu_scene.py
│   │   ├── play_scene.py
│   │   ├── game_over_scene.py
│   │   └── win_scene.py
│   │
│   ├── create/
│   │   ├── __init__.py
│   │   └── prefab_creator.py
│   │
│   └── ecs/
│       ├── __init__.py
│       ├── components/
│       │   ├── __init__.py
│       │   ├── c_transform.py
│       │   ├── c_velocity.py
│       │   ├── c_surface.py
│       │   ├── c_animation.py
│       │   ├── c_input_command.py
│       │   ├── c_player_state.py
│       │   ├── c_lander_state.py
│       │   ├── c_mutant_state.py
│       │   ├── c_astronaut_state.py
│       │   ├── c_wraparound.py
│       │   ├── c_parallax.py
│       │   ├── c_planet.py
│       │   ├── c_starfield.py
│       │   ├── c_lifetime.py
│       │   ├── c_score.py
│       │   ├── c_lives.py                # (bonus)
│       │   ├── c_minimap.py              # (bonus)
│       │   ├── c_smart_bomb.py           # (bonus opcional)
│       │   ├── c_camera.py               # (bonus opcional)
│       │   └── tags/
│       │       ├── __init__.py
│       │       ├── c_tag_player.py
│       │       ├── c_tag_lander.py
│       │       ├── c_tag_mutant.py
│       │       ├── c_tag_astronaut.py
│       │       ├── c_tag_bullet_player.py
│       │       ├── c_tag_bullet_enemy.py
│       │       ├── c_tag_planet.py
│       │       ├── c_tag_star.py
│       │       ├── c_tag_explosion.py
│       │       └── c_tag_hud.py
│       └── systems/
│           ├── __init__.py
│           ├── s_player_input.py
│           ├── s_movement.py
│           ├── s_animation.py
│           ├── s_rendering.py
│           ├── s_hud_rendering.py
│           ├── s_wraparound.py
│           ├── s_parallax.py
│           ├── s_player_state.py
│           ├── s_lander_state.py
│           ├── s_mutant_state.py
│           ├── s_astronaut_state.py
│           ├── s_screen_player_bounds.py
│           ├── s_collision_bullet_enemy.py
│           ├── s_collision_player_bullet.py
│           ├── s_collision_bullet_astronaut.py
│           ├── s_collision_bullet_bullet.py
│           ├── s_explosion.py
│           ├── s_particle_explosion.py
│           ├── s_enemy_spawner.py
│           ├── s_enemy_fire.py
│           ├── s_capture_astronaut.py
│           ├── s_rescue_astronaut.py
│           ├── s_score.py
│           ├── s_minimap.py              # (bonus)
│           ├── s_camera.py               # (bonus opcional)
│           └── s_smart_bomb.py           # (bonus opcional)
│
├── main.py                               # asyncio entry point
├── main.spec                             # pyinstaller (se genera al buildar)
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Notas

- Los archivos `(bonus)` se crean **solo cuando se vaya a implementar** la
  bonificación. Esta tabla los documenta para tener un mapa mental
  consistente.
- **Sin** `__pycache__`, `build/`, `dist/`, `.venv/` en repo (ignorados).
- Los recursos gráficos y sonoros del proyecto **ya están descargados** en
  `assets/img/`, `assets/snd/` y `assets/fnt/` (incluyendo sprites de
  enemigos opcionales: `enemy_baiter`, `enemy_swarmer`, `enemy_pod`,
  `enemy_bomber` — útiles si se decide ampliar la galería de enemigos
  como bonificación).
- `world.json`, `interface.json` y `window.json` ya están provistos. Las
  demás configs se crearán a medida que avancen las semanas 1 y 2.
