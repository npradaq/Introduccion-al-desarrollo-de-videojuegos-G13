# Post-Mortem Grupal — Clon de Defender (G13)

> **Pendiente de llenar al final del proyecto.** Este documento es el
> entregable del post-mortem grupal (rúbrica: 10% de la nota final). Debe
> responder con **claridad**, **precisión** y **profundidad** las preguntas
> de la rúbrica para lograr el "Excelente".

---

## 1. Resumen del proceso (semana a semana)

> *Describir cómo evolucionó el proyecto.*

**Semana 1 — Fundación**
- Logros:
- Bloqueos:
- Cambios respecto al plan inicial:

**Semana 2 — Gameplay core**
- Logros:
- Bloqueos:
- Cambios respecto al plan inicial:

**Semana 3 — Polish y entrega**
- Logros:
- Bloqueos:
- Cambios respecto al plan inicial:

---

## 2. Análisis arquitectónico

### 2.1 Organización de clases, componentes y sistemas

> *Describir la estructura final. Adjuntar diagrama si es posible.*

- **Capa engine:**
- **Capa scenes:**
- **ECS (componentes y sistemas):**
- **Configs y assets:**

### 2.2 Decisiones tomadas y su justificación

> *¿Por qué se eligió cada decisión arquitectónica?*

- ¿Por qué `esper` y no un ECS propio?
- ¿Por qué `SceneManager` separado del `GameEngine`?
- ¿Por qué configs JSON una por entidad y no monolíticas?
- ¿Por qué cuatro sistemas de colisión separados?
- ¿Por qué el patrón State a dos niveles (escena y entidad)?

---

## 3. Análisis de patrones usados

### 3.1 ECS — opinión grupal
> *¿Qué tan bien funcionó ECS para este juego? Comparar con otras aplicaciones (web, datos, etc.).*

- Ventajas observadas:
- Desventajas observadas:
- Lecciones para próximos proyectos:

### 3.2 Otros patrones aplicados
- **Command (input):** ¿facilitó cambios o se sintió overhead?
- **State (entidad):** ¿la separación por entidad fue suficiente?
- **State (escena):** ¿el `SceneManager` ayudó al flujo del juego?
- **Service Locator:** ¿hubo problemas de acoplamiento o estado global?
- **Prefab:** ¿se mantuvo limpio o se infló?

---

## 4. Auto-evaluación

### 4.1 ¿Qué salió bien?
-
-
-

### 4.2 ¿Qué salió mal?
-
-
-

### 4.3 ¿Qué cambiaríamos para un próximo proyecto?
-
-
-

---

## 5. Trabajo de cada integrante

### Jairo Reyes Ramírez
> *Roles y actividades específicas. Influencia en el producto final.*

### María Paula Estupiñán
> *Roles y actividades específicas. Influencia en el producto final.*

### Daniel Felipe Urrego Riveros
> *Roles y actividades específicas. Influencia en el producto final.*

### Nicolás Prada Quintero
> *Roles y actividades específicas. Influencia en el producto final.*

---

## 6. Bonificaciones implementadas

| Bonificación              | Estado   | Notas                                |
|---------------------------|----------|--------------------------------------|
| Minimapa                  | ☐ Sí ☐ No |                                      |
| Sistema de vidas          | ☐ Sí ☐ No |                                      |
| Cámara con scroll direccional | ☐ Sí ☐ No |                                  |
| Smart bomb                | ☐ Sí ☐ No |                                      |
| High Score                | ☐ Sí ☐ No |                                      |
| ≥ 5 olas / dificultad dinámica | ☐ Sí ☐ No |                                |
| Modo atracción            | ☐ Sí ☐ No |                                      |
| Fase 2                    | ☐ Sí ☐ No |                                      |
| Otros                     |          |                                      |

---

## 7. Enlaces

- **Juego publicado:** _(itch.io URL)_
- **Repositorio fuente (tag final):** _(github URL + tag v1.0.0)_
- **Video de presentación:** _(YouTube/Drive URL)_
