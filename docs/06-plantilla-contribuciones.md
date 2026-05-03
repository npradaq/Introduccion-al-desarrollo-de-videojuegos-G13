# Plantilla de Contribuciones — G13

El proyecto utiliza un **GitHub Project Board** para gestionar y rastrear las
contribuciones de cada integrante. Esta información alimentará:
- el **post-mortem individual** (rúbrica individual: 10% de la nota),
- el documento de **trabajo de cada integrante** del post-mortem grupal
  (rúbrica grupal: 3pts/10),
- el **video de presentación final** (sección "explicación del trabajo de
  cada persona").

**Tablero del proyecto:**
https://github.com/users/npradaq/projects/1/views/1

---

## Formato de Tareas en GitHub Project

Todas las tareas creadas en el tablero deben seguir esta estructura:

### Nombre de la tarea (en GitHub Issues)

Usar **Conventional Commits** como prefijo:

```
[tipo](scope): descripción breve

Ejemplo:
feat(player): implementa inercia y fricción al CVelocity
fix(wraparound): corrige cruce de bordes con velocidad alta
docs(arquitectura): documenta orden de ejecución de sistemas
assets(cfg): agrega lander.json con velocidades por estado
test(qa): escribe casos de prueba para captura de astronauta
```

Ver [docs/guia-desarrollo.md sec.11.1](guia-desarrollo.md#111-conventional-commits-obligatorio)
para tipos, scopes sugeridos y más ejemplos.

### Descripción de la tarea (en GitHub Issues)

Completar con esta plantilla:

```markdown
## Qué
[Describe brevemente qué necesita hacerse]

## Por qué
[Explica el objetivo o el contexto. Vincula a requerimientos, diseño, etc.]

## Criterios de aceptación
- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3

## Asignado a
[@usuario](https://github.com/usuario)

## Tipo
- Código / Diseño / Pruebas / Documentación / Configuración / Build / UX

## Prioridad
- Alta / Media / Baja

## Notas
[Enlaces a documentos, referencias, comentarios adicionales]
```

### Ejemplo real

```markdown
## Qué
Implementar GameEngine con loop asyncio e integración con SceneManager

## Por qué
Fundamento de toda la arquitectura del juego. Necesario antes de empezar
cualquier escena o sistema ECS.

## Criterios de aceptación
- [ ] GameEngine carga configs del juego (window, interface, player, etc.)
- [ ] Loop asyncio corre a 60 FPS con delta_time correcto
- [ ] Despacha eventos pygame a la escena activa
- [ ] Llama update() y draw() en orden correcto
- [ ] SceneManager integrado y funcional

## Asignado a
[@jairoareyes2](https://github.com/jairoareyes2)

## Tipo
Código

## Prioridad
Alta

## Notas
- Ver docs/02-arquitectura.md sec.5 para flujo del loop
- Ver docs/05-plan-trabajo.md día 2 para deadline
- PR a main cuando esté listo
```

---

## Reglas de contribución

1. **Una tarea por responsabilidad clara.** No mezclar funcionalidades no
   relacionadas.
2. **Toda tarea debe tener:** nombre en Conventional Commits, descripción con
   criterios de aceptación, asignado, tipo, prioridad.
3. **Commits asociados:** los commits que cierren la tarea deben referenciar
   el número del issue con `Closes #123` en el mensaje de commit.
4. **Reviewer:** al menos un reviewer antes de mergear a `main`.
5. **Sincronización:** cada integrante es responsable de actualizar el estado
   de su tarea en el tablero (To Do > In Progress > In Review > Done).

---

## Estructura del tablero

- **To Do:** tareas pendientes
- **In Progress:** tareas activas en las que se está trabajando ahora
- **In Review:** tareas con PR pendiente de revisión
- **Done:** tareas completadas y mergeadas a `main`

Mantén el tablero actualizado. Es la fuente de verdad para auditar
contribuciones en el post-mortem.

---

## Resumen de aporte (para post-mortem final)

Al cierre del proyecto, cada integrante generará un resumen de sus
contribuciones directamente desde el tablero (filtrar por asignado y estado
Done). El resumen debe incluir:
- Lista de tareas completadas (con números de issue)
- Archivos o componentes principales modificados
- Logros destacados (3-5 líneas)

Usa el historial del tablero y los commits mergeados como fuente de verdad.
