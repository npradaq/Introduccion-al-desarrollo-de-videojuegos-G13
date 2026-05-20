# Post-Mortem Individual — María Paula Estupiñán Molina

> Este documento es tu reflexión personal sobre el proyecto. Sé **claro**, **específico** y **reflexivo** para lograr el "Excelente" en las tres dimensiones.
>
> **Rúbrica individual: 10% de la nota final.**

---

**Nombre completo:** María Paula Estupiñán Martinez  
**Correo:** m.estupinanm@uniandes.edu.co
**GitHub:** mestupinanm  
**Fecha:** 19 de Mayo 2026

---

## 1. Descripción del rol y trabajo desempeñado *(rúbrica: 3.5 pts)*

> *Para "Excelente": describir con claridad las tareas e influencia en el producto final.*

- **Rol asumido:**
  - Especialista en UI/minimapa y terreno procedural
  - Responsable de la presentación visual del HUD y el minimapa

- **Tareas concretas que realicé** (referenciar archivos/sistemas/configs específicos):
  - **Creación del terreno procedural con Perlin Noise 1D** (`src/engine/perlin.py` y `src/create/prefab_creator.py` → `create_terrain()`)
    - Implementé `noise1d()` y `octave_noise1d()` para generar terreno orgánico y procedural sin hardcoding
    - Configuré parámetros (frequency, amplitude, persistence, lacunarity) para que el terreno se viera natural y arcade-like
    - Aplicé wrap-around: el terreno se repite seamlessly en un mundo cíclico (1600px ~ 5 pantallas)
    - El resultado: terreno que parece dibujado a mano pero es 100% procedural
  - **Creación del sistema minimapa desde cero** (`src/ecs/systems/s_minimap.py`, 156 líneas)
  - **Implementación de interpolación lineal para suavizado del terreno en el minimapa**
    - 2 muestras por píxel minimap para smooth rendering sin aliasing
    - Mapeo correcto de coordenadas mundo → minimapa con sincronización a cámara dinámica
  - **Reorganización del HUD** para acomodar minimapa + SCORE + vidas + contadores ENE/AST en 32px
  - **Ajustes de posiciones y colores** en `assets/cfg/interface.json`

- **Decisiones que tomé y cómo afectaron el producto final:**
  - **Usar Perlin Noise 1D en lugar de terreno hardcodeado o aleatorio puro.** Esto fue crítico: Perlin Noise genera terreno que se ve orgánico (suave, sin picos abruptos) pero es procedural. El alternativa hubiera sido arrays hardcodeados (aburrido, sin variedades) o Math.random puro (aliasing visual, desagradable). La decisión hizo que el juego se sienta más vivo y profesional.
  
  - **Aplicar wrap-around en el terreno.** Decidí que el terreno se repita seamlessly en lugar de terminar y empezar de nuevo. Esto requirió usar `% world_width` en los índices de Perlin Noise. El beneficio: el mundo cíclico se siente infinito, sin cortes visuales.
  
  - **Usar interpolación lineal (2 muestras por píxel) para el terreno del minimapa.** En lugar de renderizado simple (que hubiera visto como puntos), interpolación lineal hace que el minimap refleje fielmente el terreno real, mejorando la percepción de calidad.
  
  - **Mantener el minimapa en 160×26px.** Decidí que fuera pequeño (no full-screen) para que el HUD original cupiera. Esto fue un trade-off: menos espacio pero más información visible simultáneamente.
  
  - **Reorganizar el HUD vertical (SCORE→vidas abajo, AST→ENE abajo).** En lugar de horizontal (que no cabia). Esto solucionó espacio limitado manteniendo todos los elementos visibles y funcionales.

- **Evidencia** (commits, PRs, archivos):
  - Commits principales con git log --author="mestupinanm":
    - 913767d: feat(mapa): mostrando todos los componentes en la parte superior
    - 4484da4: feat(mapa): correccion seccion blanca indicativa donde esta la nave
    - b100313: feat(mapa): mejoras mini mapa terreno y creacion nave
    - d1f0254: feat(mapa): mini mapa en proceso de funcionar
    - 21f8169: feat(terreno): eliminar variables innecesarias
    - dba426c: feat(terreno): cambio estructural codigo
  - **Archivos creados:**
    - `src/ecs/systems/s_minimap.py` (156 líneas, sistema minimap completo)
    - Modificaciones en `src/engine/perlin.py` (octave_noise1d, configuración de parámetros)
  - **Archivos modificados:**
    - `assets/cfg/interface.json` (sección hud.minimap con parámetros visuales)
    - `src/create/prefab_creator.py` (create_terrain() con Perlin Noise procedural)

---

## 2. Ajustes — qué salió bien, mal y qué cambiaría *(rúbrica: 3.5 pts)*

> *Para "Excelente": describir todos los elementos solicitados sin imprecisiones.*

### 2.1 Lo que salió bien
- **Terreno Perlin Noise:** El terreno procedural se ve orgánico y vivo. No hay dos mundos iguales (es procedural), pero todos se ven naturales (gracias a Perlin Noise, no aleatorio puro). Los parámetros (frequency, persistence, lacunarity) están bien calibrados.
- **Wrap-around sin costuras visuales:** El terreno se repite infinitamente sin cortes. Esto fue desafiante pero resultó perfecto. El jugador puede viajar al infinito sin notar que está en un mundo cíclico.
- **Minimapa funcional y visualmente pulido.** La interpolación lineal hizo que se viera orgánico y similar al terreno real, a pesar del tamaño reducido. El minimapa es una réplica fiel del mundo.
- **Reorganización del HUD solucionó un problema real de espacio.** La solución (vertical stacking) fue simple y legible. Todo cabe en 32px sin sentirse apretado.
- **Documentación del minimapa.** Escribir guías para compañeros no solo ayudó al equipo sino que también aclaró mi propio entendimiento del sistema.
- **Colaboración fluida con Daniel en ajustes de posiciones de UI.** No hubo conflictos de merge. La sinergia fue buena.
- **Escalabilidad:** Cambiar colores, tamaños, posiciones es trivial (solo editar interface.json). El código ECS es agnóstico a estos valores.

### 2.2 Lo que salió mal
- No implementé detección de abducción activa (parpadeo en minimapa cuando Lander captura). Era un bonus dentro del bonus pero habría agregado pulido.
- El minimapa muestra 3 pantallas en lugar del "mundo completo" que sugería el spec. Decisión pragmática pero técnicamente una desviación.
- Landers y Mutants comparten color rojo en lugar de tener colores distintos. Simplificó config pero pierde información visual.
- No agregué escala de leyenda (dónde dice cuál color es qué). Los colores son intuitivos pero documentación visual hubiera ayudado.

### 2.3 Ajustes que haría para un próximo proyecto
> *(a título personal, no del grupo)*
- Desde el inicio, definir un "acceptance criteria" visual: "minimapa muestra X, se ve Y". No dejarme llevar por "hagamos que se vea bien" sin criterios objetivos.
- Hacer debugging visual más riguroso: usar herramientas de profiling de rendering (ej: pygame profiler, VS Code debugger con breakpoints visuales).
- Proponer testing visual automatizado (screenshot comparison) para cambios de UI. Evitar regressions por cambios accidentales.
- Comunicar más sobre deviaciones del spec. Decidir mostrar 3 pantallas en lugar de mundo completo fue correcta, pero debí documentar por qué.
- Colaborar más temprano con IA de enemigos (Nicolás) para entender qué información visual es útil en el minimapa. Posibles mejoras: mostrar radio de detección de Lander, etc.

---

## 3. Evaluación — aprendizajes *(rúbrica: 3 pts)*

> *Para "Excelente": sintetizar los principales aprendizajes, relacionarlos con elementos del curso **y** con exploración personal.*

### 3.1 Resumen de lo aprendido
- **Perlin Noise y procedural generation:** Aprendí cómo Perlin Noise genera terreno orgánico sin hardcoding. Los conceptos clave (fade, lerp, gradients, octaves) ahora tienen sentido. Entiendo por qué Perlin Noise es el estándar en games (vs simplex, vs random puro).
- **Coordinate systems en games:** Aprendí cómo mapear coordenadas del mundo a un minimapa. No es trivial (minimap_start, minimap_range, scaling). Esto me enseñó sobre transformaciones matemáticas en rendering.
- **Wrap-around y seamless tiling:** Implementar terreno que se repite sin cortes visuales fue desafiante. Aprendí sobre modulo aritmética (`% world_width`) y cómo mantener continuidad en límites.
- **Data-driven design:** Cambiar todo del minimapa y terreno (colores, posiciones, tamaños) sólo editando JSON. Sin tocar código. Esto es el poder de configs bien diseñadas.
- **Smoothing en rendering:** Interpolación lineal entre puntos no es obvia. Aprendí por qué es importante para evitar aliasing visual y hacer que mundos pequeños (minimapa) reflejen fieles el mundo grande.

### 3.2 Relación con conceptos del curso
- **Procedural Generation (Perlin Noise):** No fue tema oficial del curso, pero aprendí que es fundamental en game dev. Perlin Noise genera contenido naturalmente sin hardcoding. Esto confirma la filosofía de DRY (Don't Repeat Yourself) aplicada a assets.
- **ECS:** El minimapa es un sistema puro: lee CTerrain, lee CTransform de entidades, renderiza. No modifica nada. El terreno es un componente CTerrain que encapsula las alturas. Esto confirma por qué ECS es bueno para rendering: sistemas puros sin efectos secundarios.
- **Game Loop:** El terreno se genera una vez en PlayScene.on_enter(). El minimapa se renderiza cada frame en PlayScene.draw(). Entendí la diferencia entre initialization, update (lógica) y render (presentación).
- **Patrón Command:** No lo usé directamente, pero entiendo que CInputCommand podría extenderse para "mostrar/ocultar minimapa" fácilmente.
- **Patrón State:** Aunque no usé State pattern en el terreno/minimapa, vi cómo CLanderState muestra información diferente en el minimapa (PATROL vs ABDUCT).
- **Service Locator:** El minimapa usa interface_cfg (cargado por ServiceLocator) sin acoplamiento directo. Es un buen ejemplo de inyección vía config.
- **Manejo de assets / configs:** interface.json es la fuente de verdad del minimapa. Cambios visuales = cambios en JSON. Esto es escalable. El terreno es procedural (no un asset), pero podría ser configurado también.
- **Despliegue (web/escritorio):** No profundicé en pygbag/itch.io, pero ahora entiendo que el terreno Perlin Noise seguiría funcionando en web (pygame.js) sin cambios, porque es puro código (no archivos binarios).

### 3.3 Aspectos por apropiar (lo que aún me falta dominar)
- **Optimización de procedural generation:** Generar terreno cada frame sería lento. Lo cacheo al inicio, pero ¿qué pasa en mundos infinitos? Chunking y level-of-detail son conceptos que no exploré.
- **Profiling visual:** No sé bien cómo medir performance de rendering. ¿Cuántos FPS cuesta el minimapa? ¿El terreno Perlin Noise? No lo medí con herramientas.
- **Shaders / GPU rendering:** El minimapa es CPU (pygame.draw.line). Para un juego más grande, shaders (OpenGL/Vulkan) serían necesarios.
- **Responsive design:** El HUD está hardcodeado a 320×32. ¿Qué pasa en pantallas más grandes? No lo generalicé. El terreno Perlin Noise es escalable teóricamente pero no lo probé.
- **Accesibilidad en games:** Colores rojo/verde para enemigos/astronautas son problema para daltonismo. No consideré esto.
- **Animation / transitions:** El minimapa es estático. Animaciones (ej: fade-in, zoom) habrían agregado pulido pero requieren más complejidad.

### 3.4 Conexión con exploración personal
> *Lecturas, tutoriales, juegos analizados, herramientas exploradas fuera del curso.*
- **Perlin Noise research:**
  - Leí el artículo original de Ken Perlin (improved Perlin Noise paper) para entender la matemática detrás.
  - Vi tutoriales en YouTube: "Perlin Noise explained", "How to use Perlin Noise in game dev"
  - Aprendí la diferencia entre Perlin Noise (suave, orgánico) vs Simplex Noise (más eficiente) vs Random puro (aliasing).
  - Esto fue crucial: entender por qué Perlin Noise es el estándar en games.

- **Terreno procedural en otros engines:**
  - Vi tutoriales de Minecraft terrain generation (uses layered Perlin Noise con octaves).
  - Analicé cómo No Man's Sky genera mundos infinitos (cada planeta tiene un seed de Perlin Noise).
  - Esto me enseñó escalabilidad: generar infinitamente vs cachear.

- **Minimapa en arcade classics:**
  - Jugué el Defender original en emulador en línea para entender la mecánica del minimapa arcade (cómo muestra mundo completo, cómo parpadea abducción).

- **Rendering en pygame:**
  - Vi tutoriales de pygame rendering (YouTube: "pygame graphics optimization") para entender draw.line vs draw.polygon vs rect.
  - Exploré ejemplos de interpolación lineal en gráficos (no específicamente juegos, pero gráficos en general).

---

## 4. Reflexión final (libre)

> *Espacio opcional para cualquier reflexión adicional sobre el proyecto, el equipo, o tu crecimiento.*

Trabajar en el terreno procedural con Perlin Noise y el minimapa fue una experiencia profunda. No son features "invisibles" - son cosas que el jugador siente (terreno orgánico) y ve (minimapa) cada frame. Eso me obligó a ser cuidadosa con detalles técnicos y visuales.

**Perlin Noise en particular fue un "aha moment":** Antes pensaba que los mundos de los juegos eran creados manualmente o al azar. Descubrir que pueden ser **procedurales y al mismo tiempo hermosos** abrió mi mente. Es una aplicación real de matemática en programación: algunas fórmulas (fade, lerp, gradient) crean magia.

Lo que más me gustó fue ver cómo sistemas complejos (Perlin Noise + interpolación lineal + wrap-around + coordinate mapping) se volvió algo elegante cuando está bien estructurado.

El equipo fue colaborativo. Daniel me ayudó con ajustes de layout, Jairo coordinó merges sin conflictos, Nicolás aseguró que los enemigos y astronautas aparecieran correctamente en el minimapa. Sin esa colaboración, ambos features (terreno y minimapa) serían mucho peores.

**Reflexión de crecimiento:** Entré al proyecto sin haber trabajado con Perlin Noise. Ahora no solo lo entiendo, sino que puedo explicarlo, documentarlo, y escalarlo a problemas más complejos. Eso es lo que significa "apropiar" un concepto.

Si tuviera que resumir: **Un videojuego no es solo código. Es matemática, arte, y comunicación de equipo entrelazadas.** Cada línea de código Perlin Noise es matemática que se ve como arte en pantalla.
