# Guía de Desarrollo — Clon de Defender (G13)

Documento de referencia para mantener coherencia con los patrones
aprendidos durante el curso (ECS, State, Service Locator, Command, Prefab)
a lo largo del proyecto. Si hay duda sobre estructura, naming o patrón,
**consultar este documento primero**.

---

## 1. Stack tecnológico

| Librería        | Versión              | Uso                                  |
|-----------------|----------------------|--------------------------------------|
| Python          | 3.12                 | Runtime                              |
| `pygame-ce`     | última estable       | Render, audio, input                 |
| `esper`         | `==2.5`              | ECS                                  |
| `pygbag`        | última               | Build a WebAssembly para itch.io     |
| `pyinstaller`   | última               | Build ejecutable Windows/Linux       |

---

## 2. Resolución y configuración base

- **Tamaño de ventana**: `320 × 256` (resolución original de Defender).
- **Framerate objetivo**: 60 FPS.
- Definidos en `assets/cfg/window.json`.

---

## 3. Patrones obligatorios

### 3.1 ECS (Entity-Component-System) con `esper`
- Toda lógica de juego se modela como **Entidades** (ID), **Componentes**
  (datos) y **Sistemas** (funciones).
- **Las entidades NO tienen comportamiento.** Los componentes son data-only.
- **Los sistemas son funciones libres**, no clases. Reciben `world: esper.World`
  más los datos que necesiten.

### 3.2 Command (input)
- El input se desacopla de la acción mediante `CInputCommand` y un enum
  `CommandPhase { START, END }`.
- `s_player_input.py` traduce eventos `pygame` > `CInputCommand` y delega la
  acción al callback `_do_action` del `GameEngine`/escena.
- Esto permite re-mapeo de teclas y soporte futuro de gamepad.

### 3.3 State (a nivel de entidad)
- Cada entidad con estados propios tiene:
  - Un componente `c_<entidad>_state.py` que contiene un `Enum` con los
    estados y los datos persistentes del state machine.
  - Un sistema `s_<entidad>_state.py` que aplica la transición y la lógica
    de cada estado en funciones privadas `_do_<estado>(...)`.
- Ejemplos planificados: `CPlayerState`, `CLanderState`, `CMutantState`,
  `CAstronautState`.

### 3.4 State (a nivel de escena)
- `SceneManager` mantiene la sucesión de escenas. Cada escena
  (`MenuScene`, `PlayScene`, `GameOverScene`, `WinScene`) implementa la
  interfaz base `Scene` (`on_enter`, `on_exit`, `process_events`, `update`,
  `draw`).
- **Cada escena posee su propio `esper.World`** para evitar contaminación de
  entidades entre pantallas.
- Acceso global vía `ServiceLocator.scenes_service.switch_to("PLAY")`.

### 3.5 Service Locator
- Clase única `ServiceLocator` con miembros estáticos:
  - `images_service` — cache de `pygame.Surface`.
  - `sounds_service` — cache y reproducción de `pygame.mixer.Sound`.
  - `fonts_service` — cache de `pygame.font.Font` por `(path, size)`.
  - `scenes_service` — cambio de escena.
- **Ningún sistema/componente carga assets directamente**, siempre vía el
  service correspondiente.

### 3.6 Prefab Creator
- `src/create/prefab_creator.py` concentra la creación de entidades complejas:
  `create_player`, `create_lander`, `create_mutant`, `create_astronaut`,
  `create_planet`, `create_starfield`, `create_bullet_player`,
  `create_bullet_enemy`, `create_explosion`, `create_hud_text`, etc.
- Recibe un `world: esper.World`, un dict de configuración cargado y datos
  posicionales. Retorna el `entity_id`.

---

## 4. Convenciones de nombrado

| Elemento                       | Prefijo / convención        | Ejemplo                       |
|--------------------------------|-----------------------------|-------------------------------|
| Archivo de componente          | `c_*.py`                    | `c_velocity.py`               |
| Clase de componente            | `C<Nombre>`                 | `CVelocity`                   |
| Archivo de tag                 | `c_tag_*.py`                | `c_tag_player.py`             |
| Clase de tag                   | `CTag<Nombre>`              | `CTagPlayer`                  |
| Archivo de sistema             | `s_*.py`                    | `s_movement.py`               |
| Función de sistema             | `system_*`                  | `system_movement`             |
| Archivo de escena              | `<nombre>_scene.py`         | `play_scene.py`               |
| Clase de escena                | `<Nombre>Scene`             | `PlayScene`                   |
| Archivo de servicio            | `<nombre>_service.py`       | `sounds_service.py`           |
| Clase de servicio              | `<Nombre>Service`           | `SoundsService`               |
| Función de prefab              | `create_*`                  | `create_lander`               |
| Función loader de config       | `load_<algo>_config`        | `load_player_config`          |
| Configuración JSON             | `<algo>.json`               | `lander.json`                 |

- **Snake case** para archivos, módulos, variables y funciones.
- **PascalCase** para clases.
- **SCREAMING_SNAKE_CASE** para constantes y valores de `Enum`.

---

## 5. Flujo del game loop

```
main.py
  └─ asyncio.run(GameEngine().run())
       └─ GameEngine.run()
            ├─ _create()                  # carga configs + scene inicial
            └─ while is_running:
                 ├─ _calculate_time()     # delta_time
                 ├─ _process_events()     # pygame events > escena activa
                 ├─ _update()             # escena activa: update sistemas
                 ├─ _draw()               # escena activa: draw sistemas
                 └─ await asyncio.sleep(0)  # cede a pygbag
```

**Cada escena define su orden de sistemas en `update()` y `draw()`.** El
`GameEngine` solo despacha a la escena activa.

---

## 6. Estructura de carpetas (resumen)

```
src/
├── engine/           # game_engine, scene_manager, config_loader, services/
├── scenes/           # menu, play, game_over, win
├── create/           # prefab_creator
└── ecs/
    ├── components/   # c_*.py (data-only)
    │   └── tags/     # c_tag_*.py
    └── systems/      # s_*.py (funciones libres)

assets/
├── cfg/   # JSON: window, interface, player, enemies, astronauts,
│          #       bullets, world, level_01, scores
├── img/   # PNG sprites
├── snd/   # OGG (web-friendly)
└── fnt/   # TTF
```

Ver [docs/04-estructura-archivos.md](04-estructura-archivos.md) para el árbol completo.

---

## 7. Configuración por archivos JSON

- **Una config por concepto.** No mezclar player + bullets en el mismo JSON.
- Carga mediante `ServiceLocator.config_service.get(path)` — cachéa el dict en
  memoria; no llamar dentro de loops.
- Posiciones, colores y tamaños siempre como objetos `{"x":..,"y":..}` /
  `{"r":..,"g":..,"b":..}` / `{"w":..,"h":..}`.
- El detalle completo de claves por archivo está en
  [docs/02-arquitectura.md § 4](02-arquitectura.md).

---

## 8. Reglas de ECS para este proyecto

1. **Componentes son data-only.** Métodos solo getters/setters triviales o
   constructores. **No lógica de juego.**
2. **Sistemas no guardan estado.** Si necesitan estado persistente, va en un
   componente.
3. **Un sistema = una responsabilidad.** Si un sistema hace dos cosas,
   dividirlo (ej. `s_collision_bullet_enemy` != `s_collision_bullet_astronaut`).
4. **Tags marcan tipo, no contienen datos.** `CTagPlayer`, `CTagLander`, etc.
5. **Limpieza con `world._clear_dead_entities()`** al final del `_update()` de
   la escena, **una sola vez** por frame.

---

## 9. Audio y assets

- Todos los sonidos en formato **`.ogg`** (compatibilidad web con pygbag).
- Imágenes en `.png` con transparencia.
- Fuente: `PressStart2P.ttf` (incluida en los recursos del proyecto).
- Convertir cualquier `.wav` con Audacity antes de añadirlo a `assets/snd/`.

---

## 10. Despliegue

- **Web (pygbag)**:
  ```
  pygbag --build .
  # genera build/web/  >  subir a itch.io como "HTML"
  ```
- **Windows/Linux (pyinstaller)**:
  ```
  pyinstaller main.spec
  ```
- Plataforma de publicación: **itch.io**.

---

## 11. Convenciones de Git

- **Rama activa:** `main`. Features en `feat/<descripcion-corta>`, fixes
  en `fix/<descripcion-corta>`. PR siempre contra `main`.
- **No commitear** `__pycache__/`, `.venv/`, `build/`, `dist/`.

### 11.1 Conventional Commits (obligatorio)

Todos los commits del proyecto deben seguir el estándar
**[Conventional Commits 1.0](https://www.conventionalcommits.org/es/v1.0.0/)**.
Esto facilita la trazabilidad para el post-mortem y el documento de
contribuciones.

**Formato:**
```
<tipo>(<scope opcional>): <descripción imperativa corta>

[cuerpo opcional con detalle]

[footer opcional con BREAKING CHANGE / refs]
```

**Tipos permitidos:**

| Tipo       | Uso                                                              |
|------------|------------------------------------------------------------------|
| `feat`     | Nueva funcionalidad de juego o de motor                          |
| `fix`      | Corrección de bug                                                |
| `refactor` | Cambio de código sin alterar comportamiento externo              |
| `perf`     | Mejora de rendimiento                                            |
| `style`    | Formato (espacios, puntuación) — no afecta lógica                |
| `docs`     | Solo documentación (README, `docs/`, comentarios doc)            |
| `test`     | Casos de prueba (manuales documentados o automáticos)            |
| `chore`    | Tareas de soporte (deps, configs, `.gitignore`, scripts de build)|
| `build`    | Cambios al sistema de build (pygbag, pyinstaller)                |
| `ci`       | Cambios a CI (si se llega a configurar)                          |
| `assets`   | Adición/cambio de assets (img/snd/fnt/cfg)                       |

**Scopes sugeridos** (no exhaustivo): `engine`, `scene`, `ecs`, `player`,
`lander`, `mutant`, `astronaut`, `hud`, `world`, `input`, `audio`,
`docs`, `cfg`.

**Ejemplos válidos:**
```
feat(player): agrega inercia y fricción al CVelocity
feat(scene): introduce SceneManager y MenuScene base
fix(wraparound): corrige cruce de bordes con velocidad alta
refactor(ecs): separa s_collision_bullet_enemy en sistema propio
docs(arquitectura): añade tabla de orden de ejecución de sistemas
assets(cfg): agrega lander.json con velocidades por estado
test(qa): documenta casos de prueba para captura de astronauta
chore: ignora carpeta dist/ en .gitignore
```

**Reglas adicionales:**
- Descripción en **español**, modo imperativo, **minúsculas**, sin punto
  final.
- Máximo 72 caracteres en la línea de asunto.
- Si rompe compatibilidad: footer `BREAKING CHANGE: <descripción>`.
- Un commit = un cambio cohesivo. **No mezclar** `feat` + `refactor`
  grandes en el mismo commit.
- Los PR pueden agrupar varios commits convencionales; el título del PR
  también debe seguir el formato.

---

## 12. Cuándo (NO) modificar este documento

- [OK] Actualizar al introducir un patrón nuevo o cambiar una convención.
- [OK] Actualizar si se decide cambiar el stack o la resolución.
- [NO] No usarlo como bitácora de tareas o changelog (eso va en `docs/`).
- [NO] No duplicar diagramas de arquitectura aquí (van en
  [docs/02-arquitectura.md](02-arquitectura.md)).
 