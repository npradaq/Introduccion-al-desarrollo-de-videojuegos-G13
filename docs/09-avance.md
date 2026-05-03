# Documento de Avance — Clon de Defender (G13)

> **Entrega formativa 2 (no calificable, mentoría).** Este documento se
> entrega aproximadamente al final de la semana 2. Sirve para que tutores y
> profesores revisen el estado del proyecto.

**Fecha de corte:** _(llenar)_

---

## 1. Descripción inicial de la arquitectura propuesta

> Resumen de lo definido al iniciar el proyecto. (Para detalle ver
> `docs/02-arquitectura.md`.)

- Arquitectura **ECS** con `esper`.
- Capas: `engine/` (infra), `scenes/` (State a nivel pantalla), `ecs/`
  (componentes/sistemas), `create/` (prefabs), `assets/cfg/` (configs JSON).
- Patrones aplicados: ECS, Game Loop (asyncio), Command, State (entidad y
  escena), Service Locator, Prefab.
- Stack: Python 3.12 + `pygame-ce` + `esper==2.5` + `pygbag` + `pyinstaller`.
- Resolución: 320 × 256 (Defender original).

---

## 2. Cambios ocurridos en la arquitectura hasta ahora

> Llenar al cierre de la semana 2. Listar **decisiones que cambiaron**
> respecto al plan inicial y la **razón** del cambio.

| Cambio                                  | Razón                                        | Impacto                          |
|-----------------------------------------|----------------------------------------------|----------------------------------|
| _ej: Se separó `s_collision_*` en 4 sistemas en vez de uno_ | _Mejor SRP, facilita pruebas_ | _+claridad, +archivos_           |
|                                         |                                              |                                  |

---

## 3. Trabajo de cada integrante hasta el momento

> Resumen ejecutivo. El detalle granular vive en
> `docs/06-plantilla-contribuciones.md`.

### Jairo Reyes Ramírez (Lead Dev)
- _ej: Implementó GameEngine, SceneManager, sistemas de movimiento, render, input, wraparound, lander state. Integró Service Locator._

### María Paula Estupiñán (Diseño + QA)
- _ej: Definió diseño visual del HUD, escribió casos de prueba para player y wraparound, ajustó balances de inercia._

### Daniel F. Urrego (Niveles + QA Balance)
- _ej: Diseñó level_01.json con la curva de spawn, configuró lander/mutant/astronaut, hizo balance de dificultad._

### Nicolás Prada (Arquitectura/UX + QA Regresión)
- _ej: Refinó interface.json, diagramas de arquitectura, smoke tests, UX de menús._

---

## 4. Estado de los requerimientos obligatorios

> Marcar con [OK] / [*] (parcial) / [NO] (pendiente).

| Requisito                                                | Estado |
|----------------------------------------------------------|--------|
| Menú principal                                           |        |
| Estrellas + planeta animados                             |        |
| Movimiento + disparo del jugador                         |        |
| Spawn Lander + astronautas + comportamiento              |        |
| Wraparound (mundo y entidades)                           |        |
| Captura + Mutant                                         |        |
| Disparo enemigo                                          |        |
| Colisiones (4 tipos)                                     |        |
| Pausa con PAUSED                                         |        |
| Fanfare de inicio                                        |        |
| Score en HUD                                             |        |
| Contador enemigos + flecha de rapto                      |        |
| Explosiones de partículas                                |        |
| GAME OVER + reinicio                                     |        |
| Sonidos y animaciones                                    |        |
| Publicación itch.io                                      |        |

---

## 5. Planes para determinar el alcance final

> Llenar al cierre de la semana 2.

- **Bonos confirmados que se implementarán:** Minimapa, Vidas.
- **Bonos en evaluación (depende de tiempo restante):**
- **Bonos descartados y por qué:**
- **Riesgos abiertos al inicio de semana 3:**

---

## 6. Enlaces

- Repositorio: _(github URL)_
- Build de prueba (si existe): _(URL)_
- Capturas: _(carpeta o adjuntos)_
