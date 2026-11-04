# 06 · Control por gestos a distancia (estilo Meta Quest)

> Investigación: 2026-11-04. Idea: una webcam te graba, apuntas a la pantalla con la mano y haces gestos (pellizcar = clic), como el *hand tracking* de Meta Quest, sin tocar la pantalla.

## Cómo lo hace Meta Quest

- El SDK da por cada mano una **pose de puntero (pointer pose)**: un origen y una dirección filtrados. Con ese rayo se apunta a la interfaz.
- **Pellizco índice-pulgar = seleccionar**, equivalente al gatillo del mando. El SDK distingue un bit de "pellizcando" (para disparar el evento) de una **fuerza de pellizco continua** (para dar feedback visual).
- La documentación pública **no explica** cómo calcula el origen del rayo. En la comunidad se dice que parte de un punto estimado del hombro y pasa por la mano, pero **no lo he podido confirmar** en las fuentes.
- La diferencia con nosotros: las Quest tienen **varias cámaras IR y profundidad real**; nosotros tendríamos **una sola webcam RGB**.

## Productos y proyectos parecidos

| Proyecto | Qué hace | Hardware | Licencia | Notas |
|---|---|---|---|---|
| **Ultraleap TouchFree** | "Air push": empujas la mano hacia la pantalla = clic | Cámara Ultraleap (Leap Motion, 3Di, Stereo IR 170) | **Propietaria**, solo Windows | Solo es abierto el *Web Tooling* |
| **Google Project Gameface** | Mueves el ratón con la cabeza; clics con gestos de la cara (cejas, boca) | Webcam | **Open source** (MediaPipe + Python) | Pensado para accesibilidad; buen ejemplo de app real con MediaPipe |
| **airmouse** (Rcidshacker) | Webcam → MediaPipe → máquinas de estado de gestos → SendInput | Webcam | Open source | Windows; filtro 1€ ajustado contra temblor y retardo |
| **HandGesture-Mouse** (murfidya) | Pellizco = clic, cursor con el índice, hilo de cursor a 60 Hz | Webcam | Open source | Python, Windows |
| **pointer** (slastra) | Cursor con suavizado one-euro, legacy o Kalman; clic por proximidad de dedos | Webcam | Open source | Python + OpenCV |
| **openhandtrack** (PyPI) | Suavizado one-euro + `pointing_direction(hand)` | Webcam | Open source | Lo más cercano a un "rayo" que he encontrado |
| **hand-playground** | Laboratorio en navegador: índice = cursor, pellizco = clic | Webcam | Open source | Parámetros del 1€ documentados (freq=30, minCutoff=1.5, beta=0.01) |

**Conclusión:** sí hay ratones por gestos con webcam, pero **ninguno hace el "apuntar con rayo" de Quest**. Todos mueven el cursor según dónde está la mano en la imagen. El modo "rayo" habría que construirlo combinando piezas.

## Dos formas de mover el puntero

### A. Mapeo relativo ("caja de interacción") — fácil y estable
```
  imagen de la cámara               pantalla
  ┌────────────────────┐            ┌────────────────────┐
  │    ┌────────┐      │   escala   │                    │
  │    │ ✋ caja │ ─────┼──────────► │        ● cursor    │
  │    └────────┘      │  + filtro  │                    │
  └────────────────────┘            └────────────────────┘
```
- Se define una "caja" virtual delante de ti y la posición de la mano dentro de ella se lleva a la pantalla.
- Es lo que hacen airmouse y compañía. Funciona con **una webcam** y es preciso y estable.
- No es "apuntar" de verdad: es como un trackpad en el aire.

### B. Rayo absoluto (estilo Quest) — más natural, más difícil
```
     hombro ●───────── ✋ mano ─────────────► ● punto en la pantalla
     (MediaPipe Pose)  (MediaPipe Hands)        (intersección del rayo con el plano de la pantalla)
```
- El rayo se traza desde el hombro (o el ojo) pasando por la mano o el índice, y se corta con el plano de la pantalla.
- Hace falta la **posición 3D** del hombro y de la mano respecto a la pantalla. Una sola webcam da una profundidad **aproximada** (MediaPipe da coordenadas "world" en metros, relativas a la mano o al cuerpo) → el rayo tiembla y se desvía.
- Ventaja de partida: la webcam suele estar **encima de la pantalla**, así que el plano de la pantalla es casi conocido (se puede calibrar una vez apuntando a las 4 esquinas).
- Mejoras posibles: profundidad monocular (Depth Anything), **2 webcams en estéreo** o una cámara de profundidad barata.

## Gestos propuestos (inspirados en Quest y Vision Pro)

| Gesto | Acción |
|---|---|
| Pellizco índice-pulgar | Clic / tocar |
| Pellizco mantenido + mover | Arrastrar / seleccionar |
| Pellizco mantenido + subir/bajar | Scroll |
| Pellizco índice-corazón (o pulgar-corazón) | Clic derecho |
| Palma abierta mirando a la cámara 1 s | Menú / pausar el control |
| Dos manos con pellizco + separar | Zoom |
| Puño | Soltar / cancelar |

## Problemas conocidos y cómo resolverlos

| Problema | Solución |
|---|---|
| **Temblor del cursor** | Filtro 1€ (One Euro): suaviza cuando vas lento y responde rápido cuando vas rápido |
| **El cursor se mueve al pellizcar** (el gesto desplaza el índice) | Congelar o amortiguar el cursor durante el inicio del pellizco; usar como punto un landmark estable (nudillo del índice o centro de la palma) |
| **Clics involuntarios** ("Midas touch") | Histéresis (umbral para empezar el pellizco distinto del de soltarlo), tiempo mínimo, gesto de "activar/desactivar" |
| **Brazo cansado** ("gorilla arm") | Caja de interacción pequeña y cerca del cuerpo; ganancia no lineal tipo aceleración de ratón |
| **Luz y fondo** | MediaPipe va bien en interiores; mejor a contraluz evitado y cámara a ≥30 fps |
| **Latencia** | Cámara a 60 fps, procesar a resolución reducida, modelo *lite* de MediaPipe |

## Arquitectura propuesta (comparte la "capa de host" con la vía táctil)

```
webcam ──► MediaPipe Hands (+ Pose para el modo rayo)
        ──► motor de puntero  [modo caja | modo rayo]
        ──► filtro 1€
        ──► reconocedor de gestos (máquina de estados + histéresis)
        ──► inyección en el SO
              Linux:   uinput (ratón absoluto + multitáctil)
              Windows: SendInput / InjectSyncPointerInput
              macOS:   CGEvent (ratón)
        ──► overlay en pantalla (círculo del cursor que se cierra al pellizcar = feedback)
```

- El **overlay de feedback** es clave para la sensación tipo Quest: un círculo que se va cerrando según la fuerza del pellizco.
- La misma capa de inyección y overlay sirve después para la webcam táctil ([05-webcam.md](05-webcam.md)) y para el marco IR.

## Plan

1. **Spike G1 — modo caja (1–2 días):** Python + MediaPipe + filtro 1€ + pellizco con histéresis + uinput en Linux + overlay.
2. **Spike G2 — gestos:** arrastrar, scroll, clic derecho, pausa con la palma.
3. **Spike G3 — modo rayo:** Pose + Hands, calibración apuntando a las 4 esquinas, intersección rayo-plano. Medir el error en cm.
4. Valorar una 2.ª webcam (estéreo) si el rayo con una sola cámara es demasiado impreciso.

## Resultados del prototipo G1 (2026-11-04)

Probado en Ubuntu 26.04 (Wayland/GNOME), monitor 3440×1440 y webcam Logitech C925e. Código en `software/gestos/`.

| Problema observado | Causa (medida con datos grabados) | Solución aplicada |
|---|---|---|
| Solo 15 fps | En penumbra la webcam alarga la exposición y baja los fps | Desactivar la "prioridad de exposición" V4L2 al arrancar y restaurarla al salir → 30 fps |
| No detectaba algunos clics | Se pellizca contra la yema o el lateral del índice, no punta con punta; el 3D de MediaPipe es poco fiable (0,7 con los dedos juntos) | Distancia pulgar → último tramo del índice, medida en 2D; umbrales 0,40 / 0,55; 2 fotogramas de confirmación |
| Arrastres sin querer | Los pellizcos duran 0,4–2 s; el cursor volvía a moverse con el botón pulsado | Cursor clavado durante el clic hasta salir de un radio del 3 % del ancho ("touch slop") |
| Temblor | La caja amplifica unas 6 veces (576 px de cámara → 3440 px de pantalla) | Media de 4 nudillos + filtro 1€ más suave + zona muerta "con cuerda" (~20 px) → de 22×16 px a ~6×8 px con la mano quieta |
| Clics fantasma con la mano de canto o el dorso hacia la cámara | El pulgar y la punta del índice quedan tapados; en 2D parecen juntos y el 3D da los mismos valores que un pellizco real → **no separables con una sola cámara** | Clic solo con la palma hacia la cámara (normal 3D de la palma + izquierda/derecha + sentido de los nudillos), con histéresis y aviso en pantalla |

**Detalle importante:** al pasar a MediaPipe Tasks una imagen ya espejada, la etiqueta izquierda/derecha sale **invertida**, así que hay que darle la vuelta.

## Fuentes
- [Meta – Hand tracking interactions (Unity)](https://developers.meta.com/horizon/documentation/unity/unity-handtracking-interactions/)
- [Meta – Mobile hand tracking (native)](https://developers.meta.com/horizon/documentation/native/android/mobile-hand-tracking/)
- [UploadVR – Quest Interaction SDK](https://uploadvr.com/quest-interaction-sdk-tracked-keyboard-sdk/)
- [Ultraleap TouchFree – manual](https://docs.ultraleap.com/TouchFree/touchfree-user-manual/index.html) · [glosario](https://docs.ultraleap.com/TouchFree/touchfree-user-manual/technical-glossary.html) · [TouchFree Web Tooling](https://www.github.com/ultraleap/TouchFreeWebTooling)
- [Google – Project Gameface](https://developers.googleblog.com/en/project-gameface-makes-gaming-accessible-to-everyone/)
- [airmouse](https://github.com/Rcidshacker/airmouse) · [HandGesture-Mouse](https://github.com/murfidya/HandGesture-Mouse) · [pointer](https://github.com/slastra/pointer) · [openhandtrack](https://pypi.org/project/openhandtrack/) · [hand-playground](https://github.com/DareDev256/hand-playground)
