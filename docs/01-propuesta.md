# Propuesta Técnica de Proyecto — Clon de Defender

**Curso:** MISW 4407 — Introducción al Desarrollo de Videojuegos
**Cohorte:** 2026-12
**Equipo:** G13
**Fecha:** Mayo 2026

---

## 1. Integrantes

| Nombre                        | Correo                                                  | GitHub        | Rol principal                                  |
|-------------------------------|---------------------------------------------------------|---------------|------------------------------------------------|
| Jairo Reyes Ramírez           | [ja.reyesr1@uniandes.edu.co](mailto:ja.reyesr1@uniandes.edu.co)         | jairoareyes2  | Implementación de funcionalidades (lead dev)   |
| María Paula Estupiñán         | [m.estupinanm@uniandes.edu.co](mailto:m.estupinanm@uniandes.edu.co)     | estupinanm    | Diseño de juego y pruebas funcionales          |
| Daniel Felipe Urrego Riveros  | [d.urregor@uniandes.edu.co](mailto:d.urregor@uniandes.edu.co)           | dafur1900     | Diseño de niveles y pruebas de balance         |
| Nicolás Prada Quintero        | [n.pradaq@uniandes.edu.co](mailto:n.pradaq@uniandes.edu.co)             | npradaq       | Diseño de arquitectura/UX y pruebas de QA      |

> **Nota sobre la rúbrica:** el enunciado exige que *todos los integrantes
> programen*. Aunque el lead de implementación es Jairo, cada integrante
> mantendrá al menos una contribución de código (configuraciones JSON,
> servicios menores, pulido de un sistema, scripts de build) registrada
> mediante commits propios. Ver `docs/05-plan-trabajo.md`.

**Repositorio público:** https://github.com/npradaq/Introduccion-al-desarrollo-de-videojuegos-G13/

---

## 2. Juego a replicar

**Defender** (Williams Electronics, 1981). Shooter horizontal arcade con
mundo cíclico (*wraparound*), inercia del jugador, captura/rapto de
astronautas y mutación de enemigos.

Resolución original objetivo: **320 × 256** (escalable visualmente, pero
mantenida internamente para fidelidad).

---

## 3. Propuesta técnica y arquitectónica

### 3.1 Stack

- **Python 3.12** + `pygame-ce` para render/audio/input.
- **`esper` 2.5** como librería ECS.
- **`pygbag`** para empaquetado WebAssembly (entrega itch.io).
- **`pyinstaller`** como respaldo para build de escritorio.

Aplicamos el mismo stack y patrones aprendidos durante el curso
(ECS, State, Service Locator, Command) y consolidados en nuestro proyecto
de referencia, lo cual reduce el riesgo de configuración y permite
capitalizar lo aprendido.

### 3.2 Patrones aplicados

| Patrón                  | Aplicación en el proyecto                                                |
|-------------------------|--------------------------------------------------------------------------|
| **ECS**                 | Eje arquitectónico. Toda lógica modelada como entidad/componente/sistema |
| **Game Loop**           | `asyncio` loop en `GameEngine.run()` (compatible con pygbag)             |
| **Command**             | `CInputCommand` + `CommandPhase` para desacoplar input de acción         |
| **State (entidad)**     | Player, Lander, Mutant y Astronaut tienen state machines propias         |
| **State (escena)**      | `SceneManager` orquesta `MenuScene`, `PlayScene`, `GameOverScene`, `WinScene` |
| **Service Locator**     | Acceso global a recursos (imágenes, sonidos, fuentes, escenas)           |
| **Prefab**              | `prefab_creator.py` concentra la creación de entidades complejas         |
| **Data-driven configs** | Todos los parámetros del juego en JSON (`assets/cfg/`)                   |

### 3.3 Decisiones clave

- **Reutilizar la estructura aprendida en el curso y consolidada en nuestro
  proyecto de referencia ECS** (carpeta `src/`, naming `c_*`/`s_*`,
  `ServiceLocator`, `prefab_creator`, configs JSON) para acortar el setup
  y concentrarnos en las mecánicas propias de Defender.
- **Introducir `SceneManager`** como extensión nueva: el proyecto de
  referencia ECS tenía un solo `GameEngine` monolítico; aquí necesitamos
  varias pantallas (menú, juego, game over, win) y el patrón State a
  nivel de escena es la solución natural y exigida por la rúbrica.
- **Configuraciones por entidad** (`lander.json`, `mutant.json`, etc.) en
  vez de un único archivo monolítico, para que cada integrante pueda
  modificar su parte sin conflictos en `git`.
- **Mundo en coordenadas internas**: el mundo Defender es ~5 pantallas de
  ancho con wraparound horizontal. Internamente las posiciones X se
  manejan en `[0, world_width)` y la cámara aplica el offset al renderizar.

### 3.4 Alcance técnico estimado

- **Obligatorio (cubre 100% rúbrica base):** menú, fondo de estrellas,
  planeta procedural, jugador con inercia y disparo, wraparound, Lander +
  Mutant, captura y rapto, colisiones, pausa, fanfare, score, contador
  enemigos + flecha de rapto, explosiones de partículas, GAME OVER, WIN,
  publicación itch.io.
- **Bonos priorizados:** **Minimapa** y **sistema de vidas**.
- **Bonos opcionales (si sobra tiempo):** cámara con scroll direccional,
  smart bomb, high score, niveles configurables (≥5 olas), atracción mode,
  fase 2.

---

## 4. Documentos asociados

- `docs/02-arquitectura.md` — diseño detallado ECS.
- `docs/03-diseno.md` — diseño de juego (mecánicas y controles).
- `docs/04-estructura-archivos.md` — árbol del repositorio.
- `docs/05-plan-trabajo.md` — cronograma 3 semanas y asignación.
- `docs/06-plantilla-contribuciones.md` — bitácora individual.

---

## 5. Cronograma macro

| Semana | Hito                                                   |
|--------|--------------------------------------------------------|
| 1      | Setup, engine, escenas, player, mundo (estrellas+planeta), wraparound. Entrega formativa 1. |
| 2      | Enemigos (Lander, Mutant), astronautas, captura/rapto, colisiones, disparo enemigo. Entrega formativa 2. |
| 3      | HUD, sonidos, GAME OVER/WIN, bonos priorizados (minimapa + vidas), build itch.io, post-mortems. Entrega final. |

Detalle día a día en `docs/05-plan-trabajo.md`.
