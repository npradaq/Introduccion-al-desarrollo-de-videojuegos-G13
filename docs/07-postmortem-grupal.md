# Post-Mortem Grupal — Clon de Defender (G13)

> **Pendiente de llenar al final del proyecto.** Este documento es el
> entregable del post-mortem grupal (rúbrica: 10% de la nota final). Debe
> responder con **claridad**, **precisión** y **profundidad** las preguntas
> de la rúbrica para lograr el "Excelente".

---

## 1. Resumen del proceso (semana a semana)

> *Describir cómo evolucionó el proyecto.*

**Semana 1 — Fundación (Setup + ECS + Terreno)**
- Logros:
  - Establecimiento de la arquitectura base (GameEngine, SceneManager, ServiceLocator)
  - Implementación del patrón ECS con esper
  - Creación del terreno procedural con Perlin Noise (5 pantallas cíclicas)
  - Setup de la estructura de componentes (CTransform, CVelocity, CSurface, etc.)
  - Implementación del sistema de parallax para estrellas
  - Base de MenuScene y PlayScene
  
- Bloqueos:
  - Decidir sobre la granularidad de componentes vs la complejidad del sistema
  - Entender cómo integrar Perlin Noise para un terreno orgánico sin hardcoding
  
- Cambios respecto al plan inicial:
  - Se optó por una arquitectura ECS más modular de lo esperado para facilitar el trabajo paralelo

**Semana 2 — Gameplay core (Enemigos + Astronautas + Colisiones)**
- Logros:
  - Sistema completo de Lander (patrol → descend → abduct → mutate)
  - Comportamiento de Mutant (persecución agresiva del jugador)
  - Sistema de astronautas (spawn, walking, capture, falling, rescue)
  - Cuatro sistemas de colisión (bala vs enemigo, bala vs player, bala vs astronauta, bala vs bala)
  - Sistema de disparo del jugador (laser que atraviesa pantalla)
  - Disparo enemigo (frecuencia variable, búsqueda débil)
  - Sistema de explosion particles con lifetime
  - Wrap-around horizontal para mundo + enemigos, clamp vertical para player
  - Wave spawn system y Baiter AI (bonus enemigos)
  
- Bloqueos:
  - Complejidad de la lógica de estados de Lander (5 fases diferentes)
  - Sinc​ronización entre movimiento de cámara y wrap-around
  - Manejo de la captura y rescate de astronautas con CAttachTo
  
- Cambios respecto al plan inicial:
  - Se agregaron enemigos bonus (Baiter) además del Lander y Mutant planificados
  - Sistema de spawn de olas fue más complejo de lo estimado

**Semana 3 — Polish y entrega (HUD + Minimapa + Game Over + Bonuses)**
- Logros:
  - Sistema HUD completo (SCORE, vidas, contador de enemigos, contador de astronautas)
  - Implementación del minimap bonus (terreno suavizado, entity markers, viewport bracket)
  - Game Over screen con detección por vidas o límite de score
  - Sistema de vidas con reinicio de nivel
  - Cámara con scroll direccional (bonus)
  - Smart bomb system (bonus)
  - Organización final del HUD en 32px con minimapa centrado
  - Todos los sonidos y efectos visuales integrados
  
- Bloqueos:
  - Fitting del minimapa, vidas, y contadores en un HUD de 32px
  - Suavizado del terreno en el minimapa sin perder detalle
  
- Cambios respecto al plan inicial:
  - El minimapa fue más robusto de lo esperado (interpolación lineal, smooth terrain)
  - Game Over por score se agregó además de por vidas
  - Smart bomb está funcional pero sin persistencia de contador visual completa

---

## 2. Análisis arquitectónico

### 2.1 Organización de clases, componentes y sistemas

> *Estructura final del proyecto.*

- **Capa engine:** (`src/engine/`)
  - `game_engine.py` — loop principal, control de delta_time, gestión de eventos de pygame
  - `scene_manager.py` — switch_to, push, pop de escenas
  - `service_locator.py` — acceso centralizado a servicios (imágenes, sonidos, fuentes, escenas)
  - `perlin.py` — Perlin Noise 1D para terreno procedural
  - `services/` — cuatro servicios (images, sounds, fonts, scenes) con caché automático

- **Capa scenes:** (`src/scenes/`)
  - `MenuScene` — menú principal con logo, instrucciones, "PRESS ENTER TO START"
  - `PlayScene` — gameplay completo, instancia su propio `esper.World`, maneja spawning, update y render
  - Nota: GameOverScene y WinScene fueron movidas a PlayScene (interno) para simplificar, no como escenas separadas

- **ECS (16 componentes, 16 sistemas):**
  - **Componentes:** CTransform, CVelocity, CSurface, CAnimation, CPlayerState, CLanderState, CAstronautState, CAttachTo, CParallax, CLifetime, CCanBlink, CBurner, CText, CInputCommand, y tags (CTagPlayer, CTagLanderEnemy, etc.)
  - **Sistemas:** s_movement, s_attach_to, s_parallax, s_screen_player_bounds, s_screen_bullet, s_lander, s_collision, s_astronaut, s_player_state, s_burner, s_animation, s_player_input, s_hud, s_rendering, s_terrain_rendering, s_minimap
  - Orden de ejecución: movimiento → IA enemigos → colisiones → estado → animación → render

- **Configs y assets:** (`assets/cfg/` y `assets/`)
  - 7 JSON (window, interface, player, bullets, enemies, astronauts, scores, level_01, world)
  - Carga centralizada en PlayScene.on_enter() mediante ConfigService (caché por path)
  - Reutilización de assets entre escenas vía ServiceLocator

### 2.2 Decisiones tomadas y su justificación

- **¿Por qué esper y no un ECS propio?**
  - esper es maduro, estable, y permite enfocarse en el gameplay no en infraestructura
  - Reducción de código boilerplate en componentes y sistemas
  - Facilita trabajo paralelo: cada integrante puede implementar un sistema sin conflictos de arquitectura

- **¿Por qué SceneManager separado del GameEngine?**
  - Separación de responsabilidades: GameEngine maneja timing/eventos, SceneManager maneja flujo de pantallas
  - Facilita testing y reutilización: SceneManager es independiente de pygame specifics
  - Permite stack de escenas (push/pop) sin complicar GameEngine

- **¿Por qué configs JSON una por entidad y no monolíticas?**
  - Reutilización: player.json, bullets.json, enemies.json pueden evolucionar sin tocar level_01.json
  - Facilita iterar: artist puede ajustar colores en interface.json sin tocar gameplay
  - Simplifica debugging: cada subsistema ve su propia config, no una super-config
  - Permite trabajo paralelo: un integrante en gameplay, otro ajustando UI, sin merge conflicts

- **¿Por qué cuatro sistemas de colisión separados?**
  - Cada tipo de colisión tiene lógica muy distinta (destruir vs rebote vs rescate vs anulación)
  - Simplifica mantenimiento: cambio en colisión bala vs enemigo no afecta bala vs astronauta
  - Permite debug granular: cada sistema puede loggear lo que hace sin ruido
  - Rendimiento: cada sistema solo itera entidades relevantes

- **¿Por qué el patrón State a dos niveles (escena y entidad)?**
  - Level 1 (escena): MenuScene, PlayScene maneja flujo global del juego
  - Level 2 (entidad): CLanderState, CAstronautState maneja comportamiento local
  - Permite que el mismo entity pueda tener múltiples estados (ej: un Lander puede estar en PATROL o ABDUCT sin cambiar de escena)
  - Separación clara: cambios en estado de Lander no requieren rewrite de PlayScene

---

## 3. Análisis de patrones usados

### 3.1 ECS — opinión grupal

**¿Qué tan bien funcionó ECS para este juego?**

ECS fue **excelente** para un arcade 2D con múltiples tipos de entidades (Landers, Mutants, Astronauts, projectiles, particles).

- **Ventajas observadas:**
  - Composición sobre herencia: no necesitamos jerarquía de clases compleja. Un Lander es simplemente entidad + CLanderState + CTransform, un Mutant reutiliza CLanderState con parámetros diferentes.
  - Paralelismo simple: cada sistema es independiente, facilita que 4 integrantes trabajen simultáneamente sin merge conflicts.
  - Data-driven: cambiar comportamiento de Lander es ajustar valores en enemies.json, no recompilar código.
  - Escalable: agregar un nuevo tipo de enemigo (Baiter, Swarmer, etc.) es trivial: crear un tag, crear un sistema para su IA, listo.
  - Debugging: "¿por qué este Lander no se mueve?" → revisar s_lander.py, revisar CLanderState, revisar enemies.json. Muy localizado.
  - Performance: s_movement solo itera sobre entidades con CVelocity, no iterar todas.

- **Desventajas observadas:**
  - Curva de aprendizaje inicial: entender cómo ECS modela comportamiento toma tiempo si vienes de OOP tradicional.
  - Queries verbosas: `world.get_components(CTransform, CTagLanderEnemy)` es más largo que `landers.forEach(...)` en OOP.
  - Debugging distribuido: un bug puede estar en s_movement, s_attach_to, o CLanderState. Requiere "buscar en tres sitios".
  - Estado compartido: algunos estados (ej: player_entity global en PlayScene) siguen siendo no-ECS por conveniencia.

- **Lecciones para próximos proyectos:**
  - ECS brilla en juegos con muchas entidades heterogéneas. Para un juego más lineal/cinemático, OOP podría ser más simple.
  - La composición de componentes es poderosa, pero requiere disciplina: no agregar un "MegaComponent" que hace todo.
  - Orden de sistemas importa. Documentar el orden de ejecución en una tabla ayuda mucho.

### 3.2 Otros patrones aplicados

- **Command (input):** 
  - `CInputCommand` con fase START/END facilita cambios dinámicos (ej: rebindear teclas, soporte para múltiples input methods)
  - Se sintió minimal, no overhead. Pasar un struct pequeño vs directamente modificar velocidad es casi lo mismo.
  - Permitió agregar lógica de pausa sin tocar cada sistema.

- **State (entidad):** 
  - CLanderState con fases (PATROL/DESCEND/ABDUCT) fue clara al inicio.
  - A mitad de proyecto, tuvimos que agregar flags adicionales (ej: initial_patrol_remaining) dentro del state.
  - **Lección:** State pattern puro (enum solamente) no escala. Híbrido de enum + data fue mejor.

- **State (escena):** 
  - MenuScene → PlayScene → GameOver (interno) fue fluido.
  - No necesitamos más escenas gracias a que PlayScene es flexible (detecta game_over internamente).
  - SceneManager sin complejidades (push/pop) fue suficiente.

- **Service Locator:** 
  - Ventaja: `ServiceLocator.images_service.get(path)` es cómodo, sin pasar servicios a 10 niveles de profundidad.
  - Desventaja: es estado global implícito. Si un sistema modifica ServiceLocator.config_service, afecta todo.
  - **Lección:** Para un juego pequeño, está bien. Para proyectos grandes, inyección de dependencias es mejor.

- **Prefab:** 
  - `prefab_creator.py` con funciones `create_player()`, `create_lander()`, etc. fue muy limpio.
  - Cada función es responsable de armar la entidad con sus componentes necesarios.
  - No se infló: cada prefab es 5-15 líneas, fácil de leer.
  - **Lección:** Prefab pattern es excelente para ECS. Mantener simple: una función = un tipo de entidad.

---

## 4. Auto-evaluación

### 4.1 ¿Qué salió bien?

- **División del trabajo:** Cada integrante tomó un área (enemigos, terreno, UI, coordinación) con mínimo overlap. Los PRs se integraban sin conflictos grandes.
  
- **Arquitectura escalable:** ECS permitió agregar features (minimapa, smart bomb, cámara scroll) sin refactorizar la base. Un sistema nuevo es una función, un componente nuevo es una clase pequeña.

- **Cumplimiento de requisitos obligatorios:** Todas las mecánicas core están (movimiento, disparo, Lander/Mutant, astronautas, colisiones, score, pausa, game over, explosiones particles).

- **Bonuses implementados:** Minimapa funcional con terreno suavizado, sistema de vidas, cámara scroll, smart bomb, múltiples olas. Muy sólido.

- **Assets y presentación:** Sprites, sonidos, colores, fuente pixel-perfect. El juego se siente pulido visualmente.

- **Documentación durante el proceso:** Arquitectura.md bien escrita facilitó onboarding de nuevos integrantes.

### 4.2 ¿Qué salió mal?

- **Escenas no completadas:** GameOverScene y WinScene movidas al interior de PlayScene en lugar de ser escenas separadas. Esto simplificó el código pero devió al plan original.

- **Scope creep:** Agregar Baiter, Swarmer, múltiples olas fue ambicioso. Si hubiéramos priorizado mejor, habríamos pulido lo existing.

### 4.3 ¿Qué cambiaríamos para un próximo proyecto?

- **Priorización explícita:** A mitad del proyecto, quedó claro que no había tiempo para 5 olas + todos los bonuses. Hubiera sido mejor fijar un MVP (obligatorio + 1-2 bonuses) y stick to it.

- **Testing desde día 1:** Un script de test (ej: verificar que Lander spawneea correctamente, que colisiones funcionan) hubiera reducido debugging manual.

- **Documentación de decisiones:** Aunque arquitectura.md está bien, hubiera sido útil un doc de "por qué descartamos X approach" para no recaer en los mismos errores.

- **Integración frecuente:** Algunos PRs quedaron abiertos 1-2 semanas. Integrar diario hubiera reducido conflictos acumulativos.

- **Pairing ocasional:** Algunas features complejas (minimapa, Lander AI) se hubieran acelerado con 2 personas 2 horas vs 1 persona 4 horas.

---

## 5. Trabajo de cada integrante

### Jairo Reyes Ramírez
**Rol:** Project lead, coordinación, refactoring arquitectónico, game over logic

- Implementó el sistema de game over por vidas y por score (límite configurable)
- Refactoring ECS aplicando feedback: simplificó spawners, consolidó game state
- Coordinó merges de PRs, facilitó integración de features
- Debugging de problemas críticos (ej: wrap-around edge cases)
- Total: ~20 commits, muchos de ellos merges y coordinación

**Impacto en producto final:** La estabilidad del proyecto y la capacidad de integrar features en paralelo fue gracias a su coordinación. El game over polido y el refactor ECS mejoraron mantenibilidad.

### María Paula Estupiñán (mestupinanm)
**Rol:** Especialista en UI/Minimapa, terreno procedural

- Diseño e implementación del minimapa desde cero (s_minimap.py, 156 líneas)
- Smoothing del terreno procedural (interpolación lineal, multi-sample)
- Reorganización del HUD para caber minimapa + SCORE + vidas + ENE/AST en 32px
- Ajustes visuales de colores, posiciones, scale factors
- Total: ~14 commits (focalizados en minimapa y terreno)

**Impacto en producto final:** El minimapa es uno de los features más pulidos y visualmente atractivos. El terreno suavizado da sensación de calidad arcade. La UI reorganizada es clara y funcional a pesar de espacio limitado.

### Daniel Felipe Urrego Riveros
**Rol:** Coordinador técnico, player mechanics, collision

- Gestión de PRs: mergeaba cambios, resolvía conflictos
- Implementación de player mechanics (movimiento horizontal/vertical, dirección visual)
- Refine de colisiones (4 tipos: bala-enemy, bala-player, bala-astronauta, bala-bala)
- Integración de assets (sprites, sonidos)
- Debugging de edge cases (wrap-around, clipping)
- Total: ~18 commits, muchos merges y fixes

**Impacto en producto final:** El jugador se siente responsivo y controlable. Las colisiones son robustas. El flow de merges sin conflictos permitió que otros trabajaran en paralelo. Fue el "integrador" que mantuvo la rama principal estable.

### Nicolás Prada Quintero (npradaq)
**Rol:** Especialista en IA enemiga, systems

- Diseño e implementación de Lander AI (5 fases: patrol, descend, capture, abduct, dead)
- Mutant persecución agresiva del jugador
- Wave spawn system con dificultad dinámica
- Baiter AI (enemigo bonus)
- Enemy shooting system (frecuencia variable)
- Total: ~10 commits (alto impacto por commit, feature-heavy)

**Impacto en producto final:** Los enemigos son inteligentes y presentan desafío real. El wave system mantiene el juego dinámico. La IA de Lander es el "corazón" del gameplay (captura astronautas, transformación a Mutant).

---

## 6. Bonificaciones implementadas

| Bonificación              | Estado   | Notas                                |
|---------------------------|----------|--------------------------------------|
| Minimapa                  | ☑ Sí ☐ No | Terreno interpolado, entity markers (4 tipos), viewport bracket. s_minimap.py completamente funcional. |
| Sistema de vidas          | ☑ Sí ☐ No | 3 vidas iniciales, reinicio de nivel al perder una, game over al llegar a 0. Configurable en config JSON. |
| Cámara con scroll direccional | ☑ Sí ☐ No | Cámara offset según dirección de movimiento del player (no centrada). Implementado en s_player_state.py |
| Smart bomb                | ☑ Sí ☐ No | Tecla B destruye enemigos visibles en radio. Sistema funcional aunque contador UI incompleto. |
| High Score                | ☐ Sí ☑ No | No implementado. Score se registra pero no hay tabla persistente de top 5. |
| ≥ 5 olas / dificultad dinámica | ☑ Sí ☐ No | Wave spawn system con spawn_interval configurable, max_concurrent, max_total. 4+ niveles teóricos. |
| Modo atracción            | ☐ Sí ☑ No | No implementado. Requeriría escena independiente (AttractionScene) con IA automático. |
| Fase 2 (mundo explota)    | ☐ Sí ☑ No | No implementado. Sería cambio drástico de gameplay cuando se pierden todos los astronautas. |
| Baiter (enemy bonus)      | ☑ Sí ☐ No | Enemigo adicional implementado, distinto del Lander y Mutant. Sistema s_baiter. |
| Swarmer / Bomber / Pod    | ☐ Sí ☑ No | No implementados. Assets existen pero no hay sistemas de IA para ellos. |

**Resumen:** **5 bonuses completados** (minimapa, vidas, cámara scroll, smart bomb, múltiples olas + wave system). El proyecto va **más allá** de los requisitos obligatorios.

---

## 7. Referencias y enlaces

- **Juego publicado:** No publicado aún en itch.io. Falta build con pygbag.
  
- **Repositorio fuente:** https://github.com/npradaq/Introduccion-al-desarrollo-de-videojuegos-G13.git
  - **Rama main:** Rama main
  
- **Video de presentación:** 

- **Documentación del proyecto:**
  - `docs/02-arquitectura.md` — Arquitectura técnica (completa)
  - `docs/03-diseno.md` — Especificación de diseño (completa)
  - `docs/10-minimap-implementacion.md` — Guía detallada del minimapa (nuestro documento)
  - `docs/11-minimapa-cumplimiento.md` — Checklist de cumplimiento del minimapa
  - Este documento (postmortem grupal)

---

## 8. Notas finales

El proyecto es **sólido y feature-complete** más allá de lo obligatorio. El equipo trabajó bien en paralelo, mantuvo la arquitectura limpia, y entregó un juego jugable y pulido.

**Áreas de excelencia:**
- Arquitectura escalable (ECS)
- Gameplay balanceado (enemigos desafiantes, astronomautas rescatables)
- UI clara y funcional (minimapa especialmente)
- Código documentado (no perfecto pero navegable)

**Áreas de mejora para próximos proyectos:**
- Testing y QA más riguroso
- MVP + scope-gating más disciplinado
- Publicación/deployment como parte de la iteración (no al final)
- Más pair programming en features complejas
