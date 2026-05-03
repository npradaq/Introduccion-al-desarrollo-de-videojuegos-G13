# Arquitectura — Clon de Defender (G13)

> Documento de arquitectura técnica. La guía de convenciones de bajo nivel
> (naming, prefijos, reglas) está en [docs/guia-desarrollo.md](guia-desarrollo.md).

---

## 1. Vista de alto nivel

```
                     ┌──────────────────┐
                     │    main.py       │
                     │  asyncio.run()   │
                     └────────┬─────────┘
                              │
                       ┌──────▼───────┐
                       │  GameEngine  │  loop, delta_time, ventana
                       └──────┬───────┘
                              │
                       ┌──────▼────────┐
                       │ SceneManager  │ ── ServiceLocator (services)
                       └──┬──┬──┬──┬───┘
                          │  │  │  │
                ┌─────────┘  │  │  └──────────┐
                ▼            ▼  ▼             ▼
          ┌────────┐   ┌────────┐ ┌────────┐ ┌────────┐
          │  Menu  │   │  Play  │ │GameOver│ │  Win   │
          │ Scene  │   │ Scene  │ │ Scene  │ │ Scene  │
          └────────┘   └───┬────┘ └────────┘ └────────┘
                           │
                ┌──────────▼──────────┐
                │   esper.World       │ < entidades
                │   + sistemas (s_*)  │
                │   + componentes (c_)│
                └─────────────────────┘
```

---

## 2. Capas

### 2.1 `engine/`
Componentes infraestructurales agnósticos al juego.

| Módulo                      | Responsabilidad                                                  |
|-----------------------------|------------------------------------------------------------------|
| `game_engine.py`            | Inicializa pygame, ventana, clock; ejecuta el loop principal.    |
| `scene_manager.py`          | Mantiene la escena activa, hace `switch_to`/`push`/`pop`.        |
| `config_loader.py`          | Funciones `load_*_config(path) -> dict` para cada JSON.          |
| `service_locator.py`        | Punto único de acceso a servicios (atributos de clase).          |
| `services/images_service.py`| Cache de `pygame.Surface` (load + `convert_alpha`).              |
| `services/sounds_service.py`| Cache + `play()` de `pygame.mixer.Sound`.                        |
| `services/fonts_service.py` | Cache de `pygame.font.Font` por `(path, size)`.                  |
| `services/scenes_service.py`| Wrapper sobre `SceneManager` accesible desde sistemas/escenas.   |

### 2.2 `scenes/`
Patrón State a nivel de pantalla.

```python
class Scene:                       # base
    def on_enter(self): ...
    def on_exit(self): ...
    def process_event(self, ev): ...
    def update(self, dt): ...
    def draw(self, screen): ...
```

| Escena            | Propósito                                                       |
|-------------------|-----------------------------------------------------------------|
| `MenuScene`       | Título, instrucciones, "Presiona ENTER para jugar".             |
| `PlayScene`       | Gameplay: world, sistemas, HUD.                                 |
| `GameOverScene`   | Texto GAME OVER, vuelve a `MenuScene` o reinicia.               |
| `WinScene`        | Pantalla de victoria al terminar el nivel.                      |

Cada escena instancia su propio `esper.World`. Los recursos (sprites,
sonidos) **se comparten** vía `ServiceLocator` (cache global por path).

### 2.3 `ecs/`
La capa de juego propiamente dicha.

#### Componentes (data-only)

| Componente              | Atributos clave                                          |
|-------------------------|----------------------------------------------------------|
| `CTransform`            | `position: Vector2`                                      |
| `CVelocity`             | `velocity: Vector2`                                      |
| `CSurface`              | `area: Rect`, `surface: Surface`, `color: Color`         |
| `CAnimation`            | dict de animaciones, frame actual, framerate             |
| `CInputCommand`         | `name: str`, `phase: CommandPhase`, `key`/`button`       |
| `CPlayerState`          | `state: PlayerState (IDLE / MOVE / DEAD)`                |
| `CLanderState`          | `state: LanderState (PATROL / DESCEND / CAPTURE / ABDUCT / DEAD)`, refs |
| `CMutantState`          | `state: MutantState (CHASE / FIRE)`                      |
| `CAstronautState`       | `state: AstronautState (IDLE / WALKING / CAPTURED / FALLING / RESCUED)` |
| `CWraparound`           | flag para wrap horizontal (todos) y vertical (enemigos)  |
| `CParallax`             | `factor: float` (0.0–1.0 según capa)                     |
| `CPlanet`               | lista de segmentos `[(x1,y1),(x2,y2)]` generada aleatoria |
| `CStarfield`            | densidad, paleta, capa parallax                          |
| `CLifetime`             | `time_left: float`                                       |
| `CScore`                | `value: int`                                             |
| `CLives` *(bonus)*      | `count: int`, `extra_threshold: int`                     |
| `CMinimap` *(bonus)*    | `world_size`, `viewport`, escala                         |
| `CSmartBomb` *(bonus)*  | `count: int`                                             |
| `CCamera` *(bonus)*     | `offset: Vector2`, `target_dir`                          |

**Tags** (clases vacías, marcadores): `CTagPlayer`, `CTagLander`,
`CTagMutant`, `CTagAstronaut`, `CTagBulletPlayer`, `CTagBulletEnemy`,
`CTagPlanet`, `CTagStar`, `CTagExplosion`, `CTagHUD`.

#### Sistemas (orden de ejecución por frame, dentro de `PlayScene.update`)

```
 1. system_player_input          (eventos pygame > CInputCommand > callback)
 2. system_enemy_spawner         (timeline de level_*.json)
 3. system_enemy_fire            (Landers/Mutants disparan ocasionalmente)
 4. system_lander_state          (PATROL>DESCEND>CAPTURE>ABDUCT>MUTATE)
 5. system_mutant_state          (chase + fire)
 6. system_astronaut_state       (IDLE<->WALKING; FALLING con gravedad)
 7. system_player_state          (IDLE/MOVE/DEAD)
 8. system_movement              (transform += velocity * dt)
 9. system_wraparound            (X mundo / Y enemigos)
10. system_parallax              (offset visual fondo)
11. system_screen_player_bounds  (clamp vertical del jugador)
12. system_collision_bullet_enemy
13. system_collision_player_bullet     (enemigo>jugador)
14. system_collision_bullet_astronaut  (jugador puede matar astronauta)
15. system_collision_bullet_bullet     (player vs enemy bullets)
16. system_capture_astronaut     (Lander engancha)
17. system_rescue_astronaut      (player recoge / deposita)
18. system_explosion             (vida limitada de explosiones)
19. system_particle_explosion    (partículas con CLifetime)
20. system_animation             (avance de frames)
21. system_score                 (aplica deltas de puntuación)
22. system_camera         (bonus, scroll direccional)
23. system_minimap        (bonus, posiciones relativas)
24. system_smart_bomb     (bonus)
25. world._clear_dead_entities()
```

**Render** (en `draw`):
```
1. system_rendering        (background, planet, stars, sprites)
2. system_minimap_render   (bonus)
3. system_hud_rendering    (score, lives, arrow rapto, paused text)
```

---

## 3. Flujo de eventos clave

### 3.1 Disparo del jugador
```
KEYDOWN(SPACE) > system_player_input
   > CInputCommand("PLAYER_FIRE", START)
   > GameEngine._do_action > prefab_creator.create_bullet_player(...)
   > entity con (CTransform, CVelocity, CSurface, CTagBulletPlayer, CLifetime)
```

### 3.2 Captura de astronauta (Lander)
```
system_lander_state (PATROL):
   detecta astronauta cercano > state = DESCEND
system_lander_state (DESCEND):
   se mueve hacia astronauta > al colisionar > state = CAPTURE
system_capture_astronaut:
   astronauta.state = CAPTURED, parent = lander_id
   sounds_service.play("capture.ogg")
system_lander_state (ABDUCT):
   sube hacia tope; si llega arriba:
      delete astronauta
      reemplaza Lander por Mutant (prefab_creator.create_mutant)
```

### 3.3 Cambio de escena
```
PlayScene detecta GameOver >
   ServiceLocator.scenes_service.switch_to("GAME_OVER", payload={"score":N})
SceneManager: scene_actual.on_exit(); scene_nueva.on_enter(payload)
```

---

## 4. Datos de configuración (resumen)

| Archivo                | Contenido                                                 |
|------------------------|-----------------------------------------------------------|
| `window.json`          | size 320×256, framerate, bg_color, título                 |
| `interface.json`       | textos del HUD, fuente, posiciones, colores, pausa        |
| `player.json`          | velocidad, inercia, fricción, animaciones, sonidos        |
| `lander.json`          | velocidades por estado, distancias, sonido, animaciones   |
| `mutant.json`          | velocidad de persecución, agresividad de disparo          |
| `astronaut.json`       | velocidad de caminado, gravedad, daño por caída           |
| `bullets.json`         | player_bullet, enemy_bullet, missile (vel, sprite, sonido)|
| `world.json`           | estrellas (colores, parpadeo, parallax) + planeta (puntos del terreno, parallax) — **ya provisto** |
| `level_01.json`        | timeline de spawns, conteo de astronautas, fanfare path   |
| `lives.json` *(bonus)* | vidas iniciales, umbral de bonificación                   |
| `scores.json` *(bonus)*| high score por defecto (21270)                            |

Carga centralizada en `GameEngine._create()` o en `Scene.on_enter()`.

---

## 5. Tabla de cumplimiento de requerimientos

| Requisito (rúbrica)                                    | Sistema/Componente                                   |
|--------------------------------------------------------|------------------------------------------------------|
| Menú principal                                         | `MenuScene`                                          |
| Estrellas animadas                                     | `CStarfield` + `s_parallax` + `s_animation`          |
| Planeta aleatorio                                      | `CPlanet` (genera en `prefab_creator.create_planet`) |
| Movimiento + disparo player                            | `s_player_input`, `s_movement`, `prefab_creator`     |
| Inercia                                                | `CVelocity` + `s_movement` + fricción en `s_player_state` |
| Wraparound horizontal mundo / vertical enemigos        | `s_wraparound`                                       |
| Lander                                                 | `CLanderState` + `s_lander_state`                    |
| Captura + Mutant                                       | `s_capture_astronaut` + `prefab_creator.create_mutant`|
| Astronautas en suelo                                   | `CAstronautState` + `s_astronaut_state`              |
| Disparo enemigo                                        | `s_enemy_fire`                                       |
| Colisiones (4 tipos)                                   | 4 sistemas `s_collision_*`                           |
| Pausa                                                  | flag en `PlayScene`, oculta sprites con tag         |
| Fanfare al iniciar nivel                               | `PlayScene.on_enter` > `sounds_service.play()`       |
| Score                                                  | `CScore` + `s_score` + `s_hud_rendering`             |
| Contador enemigos + flecha rapto                       | HUD render lee mundo                                 |
| Explosiones partículas                                 | `s_particle_explosion`                               |
| GAME OVER / reinicio                                   | `GameOverScene`                                      |
| WIN                                                    | `WinScene`                                           |
| Publicación itch.io                                    | build con `pygbag`                                   |
| **(Bonus) Minimapa**                                   | `CMinimap` + `s_minimap_render`                      |
| **(Bonus) Vidas**                                      | `CLives` + lógica en `GameOverScene` y `s_score`     |

---

## 6. Decisiones que se documentarán post-implementación

A llenar en `docs/07-postmortem-grupal.md`:
- ¿Funcionó bien el `SceneManager` independiente del `GameEngine`?
- ¿Tener configs separadas por entidad ayudó al trabajo paralelo?
- ¿La granularidad de los sistemas de colisión fue adecuada?
- ¿El patrón State por entidad fue suficiente o hizo falta jerarquía?
