# 01 · Tecnologías para convertir una pantalla en táctil

> Investigación: 2026-11-04. Objetivo: añadir tacto a monitores/portátiles/TVs **existentes** (retrofit), no fabricar pantallas.

## Resumen comparativo

| Tecnología | Cómo funciona | Multitáctil | Precisión | Coste DIY estimado (24") | Escala con el tamaño | Dificultad open source | Encaje con "AllScreenTouch" |
|---|---|---|---|---|---|---|---|
| **A. Marco IR de barrera (beam-break)** | LEDs IR en 2 lados, receptores enfrente; un dedo corta haces → X/Y | Sí (2–20 puntos según algoritmo) | Alta (paso de 3–5 mm + interpolación) | ~40–70 € | Coste lineal con el perímetro | Media (PCB + firmware) | ⭐⭐⭐⭐⭐ |
| **B. Óptico con cámaras en esquinas** | 2 cámaras IR en esquinas superiores + iluminación/retroreflectante; triangulación | Limitado (2 puntos fiables; "puntos fantasma") | Media-alta | ~30–60 € | Casi constante | Media-alta (visión + calibración) | ⭐⭐⭐⭐ |
| **C. Sensor de línea CIS (escáner reciclado)** | LEDs IR + sensor lineal de escáner; triangulación de sombras | Parcial | Alta en zonas, irregular en otras | ~30–80 € (piezas recicladas) | Necesita más sensores | Alta (ingeniería inversa de cada CIS) | ⭐⭐ (no reproducible fácilmente) |
| **D. Webcam + espejo / visión** (tipo *Sistine*) | Cámara ve el reflejo del dedo y su "sombra/reflejo" en la pantalla | Difícil | Baja-media | 0–20 € | N/A | Baja (solo software) | ⭐⭐⭐ como **prototipo/MVP** |
| **E. Cámara de profundidad / ToF** | Kinect/RealSense/ToF mide distancia dedo-superficie | Sí | Media | 100–300 € | Buena para muros/mesas | Media | ⭐⭐ (caro para monitor) |
| **F. LiDAR 2D (RPLIDAR)** | Láser giratorio paralelo a la superficie detecta objetos en el plano | Sí | Media (cm) | ~70–100 € | Excelente (paredes, proyecciones) | Media | ⭐⭐ (mejor para paredes/proyección) |
| **G. Lámina PCAP (capacitiva proyectada)** | Malla de cobre ~10 µm laminada tras un cristal | Sí (hasta 32) | Muy alta | Comercial: cientos de € | Coste por superficie | Muy alta (controlador + laminado) | ⭐ (no viable DIY) |
| **H. Resistiva / SAW** | Capas resistivas o ondas acústicas sobre cristal | Resistiva: 1 punto; SAW: pocos | Alta | Comercial | Mala | Muy alta | ⭐ |

## A. Marco IR de barrera (beam-break) — el estándar de facto

- Es lo que usan los marcos comerciales "IR touch frame" de pizarras digitales, kioscos y señalética.
- Filas de LEDs IR enfrentadas a filas de fototransistores/fotodiodos. El controlador **multiplexa**: enciende un LED, lee el receptor opuesto (y opcionalmente los vecinos en diagonal), y detecta qué haces están bloqueados.
- Con escaneo **diagonal** (un LED leído por varios receptores) se resuelven multitáctiles reales y se eliminan "puntos fantasma".
- Problema conocido: **luz ambiente** (el sol es rico en IR; los fluorescentes no). Se mitiga con LEDs **pulsados/modulados** y medición diferencial (lectura con LED encendido − lectura apagado).
- Un controlador puede manejar una matriz m×n de LEDs con m+n pines → se usan multiplexores (74HC4051/4067) o registros de desplazamiento con salida de corriente constante (STP16CP05, TLC5916).
- Ventajas para nuestro proyecto: **funciona en cualquier pantalla** (LCD, OLED, TV, proyección sobre pared), no toca el panel, **USB HID nativo sin drivers** en Windows/Linux/Android/ChromeOS.
- Inconvenientes: añade un marco de ~8–15 mm de alto sobre el bisel; detecta "casi tocando" (el haz está a 1–3 mm del cristal); el coste crece con el perímetro.

## B. Óptico de cámaras en esquinas

- Usado por pizarras tipo SMART DViT: 2 (o 4) cámaras en esquinas mirando a ras de pantalla, con borde retrorreflectante o tira de LEDs IR.
- Cada cámara da un **ángulo**; la intersección de ángulos da (x, y).
- Con 2 cámaras y 2 dedos aparecen 4 intersecciones (2 reales + 2 fantasma) → hacen falta 3–4 cámaras o heurísticas.
- Muy atractivo porque **el coste no depende del tamaño** de la pantalla. Requiere sensores con buena tasa de refresco (≥60 fps) y obturación global idealmente.

## C. CIS de escáner (proyecto *Magic Frame*)

- Reutiliza sensores lineales de escáneres (≈2700 píxeles en 20 cm) + LEDs IR; el sensor ve la sombra del dedo y se triangula.
- Muy ingenioso y barato, pero cada modelo de CIS requiere ingeniería inversa y el multitáctil completo es difícil. **No es reproducible a escala** para "que todos lo tengan".

## D. Webcam + visión por computador

- *Project Sistine* (MIT): espejo de ~1 $ delante de la webcam del MacBook; el software detecta el dedo y su reflejo en la pantalla — cuando se tocan, es un "toque".
- Variantes con MediaPipe (21 puntos de la mano) dan gestos en el aire pero **no saben si el dedo toca** la superficie sin pistas de profundidad.
- Valor para nosotros: **prototipo 100 % software** para validar la parte de "inyección de eventos táctiles" en el SO y la UX, antes de tener hardware.

## E/F. Profundidad y LiDAR

- Kinect/RealSense + proyector (WorldKit, OmniTouch, LightSpace) → convierte mesas/paredes en táctiles. Bueno para instalaciones, caro y voluminoso para un monitor.
- RPLIDAR A1/A2 a ras de pared + TUIO → paredes interactivas. Slamtec tiene herramientas (FrameGrabber.NET, cerradas, solo Windows).

## G/H. PCAP, resistiva, SAW

- Son las tecnologías de los móviles y kioscos de gama alta. Requieren laminado en fábrica, controladores específicos y calibración del sensor. Fuera del alcance de un proyecto abierto y barato.

## Conclusión técnica

Para "**todas mis pantallas táctiles, abierto y que cualquiera pueda construirlo**", los candidatos reales son:

1. **A — Marco IR modular** (robusto, probado, sin drivers) → **hardware principal**.
2. **B — Cámaras en esquinas** → línea de investigación paralela (coste independiente del tamaño).
3. **D — Webcam** → MVP de software para empezar ya sin comprar nada.

Ver [04-propuesta.md](04-propuesta.md).
