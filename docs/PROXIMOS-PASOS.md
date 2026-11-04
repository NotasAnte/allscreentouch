# Próximos pasos propuestos

> Recopilación de todo lo propuesto durante la investigación y el prototipo (2026-11-04).
> El plan por fases está en [ROADMAP.md](ROADMAP.md); aquí van las propuestas concretas, con su porqué.

## Estado actual

- ✅ Investigación: tecnologías, mercado, open source, webcam y gestos (`docs/investigacion/`).
- ✅ Prototipo **G1 – apuntar y hacer clic con la mano** (`software/gestos/`), probado en Ubuntu 26.04 Wayland + Logitech C925e + monitor 3440×1440.

---

## 1. Control por gestos (`software/gestos/`) — siguiente en la cola

### 1.1 Círculo de feedback en pantalla (prioridad alta)
- Un círculo semitransparente sobre el cursor que **se cierra según la fuerza del pellizco**, como en Meta Quest. Así sabes cuándo vas a hacer clic antes de que ocurra.
- Avisos en pantalla (no solo en la ventana de la cámara): "mano de canto", "dorso", "pausa".
- **Reto técnico:** en Wayland/GNOME una app no puede ponerse por encima de todo ni dejar pasar los clics a lo de debajo tan fácilmente como en X11. Opciones a evaluar: capa `wlr-layer-shell` (no la soporta GNOME), extensión de GNOME Shell, o ventana GTK4 transparente sin decoración.

### 1.2 Más gestos (Spike G2)
| Gesto | Acción |
|---|---|
| Pellizco mantenido + mover | Arrastrar (ya funciona) |
| Pellizco mantenido + subir/bajar | Scroll |
| Pellizco pulgar-corazón | Clic derecho |
| Palma abierta 1 s | Pausar o reanudar el control (sin teclado) |
| Dos manos pellizcando + separar | Zoom |

### 1.3 Modo rayo, estilo Quest (Spike G3)
- Rayo hombro → mano → plano de la pantalla, con MediaPipe Pose + Hands.
- Calibración apuntando a las 4 esquinas de la pantalla.
- Medir el error en cm; si con una cámara no basta, probar **2 webcams en estéreo**.

### 1.4 Ajustes de calidad pendientes
- **Caja de interacción más grande** (`--box-width 0.6`) si el temblor que queda (~6×8 px) molesta: menos amplificación a cambio de más brazo.
- **Ganancia no lineal** (como la aceleración del ratón) para combinar precisión en movimientos lentos y rapidez en los largos.
- **Detectar mal la luz**: avisar si la imagen está demasiado oscura (en penumbra baja la calidad del seguimiento).
- **Multimonitor**: mapear la caja a la pantalla concreta, no al escritorio entero.
- **Empaquetado**: lanzarlo sin terminal (icono en la bandeja, autoarranque, perfil de ajustes guardado).
- **Otros sistemas**: Windows (`SendInput`) y macOS (`CGEvent`, sin táctil nativo).

### 1.5 Limitaciones conocidas (por diseño)
- Con **una sola cámara**, un pellizco con la mano de canto o el dorso hacia la cámara no se distingue de uno fantasma → solo se hace clic con la palma de frente.
- La latencia mínima es la de la cámara (~33 ms a 30 fps) más el procesado.

---

## 2. Táctil con webcam (ver [05-webcam.md](investigacion/05-webcam.md))

1. **Spike A — reflejo tipo Sistine en el portátil**: medir si una pantalla mate refleja lo suficiente.
2. **Spike B — una cámara rasante en una esquina**, 1 dedo, con una tira negra de fondo.
3. **Spike C — dos cámaras rasantes + triangulación** → toque real en el monitor. Es la opción más prometedora para monitores: funciona con pantallas mate y no depende del tamaño.
4. **Calibración automática con marcadores ArUco** mostrados en la propia pantalla (idea propia, no vista en otros proyectos).

Todos reutilizan la capa ya hecha en `software/gestos/`: ratón virtual por uinput, filtros y registro de datos.

---

## 3. Hardware: marco IR modular (ver [04-propuesta.md](investigacion/04-propuesta.md))

1. **Comprar un marco IR chino barato** como referencia y desmontarlo.
2. **Prototipo en protoboard**: 8 LEDs + 8 receptores + RP2040, lectura diferencial (LED encendido − apagado) contra la luz ambiente.
3. **Firmware USB HID digitizer** (1 → 5 → 10 contactos) sin drivers en Windows, Linux, Android y ChromeOS.
4. **PCBs modulares encadenables** en KiCad (segmento emisor, segmento receptor, controladora) + carcasa paramétrica por tamaño.
5. **Configurador web** (WebUSB/WebSerial) para calibrar y actualizar el firmware.
6. Línea paralela: **cámaras en esquinas** con LEDs IR, si el marco IR sale caro en tallas grandes.

---

## 4. Proyecto y comunidad

- **Licencias** propuestas: hardware CERN-OHL-S v2, software MIT o Apache-2.0, documentación CC BY-SA 4.0. *(El prototipo de gestos ya declara MIT en su `pyproject.toml`.)*
- **Repositorio público** en GitHub cuando haya algo enseñable, con README en español e inglés.
- **Vídeo/GIF de demo** del control por gestos para el README.

## 5. Decisiones pendientes del usuario

- [ ] ¿Qué pantallas exactas quieres convertir (tamaños, portátil/monitor/TV) y con qué sistemas operativos?
- [ ] ¿Basta con 1–2 dedos o quieres multitáctil completo?
- [ ] ¿Presupuesto por pantalla y si sabes soldar o tienes impresora 3D?
- [ ] Orden de prioridad entre: (1) seguir puliendo gestos, (2) táctil con webcam, (3) marco IR.
- [x] Licencia del software: **MIT** (decidido 2026-11-04).
