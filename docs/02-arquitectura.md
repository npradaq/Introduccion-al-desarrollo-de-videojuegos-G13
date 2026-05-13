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

| Escena              | Propósito                                                       |
|---------------------|-----------------------------------------------------------------|
| `MenuScene`         | Título, instrucciones, "Presiona ENTER para jugar".             |
| `PlayScene`         | Gameplay: world, sistemas, HUD.                                 |
| `GameOverScene`     | Texto GAME OVER, vuelve a `MenuScene` o reinicia.               |
| `WinScene`          | Pantalla de victoria al terminar el nivel.                      |
| `AttractionScene`   | *(bonus)* El juego se "juega solo" como demo; funciona de forma completamente distinta a `PlayScene`. Confirmada por el profesor como escena independiente propia. |

Cada escena instancia su propio `esper.World`. Los recursos (sprites,
sonidos) **se comparten** vía `ServiceLocator` (cache global por path).

### 2.3 `ecs/`
La capa de juego propiamente dicha.

#### Componentes (data-only)

| Componente              | Atributos clave                                                                                           | Estado       |
|-------------------------|-----------------------------------------------------------------------------------------------------------|--------------|
| `CTransform`            | `position: Vector2`                                                                                       | ✅ impl.     |
| `CVelocity`             | `velocity: Vector2`                                                                                       | ✅ impl.     |
| `CSurface`              | `area: Rect`, `surface: Surface`, `color: Color`, `visible: bool`                                        | ✅ impl.     |
| `CAnimation`            | dict de animaciones, `current_frame`, `current_animation`, `paused: bool`                                | ✅ impl.     |
| `CInputCommand`         | `name: str`, `phase: CommandPhase`, `key`                                                                 | ✅ impl.     |
| `CPlayerState`          | `state: PlayerState (IDLE / MOVE)`                                                                        | ✅ impl.     |
| `CLanderState`          | `phase: LanderPhase (PATROL / DESCEND / ABDUCT)`, `target_astronaut_id`, `initial_patrol_remaining`      | ✅ impl.     |
| `CAstronautState`       | `phase: AstronautPhase (FALLING / LANDED / CAPTURED / RESCUED)`, `land_y: float`                        | ✅ impl.     |
| `CAttachTo`             | `parent_id: int`, `offset: Vector2` — ancla una entidad a otra (propulsor de la nave)                    | ✅ impl.     |
| `CParallax`             | `factor: float` (0.0–1.0 según capa)                                                                     | ✅ impl.     |
| `CLifetime`             | `time_left: float`                                                                                        | ✅ impl.     |
| `CCanBlink`             | `blink_rate: float` — parpadeo del texto de pausa                                                        | ✅ impl.     |
| `CBurner`               | superficies idle/moving y configs de animación del propulsor                                              | ✅ impl.     |
| `CText`                 | `text`, `font_path`, `size`, `color`, `surface`, `visible`                                               | ✅ impl.     |
| `CWraparound`           | flag para wrap horizontal (todos) y vertical (enemigos)                                                   | 📋 planif.  |
| `CPlanet`               | lista de segmentos `[(x1,y1),(x2,y2)]` generada aleatoria                                                 | 📋 planif.  |
| `CSmartBomb` *(bonus)*  | `count: int`                                                                                              | 📋 bonus    |
| `CMinimap` *(bonus)*    | `world_size`, `viewport`, escala                                                                          | 📋 bonus    |

**Tags implementados** (clases vacías, marcadores):
`CTagPlayer`, `CTagLanderEnemy`, `CTagMutantEnemy`, `CTagAstronaut`,
`CTagBulletPlayer`, `CTagBurner`, `CTagStar`, `CTagHUD`, `CTagParticle`.

#### Sistemas (orden de ejecución por frame, dentro de `PlayScene.update`)

```
── Movimiento y cámara ──────────────────────────────────────────────────
 1. system_movement              transform += velocity * dt
 2. system_attach_to             sincroniza entidades hijo (propulsor) via CAttachTo
 3. system_parallax              offset visual del fondo según velocidad del jugador
 4. system_screen_player_bounds  clamp vertical + wrap horizontal del jugador

── Limpieza de balas ────────────────────────────────────────────────────
 5. system_screen_bullet         decrementa CLifetime; elimina al expirar
                                 (reutilizado por partículas de explosión)

── IA de enemigos ───────────────────────────────────────────────────────
 6. system_lander                PATROL › DESCEND › ABDUCT › transformación a mutante
                                 + mutantes persiguen al jugador

── Colisiones ───────────────────────────────────────────────────────────
 7. system_collision             balas del jugador vs landers/mutantes
                                 → elimina ambos, spawnea partículas,
                                   libera astronauta capturado si aplica

── Astronautas ──────────────────────────────────────────────────────────
 8. system_astronaut             FALLING → LANDED (anima al aterrizar)
                                 RESCUED → LANDED (anima + suma 250 pts)

── Estado y animación del jugador ───────────────────────────────────────
 9. system_player_state          IDLE / MOVE según velocidad
10. system_burner                cambia superficie del propulsor según estado
11. system_animation             avance de frames (respeta CAnimation.paused)

── Score y game over ────────────────────────────────────────────────────
12. (PlayScene) _update_camera
13. (PlayScene) _update_score_display   actualiza CText del score en HUD
14. (PlayScene) _check game_over_score  muestra texto y detiene el juego

 ▸  world._clear_dead_entities()
```

**Render** (en `draw`):
```
1. system_rendering    sprites, partículas y textos no-HUD sobre game_surface
                       (excluye entidades con CTagHUD)
2. system_hud          cabecera negra + línea divisora + score + vidas +
                       contadores ENE/AST + textos HUD (pausa, game over)
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
system_lander (PATROL):
   initial_patrol_remaining > 0  → solo patrulla, no detecta
   initial_patrol_remaining <= 0 → busca astronauta LANDED dentro de
                                    astronaut_detection_range px horizontales
   al encontrar uno > target_astronaut_id = astro_id, phase = DESCEND

system_lander (DESCEND):
   mueve el lander hacia la posición del astronauta
   condición: lander_bottom_y >= astronaut_top_y (distancia < 2 px)
      → astronauta.phase = CAPTURED, vel = 0, animation.paused = True
      → sounds_service.play(sound_capture)
      → phase = ABDUCT

system_lander (ABDUCT):
   sube verticalmente a velocity_abduct px/s
   astronauta.position = (lander.x, lander.y + lander.height)  ← sigue al lander
   si lander.y <= 0:
      sounds_service.play(sound_mutate)
      delete astronauta
      delete lander
      create_mutant_enemy(posición)

── Si el lander muere durante ABDUCT (bala del jugador) ────────────────
system_collision detecta impacto:
   astronauta.phase = RESCUED, vel.y = falling_velocity
   sounds_service.play(sound_fall)
   → el astronauta cae libremente hasta su land_y
   → al aterrizar: phase = LANDED, animation.paused = False, score += 250
```

### 3.3 Cambio de escena
```
PlayScene detecta GameOver >
   ServiceLocator.scenes_service.switch_to("GAME_OVER", payload={"score":N})
SceneManager: scene_actual.on_exit(); scene_nueva.on_enter(payload)
```

---

## 4. Datos de configuración

Todos los archivos viven en `assets/cfg/`. Se cargan en `PlayScene.on_enter()`
mediante `ServiceLocator.config_service.get(path)` (caché automática).

### `window.json`
| Clave        | Descripción                     |
|--------------|---------------------------------|
| `width`      | Ancho de la ventana (px)        |
| `height`     | Alto del área de juego (px)     |
| `framerate`  | FPS objetivo                    |
| `bg_color`   | Color de fondo `{r,g,b}`        |
| `title`      | Título de la ventana            |

### `interface.json`
| Clave                          | Descripción                                                         |
|--------------------------------|---------------------------------------------------------------------|
| `font`                         | Ruta a la fuente TTF global                                         |
| `hud.header_height`            | Alto de la cabecera HUD en px                                       |
| `hud.header_line_color`        | Color de la línea divisora `{r,g,b}`                                |
| `hud.score_label`              | Config del texto "SCORE": `text`, `size`, `position`, `color`       |
| `hud.score_value`              | Config del valor numérico del score (mismo esquema)                 |
| `hud.lives`                    | `image`, `count`, `x`, `y`, `spacing` — iconos de vidas            |
| `hud.enemies_count`            | `label`, `size`, `x`, `y`, `color` — contador de enemigos          |
| `hud.astronauts_count`         | `label`, `size`, `x`, `y`, `color` — contador de astronautas       |
| `pause.text/size/color/blink_rate` | Texto de pausa centrado con parpadeo                           |
| `game_over.text/size/color`    | Texto de game over centrado (se muestra al alcanzar el límite)      |

### `player.json`
| Clave                   | Descripción                                                  |
|-------------------------|--------------------------------------------------------------|
| `image`                 | Ruta al sprite del jugador                                   |
| `input_velocity`        | Velocidad al presionar flecha (px/s)                         |
| `max_velocity`          | Velocidad máxima permitida (px/s)                            |
| `burner_idle_image`     | Sprite del propulsor en reposo                               |
| `burner_moving_image`   | Sprite del propulsor en movimiento                           |
| `burner_offset`         | Offset `{x,y}` del propulsor respecto al jugador             |
| `burner_animations`     | Config de animación idle del propulsor                       |
| `burner_moving_animations` | Config de animación moving del propulsor                  |

### `bullets.json`
| Clave                       | Descripción                                              |
|-----------------------------|----------------------------------------------------------|
| `player_bullet.color`       | Color `{r,g,b}` de la bala del jugador                   |
| `player_bullet.size`        | Dimensiones `{w,h}` en px                                |
| `player_bullet.velocity`    | Velocidad horizontal (px/s)                              |
| `player_bullet.lifetime`    | Segundos antes de desaparecer                            |
| `player_bullet.sound`       | Ruta al sonido de disparo                                |

### `enemies.json`
| Clave                               | Descripción                                                         |
|-------------------------------------|---------------------------------------------------------------------|
| `explosion.particle_speed`          | Velocidad de cada partícula de explosión (px/s)                     |
| `explosion.max_distance`            | Distancia máxima que viaja cada partícula (px) — determina lifetime |
| `explosion.color`                   | Color `{r,g,b}` de las partículas                                   |
| `Lander.image`                      | Sprite del lander                                                   |
| `Lander.sound_die`                  | Sonido al morir                                                     |
| `Lander.sound_capture`              | Sonido al capturar un astronauta                                     |
| `Lander.sound_mutate`               | Sonido al transformarse en mutante                                  |
| `Lander.animations`                 | Config de animación (`number_frames`, lista con name/start/end/framerate) |
| `Lander.velocity_patrol`            | Velocidad durante patrullaje (px/s)                                 |
| `Lander.velocity_descend`           | Velocidad al descender hacia el astronauta (px/s)                   |
| `Lander.velocity_abduct`            | Velocidad de ascenso con astronauta capturado (px/s)                |
| `Lander.astronaut_detection_range`  | Distancia horizontal máxima para detectar astronautas (px)          |
| `Lander.initial_patrol_min`         | Mínimo de segundos de patrullaje obligatorio al crear el lander     |
| `Lander.initial_patrol_max`         | Máximo de segundos de patrullaje obligatorio al crear el lander     |
| `Lander.max_concurrent`             | Máximo de landers vivos al mismo tiempo                             |
| `Lander.max_total`                  | Máximo de landers que pueden spawnearse en la partida               |
| `Lander.spawn_interval`             | Segundos entre spawns de landers                                    |
| `Mutant.image`                      | Sprite del mutante                                                  |
| `Mutant.sound_die`                  | Sonido al morir                                                     |
| `Mutant.animations`                 | Config de animación                                                 |
| `Mutant.velocity_chase`             | Velocidad de persecución al jugador (px/s)                          |

> Los mutantes **no se crean por spawn directo**. Solo aparecen cuando un
> lander llega al límite superior de la pantalla tras capturar un astronauta.

### `astronauts.json`
| Clave                    | Descripción                                                          |
|--------------------------|----------------------------------------------------------------------|
| `Astronaut.image`        | Sprite (spritesheet horizontal)                                      |
| `Astronaut.sound_rescued`| Sonido al aterrizar tras ser rescatado                               |
| `Astronaut.sound_fall`   | Sonido cuando el astronauta empieza a caer tras matar al lander      |
| `Astronaut.animations`   | Config de animación (`number_frames`, `list` con name/start/end/framerate) |
| `Astronaut.falling_velocity` | Velocidad de caída cuando es liberado de un lander (px/s)        |
| `Astronaut.levels`       | Array de ratios de altura (0.0–1.0) donde aparecen los astronautas. Se definen tres niveles; cada astronauta se asigna aleatoriamente a uno. Ejemplo: `[0.70, 0.80, 0.90]` |

> Los astronautas aparecen **directamente en su nivel** (estado `LANDED`,
> animación activa). La velocidad `falling_velocity` solo se usa cuando
> son liberados de un lander en plena abducción.

### `scores.json`
| Clave                          | Descripción                                                |
|--------------------------------|------------------------------------------------------------|
| `points_per_enemy`             | Puntos por eliminar un lander o mutante                    |
| `points_per_rescued_astronaut` | Puntos al aterrizar un astronauta rescatado                |
| `game_over_score`              | Puntuación a la que se activa el Game Over                 |

### `world.json`
| Clave                    | Descripción                                       |
|--------------------------|---------------------------------------------------|
| `stars_number`           | Número de estrellas de fondo                      |
| `star_colors`            | Array de colores `{r,g,b}` para las estrellas     |
| `stars_parallax_factor`  | Factor de parallax de las estrellas               |
| `world_repeats`          | Veces que se repite el ancho base del mundo       |

### `level_01.json`
| Clave                      | Descripción                                                  |
|----------------------------|--------------------------------------------------------------|
| `player_spawn.position`    | Posición inicial del jugador `{x,y}`                         |
| `world.width`              | Ancho base del mundo (px); se multiplica por `world_repeats` |
| `astronauts_count`         | Total de astronautas que aparecen en el nivel                |
| `astronaut_spawn_duration` | Ventana de tiempo (s) en la que se reparten los spawns       |
| `enemy_start_delay`        | Segundos desde el inicio hasta que empiezan a spawnearse landers |
| `fanfare_sound`            | Ruta al sonido de arranque del nivel                         |

Carga centralizada en `Scene.on_enter()` mediante `ConfigService` (caché por path).

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
| Captura + Mutant                                       | `s_capture_astronaut` + `prefab_creator.create_mutant` + `CAttachTo`|
| Astronautas en suelo (movimiento orgánico)             | `CAstronautState` + `s_astronaut_state` + Perlin Noise|
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
| **(Bonus) Modo atracción**                             | `AttractionScene` (escena propia, no variante de `PlayScene`) |

---

## 6. Decisiones que se documentarán post-implementación

A llenar en `docs/07-postmortem-grupal.md`:
- ¿Funcionó bien el `SceneManager` independiente del `GameEngine`?
- ¿Tener configs separadas por entidad ayudó al trabajo paralelo?
- ¿La granularidad de los sistemas de colisión fue adecuada?
- ¿El patrón State por entidad fue suficiente o hizo falta jerarquía?
