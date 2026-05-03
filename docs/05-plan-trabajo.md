# Plan de Trabajo — Clon de Defender (G13)

**Duración total:** 21 días (3 semanas).
**Inicio estimado:** 2026-05-04.
**Entrega final estimada:** 2026-05-24.

---

## 1. Asignación por integrante

| Integrante                | Rol                              | Áreas principales                                           |
|---------------------------|----------------------------------|--------------------------------------------------------------|
| **Jairo Reyes**           | Lead Dev — Implementación         | `engine/`, `scenes/`, ECS (componentes y sistemas), prefabs, integración, build |
| **María Paula Estupiñán** | Diseño + QA Funcional             | Diseño de juego, configs JSON visuales/HUD, pruebas manuales, casos de prueba |
| **Daniel F. Urrego**      | Diseño de Niveles + QA Balance    | Diseño de niveles, configs de spawns, balance de dificultad, pruebas de balance |
| **Nicolás Prada**         | Diseño Arquitectónico/UX + QA     | Diagramas de arquitectura, UX de menús, mensajes, configs de interfaz, pruebas de regresión |

> **Nota requerida por la rúbrica del curso:** se exige que *todos los
> integrantes programen*. Por eso cada integrante tiene asignada al menos
> **una tarea explícita de código** en el cronograma (marcada con 🔧). El
> resto de su carga es diseño y pruebas. Los commits propios quedan
> registrados en `docs/06-plantilla-contribuciones.md`.

---

## 2. Cronograma día a día

### Semana 1 — Fundación (días 1–7)

| Día | Tarea                                                                                          | Resp.    |
|-----|------------------------------------------------------------------------------------------------|----------|
| 1   | Setup: venv, `requirements.txt`, push estructura inicial al repo                               | Jairo    |
| 1   | Documento `docs/01-propuesta.md` final (revisión y ajustes)                                    | Nicolás  |
| 1   | Documento `docs/03-diseno.md` final (mecánicas Defender, controles)                            | Daniel   |
| 1   | Documento `docs/02-arquitectura.md` (revisión, diagramas)                                      | Nicolás  |
| 2   | Implementar `engine/game_engine.py` + `main.py` con loop asyncio                               | Jairo    |
| 2   | Implementar `engine/services/*` (imágenes, sonidos, fuentes) 🔧                               | María Paula |
| 2   | `assets/cfg/window.json` + `interface.json` con valores 320×256                                | Nicolás  |
| 3   | Implementar `engine/scene_manager.py` + `scenes/scene.py` base + `scenes_service.py`           | Jairo    |
| 3   | `MenuScene` con título e instrucciones                                                         | Jairo    |
| 3   | Casos de prueba para Menu (entrada/salida, navegación)                                         | María Paula |
| 4   | Componentes base: `c_transform`, `c_velocity`, `c_surface`, `c_animation`, `c_input_command`   | Jairo    |
| 4   | Tags básicos: `c_tag_player`, `c_tag_hud`, `c_tag_bullet_player`, `c_tag_bullet_enemy` 🔧    | Daniel   |
| 5   | Sistemas: `s_movement`, `s_rendering`, `s_animation`, `s_player_input` (Command)               | Jairo    |
| 5   | `assets/cfg/player.json` (velocidad, inercia, sprites)                                         | Daniel   |
| 5   | Documento de casos de prueba de jugador                                                         | María Paula |
| 6   | Player en `PlayScene` con inercia + disparo de prueba                                          | Jairo    |
| 6   | Diseño visual del HUD (posiciones, colores, fuentes en `interface.json`)                       | Nicolás  |
| 7   | `c_starfield`, `c_parallax`, `s_parallax`, `prefab_creator.create_starfield`                   | Jairo    |
| 7   | Revisar y ajustar `assets/cfg/world.json` (densidad de estrellas, parallax, paleta) — ya provisto | Daniel   |
| 7   | **[*] Hito formativo 1**: revisión grupal, push a `main`, escribir `docs/01-propuesta.md` final | Todos    |

### Semana 2 — Gameplay core (días 8–14)

| Día | Tarea                                                                                          | Resp.    |
|-----|------------------------------------------------------------------------------------------------|----------|
| 8   | `c_planet`, `prefab_creator.create_planet` (generación procedural)                             | Jairo    |
| 8   | Ajustes finos al planeta en `assets/cfg/world.json` (puntos del terreno, paleta)                | Daniel   |
| 8   | Diseño de paleta de colores final (planeta, estrellas, enemigos)                                | Nicolás  |
| 9   | `s_wraparound` horizontal (mundo + jugador) y `s_screen_player_bounds`                         | Jairo    |
| 9   | Pruebas de wraparound (entrar/salir por bordes, multi-pantalla)                                | María Paula |
| 10  | Disparo del jugador real (`prefab_creator.create_bullet_player`, atraviesa enemigos)           | Jairo    |
| 10  | `assets/cfg/bullets.json`                                                                      | Daniel   |
| 10  | `c_lander_state` + `s_lander_state` (PATROL/DESCEND)                                           | Jairo    |
| 11  | `s_lander_state` (CAPTURE/ABDUCT) + transformación a Mutant                                    | Jairo    |
| 11  | `c_astronaut_state` + `s_astronaut_state` + `prefab_creator.create_astronaut`                  | Jairo    |
| 11  | `assets/cfg/lander.json` y `astronaut.json`                                                    | Daniel   |
| 12  | `c_mutant_state` + `s_mutant_state` (chase + fire)                                             | Jairo    |
| 12  | `assets/cfg/mutant.json`                                                                        | Daniel   |
| 12  | `s_enemy_spawner` con timeline de `level_01.json`                                              | Jairo    |
| 12  | `assets/cfg/level_01.json` con olas iniciales                                                   | Daniel   |
| 13  | Sistemas de colisión (4 sistemas separados) + reglas de score                                   | Jairo    |
| 13  | Pruebas de colisión (matriz de casos: bullet vs enemy, vs astronauta, vs bullet, vs player)    | María Paula |
| 14  | `s_wraparound` vertical para enemigos + `s_capture_astronaut` + `s_rescue_astronaut`           | Jairo    |
| 14  | **[*] Hito formativo 2**: actualizar `docs/09-avance.md`, demo informal, retro                  | Todos    |

### Semana 3 — Polish + entrega (días 15–21)

| Día | Tarea                                                                                          | Resp.    |
|-----|------------------------------------------------------------------------------------------------|----------|
| 15  | HUD completo (`s_hud_rendering`): score, contador enemigos, flecha de rapto                    | Jairo    |
| 15  | Pausa con texto PAUSED parpadeante (oculta jugador/enemigos/proyectiles)                       | Jairo    |
| 15  | Pruebas de regresión sobre todo lo anterior (checklist) 🔧 — script auxiliar de smoke test    | Nicolás  |
| 16  | Explosiones de partículas (`s_particle_explosion`, `c_lifetime`, `prefab_creator.create_explosion`) | Jairo |
| 16  | Sonidos integrados: fanfare, laser, explosion, capture, mutate, rescue                         | Jairo    |
| 16  | Validación auditiva + ajuste de volúmenes en configs                                            | María Paula |
| 17  | `GameOverScene` + `WinScene` + reinicio de partida                                             | Jairo    |
| 17  | `assets/cfg/lives.json` + `c_lives` + lógica de vidas (bonus priorizado)                       | Jairo    |
| 17  | UX de Game Over y Win (textos, parpadeo, instrucciones de reinicio)                             | Nicolás  |
| 18  | Bono priorizado: **Minimapa** (`c_minimap`, `s_minimap`)                                       | Jairo    |
| 18  | Diseño visual del minimapa (proporciones, colores)                                              | Nicolás  |
| 18  | Bonos opcionales si hay tiempo (smart bomb / cámara / high score)                               | Jairo    |
| 19  | Testing integral end-to-end (jugar hasta ganar, hasta perder, casos límite)                     | María Paula |
| 19  | Pruebas de balance — afinar velocidades, frecuencias, dificultad                                | Daniel   |
| 19  | Pulido de código, refactors menores, comentarios donde aplique                                  | Jairo    |
| 20  | Build pygbag > publicar en itch.io con descripción + screenshot                                 | Jairo    |
| 20  | Build pyinstaller (Linux/Windows) como respaldo 🔧                                             | Daniel   |
| 20  | Crear página itch.io: descripción, controles, créditos, screenshot                              | Nicolás  |
| 21  | `docs/07-postmortem-grupal.md` final                                                            | Todos    |
| 21  | Post-mortem individual (cada uno escribe el suyo)                                               | Todos    |
| 21  | Grabación de video presentación (arquitectura, ECS, roles)                                      | Todos    |
| 21  | **[!] Hito final**: tag `v1.0.0`, push final, entrega                                            | Todos    |

---

## 3. Dependencias entre tareas (críticas)

```
GameEngine + SceneManager (día 2-3)
    v
Componentes base + Prefab + Sistemas básicos (día 4-5)
    v
Player jugable (día 6)
    v
Mundo (estrellas + planeta + parallax + wraparound) (día 7-9)
    v
Disparo + Enemigos + Astronauta + Captura/Mutación (día 10-12)
    v
Colisiones (día 13)
    v
HUD + Pausa + Score (día 15)
    v
Pulido + Bonos (día 16-18)
    v
Build + Publicación (día 20)
    v
Post-mortems + Video (día 21)
```

Bloqueantes:
- Sin `SceneManager` no se puede tener Menu/Play/GameOver > **prioridad día 3**.
- Sin componentes base ni `s_movement` > nada se mueve > **prioridad día 4-5**.
- Sin wraparound > no se puede testear el mundo > **prioridad día 9**.

---

## 4. Reglas de trabajo en equipo

- **Una rama por feature:** `feat/<descripcion-corta>`. PR a `main`.
- **Conventional Commits 1.0 obligatorio** para todos los commits del
  repositorio. Formato `tipo(scope): descripción`. Tipos permitidos,
  scopes sugeridos y ejemplos en
  [docs/guia-desarrollo.md sec.11.1](guia-desarrollo.md#111-conventional-commits-obligatorio).
  Esto se usará luego para reconstruir el aporte de cada integrante en
  el post-mortem grupal y los post-mortems individuales.
- **Commits diarios** mínimo cuando se trabaje (aunque sea WIP).
- **Bitácora de contribución** (`docs/06-plantilla-contribuciones.md`) actualizada
  por cada miembro al menos cada 2 días.
- **Stand-up asíncrono** vía Slack/WhatsApp cada 2-3 días: qué hice, qué sigue,
  qué bloqueo tengo.
- **Code review:** Jairo revisa PRs de configs/scripts; al menos 1 revisor antes
  de mergear a `main`.
- **Pruebas antes de merge:** correr el juego localmente y validar que no se
  rompió lo que ya funcionaba.

---

## 5. Riesgos y mitigaciones

| Riesgo                                              | Mitigación                                                |
|-----------------------------------------------------|-----------------------------------------------------------|
| El procedural del planeta consume mucho tiempo      | Empezar con generación simple (ruido lineal); refinar después |
| Wraparound + colisiones dan problemas en bordes     | Aislar lógica de wrap en `s_wraparound`, tests específicos  |
| pygbag falla en build web por dependencias          | Probar build temprano (día 7) con un mínimo                |
| Bonos consumen tiempo del core                      | **Bonos solo después del día 17** y solo si hay holgura    |
| Algún integrante no puede contribuir una semana     | Re-balancear: Jairo absorbe; resto cubre QA y docs         |
