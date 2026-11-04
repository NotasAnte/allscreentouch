# 03 · Proyectos open source y DIY existentes

## Hardware de marco / superficie

| Proyecto | Año | Técnica | Estado | Qué aprovechar |
|---|---|---|---|---|
| **Magic Frame** (Jean Perardel) — [hackaday.io](https://hackaday.io/project/27155-magic-frame-turn-everything-into-a-touch-area), [GitHub](https://github.com/jeanot1314/Magic_Frame) | 2017 | 96 LEDs IR + sensores CIS de escáner, Teensy 3.6, triangulación de sombras; marco imprimible en 3D por módulos de 13 cm | Completado, sin actualizar ~6 años, **sin licencia declarada** | Idea de **elementos modulares imprimibles**, driver STP16CP05, salida ratón/serial, feedback con WS2812 |
| **Pizarra IR gigante** (Hackaday 2017) | 2017 | 144 pares LED/fototransistor, multiplexores 4051, 2 Arduino Nano | Prototipo | Esquema de multiplexado simple |
| **Panel multitáctil LED** (Amanda Ghassaei) | ~2012 | 64 pares LED blanco + fototransistor IR bajo cristal, tabiques de aluminio | Proyecto artístico | Celdas unitarias repetibles |
| **NUI Group – Open Source IR Frame** (GSoC 2012) | 2012 | Propuesta de marco IR escalable | Comunidad inactiva | Contexto histórico |
| **spritesmods – CCD lineal** | 2001 | Sensor CCD de escáner como táctil | Histórico | — |

## Software de visión / multitáctil

| Proyecto | Técnica | Estado | Notas |
|---|---|---|---|
| **Project Sistine** ([bijection/sistine](https://github.com/bijection/sistine), MIT, ~3,2k ⭐) | Webcam + espejo, OpenCV | PoC, Python 2 + macOS | Autores: con cámara de más resolución y espejo curvo sería un táctil barato práctico |
| **Windows-Touch** ([ashishgupta1350](https://github.com/ashishgupta1350/Windows-Touch)) | Port de Sistine a Windows | PoC | opencv-python + pyautogui |
| **manitas** ([nacmartin](https://github.com/nacmartin/manitas)) | MediaPipe en navegador → eventos tipo touch | 2023 | Evento "airfinger" |
| **handTrack** / **virtual-gesture-mouse** | MediaPipe + PyAutoGUI, pellizco = clic | 2025 | Gestos, no tacto de superficie |
| **Touchlib / Community Core Vision (CCV)** / **reacTIVision** | Visión para mesas FTIR/DI | Históricos | Origen del protocolo **TUIO** |
| **libfreenect2** | Driver abierto Kinect v2 | Activo | Para variantes con profundidad |
| **SlamtecCHOP** | Plugin TouchDesigner para RPLIDAR | — | Paredes interactivas |

## Investigación académica

- **WorldKit** (CMU, 2013): Kinect + proyector, "pintar" controles en cualquier superficie.
- **OmniTouch** (Microsoft Research + CMU, 2011): proyector y cámara de profundidad al hombro.
- **LightSpace** (Microsoft Research): calibración cámara-proyector, superficies no planas.

## Estándares y piezas reutilizables

- **USB HID Digitizer (Usage Page 0x0D, Touch Screen 0x04)**: el descriptor "multi-touch" que Windows reconoce sin drivers (Windows Touch / Precision Touch para pantallas) y Linux con `hid-multitouch`. Android y ChromeOS también.
- **TinyUSB**: pila USB para RP2040/ESP32-S2/S3/STM32; tiene ejemplos HID compuestos que sirven de base para un digitalizador.
- **TUIO**: protocolo abierto (OSC/UDP) para enviar toques a apps creativas (TouchDesigner, Unity, Processing).
- **Linux uinput** / **Windows InjectTouchInput** / **macOS (sin API táctil pública)**: para el MVP por software.

## Conclusión

No hay ningún proyecto abierto **actual, modular, documentado y con firmware HID estándar**. Las piezas existen (TinyUSB, HID digitizer, ideas de Magic Frame), pero nadie las ha juntado en un producto reproducible. Ese es el hueco de AllScreenTouch.
