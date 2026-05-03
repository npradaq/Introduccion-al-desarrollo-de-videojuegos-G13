# Diseño de Juego — Clon de Defender (G13)

---

## 1. Concepto

Reproducción fiel del arcade *Defender* (Williams, 1981). Shooter horizontal
de scroll lateral en mundo cíclico, donde el jugador defiende astronautas
de ser raptados por los enemigos *Lander*, que al alcanzar la parte superior
se convierten en *Mutant*.

**Resolución:** 320 × 256 px (original).
**Plataformas:** Web (itch.io vía pygbag) — primaria. Escritorio Linux/Windows
como secundaria.

---

## 2. Pantallas

| Pantalla        | Descripción                                                          |
|-----------------|----------------------------------------------------------------------|
| **Menu**        | Logo "DEFENDER", controles, "PRESS ENTER TO START".                  |
| **Play**        | Gameplay: jugador, mundo cíclico, planeta, estrellas, HUD.           |
| **Pausa**       | Overlay sobre Play. Texto `PAUSED` parpadeante centrado. Esconde jugador, enemigos y proyectiles. |
| **Game Over**   | Texto GAME OVER + score final. Vuelve a Menu (o pierde una vida).    |
| **Win**         | Texto de victoria al limpiar el nivel. Vuelve a Menu.                |

---

## 3. Controles

| Acción                | Teclado                  | Mouse (alternativo) |
|-----------------------|--------------------------|---------------------|
| Mover arriba/abajo    | ^ / v                   | mover mouse vertical |
| Mover izq/der         | < / >                   | bordes de pantalla   |
| Disparar              | `Espacio` o click izq.   | click izquierdo      |
| Smart bomb *(bonus)*  | `B` o click der.         | click derecho        |
| Pausar                | `P`                      | —                    |
| Salir                 | `Esc`                    | —                    |

---

## 4. Mecánicas obligatorias

### 4.1 Movimiento del jugador (con inercia)
- Aceleración constante mientras se presiona la dirección.
- Fricción cuando no hay input > el jugador sigue moviéndose y se detiene
  gradualmente.
- Velocidad máxima horizontal y vertical separadas (configurable).
- **Sin cámara (default):** el jugador siempre en el centro de pantalla;
  el mundo se mueve en sentido inverso.

### 4.2 Disparo del jugador
- Láser que cubre toda la pantalla en su dirección de avance.
- **Atraviesa** todos los enemigos que toque dentro del viewport.
- **No afecta** entidades fuera de pantalla (validar contra rect del viewport).
- Cooldown corto entre disparos (configurable).

### 4.3 Mundo cíclico (wraparound)
- Ancho del mundo ≈ **5 pantallas** (1600 px) — afinable.
- Wraparound **horizontal** para todas las entidades y para el jugador.
- Wraparound **vertical** solo para enemigos. El jugador hace clamp con
  los bordes.
- Estrellas y planeta se mueven a **diferentes velocidades** (parallax
  multi-capa).

### 4.4 Planeta procedural
- Línea quebrada generada aleatoriamente al iniciar la partida.
- Parámetros: número de segmentos, altura mínima/máxima, suavizado.
- Los astronautas caminan **debajo** de la línea, sobre la superficie del
  planeta. Ni jugador ni enemigos colisionan con la línea.

### 4.5 Astronautas
- Cantidad inicial fija por nivel (10 en el original).
- Caminan lentamente en horizontal sobre el suelo.
- **Estados** (`CAstronautState`): IDLE > WALKING > CAPTURED > FALLING > RESCUED.
- Si el Lander que lo lleva muere a media altura, el astronauta cae con
  gravedad. Si cae desde muy alto sin ser rescatado, **muere** al impactar
  el suelo.
- Si el jugador atrapa un astronauta CAPTURED/FALLING, lo lleva consigo.
  Al depositarlo en el suelo gana puntos.

### 4.6 Lander (enemigo principal)
- Se mueve por la zona superior buscando astronautas.
- Dispara al jugador ocasionalmente si está en el viewport.
- Al detectar un astronauta libre, baja, lo engancha y lo sube.
- **Estados** (`CLanderState`):
  - **PATROL**: vuelo errático, dispara ocasional.
  - **DESCEND**: baja hacia astronauta objetivo.
  - **CAPTURE**: agarra al astronauta, ahora ambos suben juntos.
  - **ABDUCT**: subir verticalmente. Al llegar al tope > muta a Mutant y
    el astronauta se elimina.
  - **DEAD**: explosión.

### 4.7 Mutant (Lander mutado)
- Persigue agresivamente al jugador.
- Disparo más frecuente que el Lander.
- **Estados**: CHASE / FIRE / DEAD.

### 4.8 Disparo enemigo
- **Bala estándar**: aleatoria, frecuencia baja, velocidad media.
- **Misil pequeño**: aún más raro, más rápido, hace búsqueda débil del
  jugador.

### 4.9 Colisiones (cuatro tipos)
1. Bala player <-> enemigo > enemigo destruido + score.
2. Bala enemigo <-> player > player destruido (GAME OVER o pierde vida).
3. Bala player <-> astronauta > astronauta muere (penalización opcional).
4. Bala player <-> bala enemigo > ambas se destruyen.

### 4.10 Explosiones de partículas
- Al destruir cualquier entidad, spawn de N partículas con `CLifetime`.
- **Player**: arranca blanco, se desvanece a colores (rojo/amarillo).
- **Enemigos**: partículas con su propio color base.
- Sonido de explosión al spawn.

### 4.11 Pausa
- Tecla `P`. Estado interno `is_paused` en `PlayScene`.
- Sistemas de update se saltan.
- Render: jugador, enemigos y proyectiles se ocultan; estrellas, planeta y
  HUD se mantienen. Texto `PAUSED` centrado, parpadeo a 2 Hz.

### 4.12 Fanfare al inicio
- Al entrar a `PlayScene`, reproducir `fanfare.ogg`.
- Bloquear input del jugador durante ~1.5s mientras suena (opcional).

### 4.13 HUD
- **Score** arriba a la izquierda.
- **Vidas** *(bonus)* arriba al centro o izq.
- **Contador de enemigos** arriba a la derecha.
- **Flecha de rapto**: cuando un Lander está abduciendo a un astronauta y
  está fuera del viewport, una flecha en el borde apunta hacia él.
  *(Si se implementa minimapa, la flecha se reemplaza/complementa.)*

### 4.14 GAME OVER y reinicio
- Cuando el jugador muere (sin vidas restantes) o cuando todos los
  astronautas mueren/son raptados > `GameOverScene`.
- Texto GAME OVER + score final + "PRESS ENTER".
- Vuelve a `MenuScene`.

### 4.15 Win
- Si se completan los spawns del nivel y se eliminan todos los enemigos >
  `WinScene` con score final.

---

## 5. Mecánicas de bonificación priorizadas

### 5.1 Minimapa (priorizado)
- Barra horizontal en la parte superior central de la pantalla.
- Representación a escala del mundo completo con marcadores de:
  - Player (color blanco).
  - Landers / Mutants (color por tipo).
  - Astronautas (color verde).
- Resalta capturas en curso con parpadeo.
- Cumple además el requisito obligatorio del "contador de enemigos + flecha"
  (la flecha se mantiene como redundancia visual fuera del minimapa).

### 5.2 Sistema de vidas (priorizado)
- Vidas iniciales configurables en `assets/cfg/lives.json` (default: 3).
- Al morir, pierde una vida. Cuando llega a 0 > `GameOverScene`.
- Bonificación: gana una vida cada 10000 puntos.

---

## 6. Mecánicas de bonificación opcionales (si sobra tiempo)

- **Cámara con scroll direccional**: el jugador se desplaza al frente
  según mire izquierda/derecha (no centrado).
- **Smart bomb**: tecla `B` elimina enemigos visibles. Inicial: 3, se
  recupera 1 cada 10000 puntos.
- **High Score**: tabla con score máximo configurable (inicial 21270).
- **Múltiples olas**: 5+ niveles configurables, dificultad creciente.
- **Modo atracción**: gameplay automático cuando nadie juega en menú.
- **Fase 2**: cuando se pierden todos los astronautas, el mundo "explota"
  y cambia el gameplay.

---

## 7. Game feel — checklist

- [ ] Hit-stop de 1-2 frames al destruir enemigo.
- [ ] Flash blanco breve del player al recibir daño.
- [ ] Sonido distinto por estado: patrol, captura, mutación, disparo, explosion.
- [ ] Volumen del fanfare un poco más alto que SFX.
- [ ] Parpadeo de 2 Hz para texto PAUSED y prompts (`PRESS ENTER`).
- [ ] Texto a colores dinámico para puntajes (bonus opcional).

---

## 8. Sonidos requeridos

| Evento                       | Asset (`assets/snd/*.ogg`) | Estado |
|------------------------------|----------------------------|----|
| Fanfare inicio nivel         | `game_start.ogg`           | [OK] |
| Disparo player               | `player_shoot.ogg`         | [OK] |
| Disparo enemigo              | `enemy_shot.ogg`           | Pendiente |
| Explosión enemigo            | `enemy_die.ogg`            | [OK] |
| Captura de astronauta        | `lander_capture_astronaut.ogg` | [OK] |
| Mutación a Mutant            | `lander_mutate_astronaut.ogg` | [OK] |
| Astronauta cayendo           | `astronaut_fall.ogg`       | [OK] |
| Rescate de astronauta        | `rescue.ogg`               | Pendiente |
| Pausa                        | `game_paused.ogg`          | [OK] |
| Muerte del jugador           | `player_die.ogg`           | [OK] |
| Game Over                    | `game_over.ogg`            | [OK] |
| Smart bomb *(bonus)*         | `smart_bomb.ogg`           | Pendiente |
| Win *(bonus)*                | `win.ogg`                  | Pendiente |

---

## 9. Sprites y Assets

### Sprites disponibles en `assets/img/`

| Elemento               | Archivo(s)                           | Estado |
|------------------------|--------------------------------------|--------|
| **Jugador**            | `player.png`                         | [OK] |
|                        | `player_burner_idle.png` (animación) | [OK] |
|                        | `player_burner_moving.png` (animación) | [OK] |
| **Lander** (obligatorio) | `enemy_lander.png`                  | [OK] |
| **Mutant** (obligatorio) | `enemy_mutant.png`                  | [OK] |
| **Bala enemiga**       | `enemy_bullet.png`                   | [OK] |
| **Astronauta** (obligatorio) | `astronaut.png`                   | [OK] |
| **Logo del juego**     | `game_logo.png`                      | [OK] |
| **Interfaz: Vidas** (bonus) | `interface_lives.png`              | [OK] |
| **Interfaz: Smart Bomb** (bonus) | `interface_smart_bomb.png`    | [OK] |
| **Enemy Baiter** (bonus) | `enemy_baiter.png`                  | [OK] |
| **Enemy Swarmer** (bonus) | `enemy_swarmer.png`                | [OK] |
| **Enemy Bomber** (bonus) | `enemy_bomber.png`                  | [OK] |
| **Enemy Pod** (bonus)  | `enemy_pod.png`                      | [OK] |
| **Bomba del Bomber** (bonus) | `bomber_bomb.png`                 | [OK] |

**Nota:** Los sprites de enemigos adicionales (Baiter, Swarmer, Bomber, Pod) están disponibles como bonificación si se decide implementar *todos los enemigos del juego original*. Vea [docs/guia-desarrollo.md](guia-desarrollo.md) para detalles sobre Conventional Commits al agregar estos bonos.

---

## 10. Paleta y estilo visual

- Fondo: negro puro.
- Estrellas: blanco / azul tenue / amarillo (parpadeo lento).
- Planeta: línea verde brillante (#00FF00 estilo arcade) o blanca.
- Player: rojo + blanco.
- Lander: amarillo.
- Mutant: rojo intenso.
- Astronauta: verde claro / amarillo.
- HUD: blanco + amarillo (acento).
- Fuente HUD: `PressStart2P.ttf`.

---

## 11. Referencias

- Gameplay: https://gamefaqs.gamespot.com/arcade/584162-defender/faqs/25139
- Emulador online: https://online-emulators.com/snes/Williams_Arcade%27s_Greatest_Hits_(USA)
- Recursos del curso: https://misw-4407-desarrollo-de-videojuegos.github.io/web-cohorte-2026-12/
