# Defender — Clon (G13)

Proyecto final del curso **MISW 4407 — Introducción al Desarrollo de
Videojuegos** (cohorte 2026-12, Universidad de los Andes).

Reproducción del clásico arcade ***Defender*** (Williams Electronics, 1981),
construida en **Python + pygame-ce** sobre una arquitectura **ECS**
(Entidad-Componente-Sistema) con `esper`. Aplica los patrones aprendidos
durante el curso: **ECS**, **Game Loop**, **Command**, **State** (a nivel
de entidad y de escena), **Service Locator** y **Prefab**, sobre el mismo
stack y las mismas convenciones del proyecto de referencia ECS construido
a lo largo del curso.

---

## Equipo (G13)

| Nombre                        | Correo                                                                      | GitHub        |
|-------------------------------|-----------------------------------------------------------------------------|---------------|
| María Paula Estupiñán         | [m.estupinanm@uniandes.edu.co](mailto:m.estupinanm@uniandes.edu.co)         | estupinanm    |
| Jairo Reyes Ramírez           | [ja.reyesr1@uniandes.edu.co](mailto:ja.reyesr1@uniandes.edu.co)             | jairoareyes2  |
| Daniel Felipe Urrego Riveros  | [d.urregor@uniandes.edu.co](mailto:d.urregor@uniandes.edu.co)               | dafur1900     |
| Nicolás Prada Quintero        | [n.pradaq@uniandes.edu.co](mailto:n.pradaq@uniandes.edu.co)                 | npradaq       |

---

## Stack

- **Python 3.12**
- [`pygame-ce`](https://pyga.me/) — render, audio e input
- [`esper`](https://github.com/benmoran56/esper) `==2.5` — ECS
- [`pygbag`](https://github.com/pygame-web/pygbag) — build a WebAssembly (itch.io)
- [`pyinstaller`](https://pyinstaller.org/) — build de escritorio

Resolución original objetivo: **320 × 256 px**.

---

## Estructura del repositorio

```
.
├── docs/                      # Documentos (propuesta, arquitectura, guía, ...)
├── assets/                    # cfg/, img/, snd/, fnt/
├── src/
│   ├── engine/                # GameEngine, SceneManager, ServiceLocator, services
│   ├── scenes/                # Menu, Play, GameOver, Win
│   ├── create/                # prefab_creator
│   └── ecs/                   # components/, components/tags/, systems/
├── main.py
├── requirements.txt
└── README.md
```

Detalle completo en [docs/04-estructura-archivos.md](docs/04-estructura-archivos.md).

---

## Ejecución local (Python)

> Requisitos: Python **3.12** y `pip`. Probado en Linux (Ubuntu 24.04).

### 1. Clonar e ingresar al repositorio
```bash
git clone https://github.com/npradaq/Introduccion-al-desarrollo-de-videojuegos-G13.git
cd Introduccion-al-desarrollo-de-videojuegos-G13
```

### 2. Crear y activar el entorno virtual
```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate            # Windows (PowerShell)
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar el juego
```bash
python main.py
```

**Escalado para desarrollo local** (resolución 320×256 es pequeña para pantallas modernas):
```bash
python main.py --scale 3        # Escalado 3x (960×768)
python main.py -s 2              # Escalado 2x (640×512) — forma corta
```

Sin flag, se ejecuta a la resolución original 320×256.

---

## Build para itch.io (web)

```bash
pygbag --build .
# El sitio estático queda en build/web/. Súbelo a itch.io como "HTML".
```

## Build de escritorio (opcional)

```bash
pyinstaller main.spec
# Ejecutable resultante en dist/
```

---

## Controles

| Acción                   | Teclado                  | Mouse              |
|--------------------------|--------------------------|--------------------|
| Mover                    | Flechas ^ v < >          | (alternativo)      |
| Disparar                 | `Espacio`                | Click izquierdo    |
| Pausar                   | `P`                      | —                  |
| Smart bomb *(bonus)*     | `B`                      | Click derecho      |
| Salir                    | `Esc`                    | —                  |

Detalle completo en [docs/03-diseno.md](docs/03-diseno.md).

---

## Documentos del proyecto

| Documento                                                                  | Propósito                              |
|----------------------------------------------------------------------------|----------------------------------------|
| [docs/guia-desarrollo.md](docs/guia-desarrollo.md)                         | Guía de desarrollo (patrones, naming, commits) |
| [docs/01-propuesta.md](docs/01-propuesta.md)                               | Propuesta técnica (entrega formativa 1) |
| [docs/02-arquitectura.md](docs/02-arquitectura.md)                         | Arquitectura ECS                       |
| [docs/03-diseno.md](docs/03-diseno.md)                                     | Diseño de juego                        |
| [docs/04-estructura-archivos.md](docs/04-estructura-archivos.md)           | Árbol de archivos                      |
| [docs/05-plan-trabajo.md](docs/05-plan-trabajo.md)                         | Cronograma 3 semanas + asignación      |
| [docs/06-plantilla-contribuciones.md](docs/06-plantilla-contribuciones.md) | Bitácora individual                    |
| [docs/07-postmortem-grupal.md](docs/07-postmortem-grupal.md)               | Post-mortem grupal (al final)          |
| [docs/08-postmortem-individual-template.md](docs/08-postmortem-individual-template.md) | Plantilla post-mortem individual |
| [docs/09-avance.md](docs/09-avance.md)                                     | Documento de avance (entrega formativa 2) |

---

## Contribuir

- Trabajamos sobre `main` con ramas `feat/*` y `fix/*`, y PR a `main`.
- **Conventional Commits 1.0 obligatorio** para todos los commits
  (`feat`, `fix`, `refactor`, `docs`, `assets`, `test`, `chore`, …).
  Ver formato, tipos, scopes y ejemplos en
  [docs/guia-desarrollo.md sec.11.1](docs/guia-desarrollo.md#111-conventional-commits-obligatorio).
- Cada integrante mantiene su bitácora en
  [docs/06-plantilla-contribuciones.md](docs/06-plantilla-contribuciones.md).

---

## Estado del proyecto

[*] **En desarrollo.** Iteración 1 (planeación + estructura inicial)
completada. Ver [docs/05-plan-trabajo.md](docs/05-plan-trabajo.md) para el
estado detallado.

---

## Enlace al juego publicado

> _(pendiente — se completará al cierre del proyecto en la página de itch.io)_

## Licencia

Proyecto académico. Los recursos gráficos y sonoros utilizados son libres
de derechos o se respeta el copyright de sus autores originales.
