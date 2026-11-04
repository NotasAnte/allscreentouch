# 05 · Táctil con webcam (solo cámara + software)

> Investigación: 2026-11-04. Objetivo: convertir una pantalla en táctil usando solo una o dos webcams y visión por computador.

## El problema de fondo

Una webcam frontal ve **dónde** está el dedo, pero no si **toca** la pantalla: le falta la profundidad. Todas las técnicas de abajo resuelven eso de alguna manera:

| # | Técnica | Cómo se sabe que toca | Referencia |
|---|---|---|---|
| 1 | **Reflejo** | El dedo se junta con su propio reflejo en la pantalla | Project Sistine (MIT) |
| 2 | **Sombra** | El dedo tapa su sombra cuando toca | PlayAnywhere (Microsoft Research), EclipseTouch (UIST 2025), Shadow Touch (2023) |
| 3 | **Cámara rasante** (en las esquinas) | La cámara mira a ras del cristal; el dedo "cruza la línea" de la pantalla | Pizarras ópticas tipo SMART DViT, hecho con webcams |
| 4 | **Mano + profundidad estimada** | MediaPipe + profundidad monocular (Depth Anything) o modelos de presión | TouchUp, manitas, PressureVision++ (WACV 2024), Toshpulatov et al. |
| 5 | **Gestos en el aire** | No detecta toque: pellizcar = clic | handTrack, virtual-gesture-mouse |

---

## 1. Reflejo — Project Sistine

**Montaje:** un espejo pequeño delante de la webcam del portátil (con un plato de papel, una bisagra y cola caliente) para que la cámara mire la pantalla con un ángulo muy inclinado.

**Por qué funciona:** vista en ángulo rasante, cualquier pantalla se comporta como un espejo. El dedo y su reflejo se acercan hasta juntarse en el momento del toque.

**Pipeline:**
1. Filtrar por color de piel → umbral binario → contornos.
2. Tomar los 2 contornos mayores que se solapen en horizontal: el dedo (abajo) y su reflejo (arriba).
3. Punto de toque = punto medio entre la parte de arriba del dedo y la de abajo del reflejo.
4. Separación pequeña = **toque**; grande = **hover** (el dedo flota).
5. Calibración: el usuario toca puntos marcados → **homografía con RANSAC** que pasa de coordenadas de cámara a coordenadas de pantalla.

**Limitaciones:** cámara de 480p; el espejo plano solo ve parte de la pantalla (los autores proponen un espejo curvo); depende del color de piel y de la luz; solo genera eventos de ratón; código en Python 2 y solo macOS (hay un port a Windows).

**Riesgo para nosotros:** las pantallas **mate/antirreflejo** reflejan mucho menos que las brillantes de un MacBook. Hay que medirlo en tus pantallas.

## 2. Sombra — PlayAnywhere / EclipseTouch

- Una luz IR separada de la cámara proyecta la sombra del dedo. Cuando el dedo se acerca, dedo y sombra se juntan; cuando la punta tapa su sombra, cuenta como toque.
- **EclipseTouch (2025):** cámara sincronizada con varios emisores IR que generan "sombras estructuradas". Consigue **98 % de acierto** en el toque y **6,9 mm de error** al medir el hover. No he encontrado su código publicado.
- Va muy bien sobre **mesas y proyecciones**. Sobre un monitor encendido es dudoso: la propia luz del panel y su superficie apagan la sombra. Requiere una cámara IR (sin filtro IR) y LEDs IR.

## 3. Cámara rasante en las esquinas ⭐ (la más prometedora para monitores)

```
 [CAM A]─────────────────────────[CAM B]     cámaras en las esquinas superiores,
    \  ·                         ·  /        mirando a ras del cristal
     \    ·                   ·    /
      \       ·     👆     ·      /           cada cámara da un ÁNGULO del dedo
       \          · ✕ ·          /            → la intersección da (x, y)
  ▓▓▓▓▓▓▓▓▓▓ tira negra mate o LED IR ▓▓▓▓▓▓▓   fondo uniforme en los bordes
```

- Cada cámara solo necesita mirar una **franja fina** a ras del cristal: si el dedo aparece en esa franja, está tocando.
- Con dos cámaras se triangula la posición. Es la idea de las pizarras ópticas profesionales, pero con webcams USB baratas.
- Ventajas: **funciona igual en pantallas mate y brillantes**; es **independiente del tamaño**; no depende del color de piel si el fondo es uniforme (tira negra o tira de LED IR + cámara IR); **sirve de puente hacia el hardware**, porque es la "línea B" de [04-propuesta.md](04-propuesta.md).
- Inconvenientes: hay que fijar 2 cámaras en las esquinas; con 2 dedos aparecen **puntos fantasma** (2 reales + 2 falsos), así que conviene empezar con 1 dedo; necesita cámaras de **gran angular** (≥ 90°) para cubrir la pantalla entera desde la esquina.

## 4. Mano + profundidad estimada (MediaPipe y modelos)

- **TouchUp** (hackathon): MediaPipe + detección de la pantalla por bordes; los "clics" son gestos de pellizco. Sus autores admiten que con una sola cámara no hay profundidad y que el seguimiento es inestable.
- **PressureVision++ (WACV 2024):** estima la **presión** de los dedos a partir de una sola imagen RGB, con código y modelos publicados. Sirve para "tocar" superficies cualquiera en realidad mixta.
- **Toshpulatov et al.:** Depth Anything V2 ajustado + movimiento del dedo + máquina de estados con histéresis para decidir el contacto. Lo publica como CVPR 2026; no he podido verificarlo.
- Interesante como **investigación y apoyo**, pero hoy no da la precisión de milímetros que necesita una pantalla.

## 5. Gestos en el aire

Pellizcar para hacer clic, mover el índice para mover el puntero. Funciona hoy y es fácil, pero **no es tacto**: es un ratón por gestos.

---

## Comparativa para AllScreenTouch

| | Reflejo (1) | Sombra (2) | Rasante (3) | MediaPipe (4/5) |
|---|---|---|---|---|
| Hardware | 1 webcam + espejo | Cámara IR + LEDs IR | 2 webcams gran angular + tira | 1 webcam |
| Coste | ~0–10 € | ~20–40 € | ~20–50 € | 0 € |
| Toque real | Sí | Sí | Sí | No o aproximado |
| Pantalla mate | ⚠️ dudoso | ⚠️ dudoso | ✅ | ✅ |
| Multitáctil | Difícil | Difícil | 1 fácil, 2 con fantasmas | Sí (gestos) |
| Precisión esperada | Media | Media-alta | Alta | Baja |
| Encaje | **Portátil** (prueba rápida) | Mesas/proyección | **Monitores** ⭐ | Demo y gestos |

## Pipeline de software común (sirve para todas las técnicas)

```
captura (OpenCV, ≥60 fps si es posible)
  → calibración pantalla↔cámara
      (automática: la propia pantalla muestra marcadores ArUco y se calcula la homografía)
  → detección del dedo (clásica por contornos o MediaPipe)
  → clasificador toque / hover
  → tracking + filtro (1€ filter) + histéresis (evita rebotes del toque)
  → inyección en el SO:
      Linux:   uinput multitáctil (protocolo MT tipo B)
      Windows: InjectSyncPointerInput / InjectTouchInput
      macOS:   solo eventos de ratón (no hay API táctil pública)
```

**Latencia esperada:** a 30 fps son unos 33 ms por fotograma, más el procesado, así que unos 60–100 ms en total. Con cámaras de 60–120 fps (algunas webcams USB de bajo coste o cámaras con obturación global) baja bastante. Los marcos IR comerciales rondan los 10–20 ms.

**Calibración automática con ArUco** (idea propia, no la he visto en los proyectos revisados): como la cámara ve la pantalla, la pantalla puede mostrar marcadores conocidos y calcular sola la homografía, sin que el usuario toque puntos.

## Propuesta de prototipos (en este orden)

1. **Spike A — Reflejo en portátil (1–2 días):** Sistine reescrito en Python 3 + OpenCV, inyectando con `uinput` en Linux. Sirve para medir si la pantalla mate refleja lo suficiente.
2. **Spike B — Rasante con 1 cámara (1 dedo, solo eje X):** una webcam en una esquina mirando a ras del cristal, con una tira negra al fondo. Valida la detección "cruza la línea".
3. **Spike C — Rasante con 2 cámaras:** triangulación → (x, y) → toque real en el monitor.
4. Con lo aprendido, comparar con el marco IR y decidir si el producto es **cámara**, **IR** o **las dos variantes**.

## Fuentes
- [Anish Athalye – Project Sistine](https://anishathalye.com/macbook-touchscreen/) · [GitHub sistine](https://github.com/bijection/sistine) · [Windows-Touch](https://github.com/ashishgupta1350/Windows-Touch)
- [TouchUp (GitHub)](https://github.com/mattshrew/TouchUp)
- [Microsoft Research – PlayAnywhere](https://www.microsoft.com/en-us/research/video/playanywhere/) · [paper PDF](https://typeset.io/pdf/playanywhere-a-compact-interactive-tabletop-projection-nmgkpegfwe.pdf)
- [EclipseTouch – arXiv 2509.03430](https://arxiv.org/abs/2509.03430)
- [Matsubara et al. 2016 (IPSJ) – sombras con cámara IR](https://ipsj.ixsq.nii.ac.jp/record/174289/files/IPSJ-CDS16017003.pdf)
- [PressureVision++ – arXiv 2301.02310](https://arxiv.org/abs/2301.02310v3)
- [Multimodal Fingertip Contact Detection (Toshpulatov et al.)](https://muxiddin19.github.io/Multimodal-Fingertip-Contact-Detection-via-Depth-and-Motion-Fusion)
- [Roboflow – Any screen touchless (2026)](https://roboflow.com/blog/egocentric-hand-keypoint-detection)
- [manitas (GitHub)](https://www.github.com/nacmartin/manitas)
