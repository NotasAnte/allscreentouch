# 04 · Propuesta: qué construir

## Recomendación

**Construir un marco táctil IR modular, open hardware + open firmware, que se presenta como USB HID multitáctil estándar (sin drivers).**

Razones:
- Es la única tecnología que es a la vez **barata, precisa, multitáctil, válida para cualquier pantalla** y **reproducible** por cualquiera con un pedido de PCBs (JLCPCB/PCBWay ensamblan los componentes SMD).
- El mercado demuestra que funciona (marcos chinos baratos), pero todos son **cerrados y de talla fija** → nuestra diferencia es: **abierto + modular + configurable**.

## Concepto: "segmentos encadenables"

```
  ┌──[TX]──[TX]──[TX]──[TX]──[CTRL]┐   TX = segmento emisor (LEDs IR)
  │                                │   RX = segmento receptor (fotodiodos)
 [TX]                            [RX]  CTRL = controlador (MCU + USB-C)
 [TX]        PANTALLA            [RX]
  │                                │
  └──[RX]──[RX]──[RX]──[RX]────────┘
```

- PCBs **segmento** de longitud fija (p. ej. 50 mm o 100 mm) con N LEDs o N receptores a paso de ~4–5 mm.
- Se encadenan con conectores/FFC → cualquier tamaño (portátil 13" hasta TV 65").
- Una placa **controladora** única.
- **Esquinas y carcasa** en perfil de aluminio o impresión 3D (STL paramétrico generado por tamaño).
- El tamaño real (nº de segmentos) se detecta al arrancar o se configura una vez.

## Arquitectura

### Hardware (borrador, a validar en prototipo)
| Bloque | Opción inicial | Alternativa |
|---|---|---|
| MCU | **RP2040 / RP2350** (barato, PIO para escaneo rápido, USB nativo, TinyUSB) | ESP32-S3 (añade BLE/Wi-Fi) |
| Emisores | LED IR 850/940 nm SMD | — |
| Receptores | Fototransistor/fotodiodo IR SMD con filtro de luz visible | — |
| Drivers emisores | Registro de desplazamiento de corriente constante (TLC5916/STP16) | Multiplexor analógico |
| Lectura receptores | Mux analógico (74HC4067) → ADC del MCU | ADC externo rápido |
| Conexión | USB-C (HID) | BLE HID (fase posterior) |

### Firmware
1. **Escaneo**: LED pulsado + lectura diferencial (encendido − apagado) para rechazar luz ambiente.
2. **Escaneo diagonal** (cada LED leído por varios receptores) → multitáctil real y eliminación de fantasmas.
3. **Detección**: mapa de sombras → blobs → centroides con interpolación sub-paso.
4. **Tracking**: asignación de IDs entre fotogramas, filtro (1€ filter / Kalman), palm rejection.
5. **USB HID digitizer** multitáctil (5–10 contactos) compatible con Windows, Linux, Android, ChromeOS.
6. Interfaz de configuración por **USB serial/WebUSB** (calibración, nº de segmentos, sensibilidad).

### Software de escritorio (abierto)
- **Configurador web** (WebUSB/WebSerial, sin instalar nada): calibración por 4 puntos, test de haces, actualización de firmware.
- **Mapeo multimonitor**: asignar el digitalizador a la pantalla correcta (xinput/libinput en Linux, ajuste de Tablet PC en Windows).
- **macOS**: driver/daemon abierto que traduzca toques a eventos (no hay soporte nativo).
- Salida **TUIO** opcional para instalaciones creativas.

## Plan B / línea paralela: cámaras en esquinas
Si el marco IR resulta demasiado caro en tallas grandes, investigar 2–3 cámaras IR de alta tasa en esquinas + retrorreflectante. Coste casi fijo por tamaño. Se deja como experimento tras el MVP.

## MVP por software (empezar ya, sin hardware)
- App con webcam (estilo Sistine mejorado con MediaPipe) que inyecte toques en el SO.
- Objetivo **no** es el producto final, sino construir y probar **la capa de host** (inyección de eventos, mapeo multimonitor, configurador) que luego reutilizará el marco IR.

## Coste estimado del marco DIY (24", estimación sin validar)
| Partida | Estimación |
|---|---|
| ~170 LEDs IR + ~170 receptores (paso 5 mm) | 15–25 € |
| PCBs segmentos + controladora (ensamblado JLC, lote pequeño) | 20–35 € |
| MCU RP2040 + USB-C + pasivos | 5 € |
| Carcasa (impresión 3D / perfil aluminio) | 5–15 € |
| **Total** | **~45–80 €** |

Comparable con un marco chino de reventa, pero **abierto, reparable y de cualquier tamaño**.

## Licencias propuestas
- Hardware: **CERN-OHL-S v2**
- Firmware y software: **MIT** o **Apache-2.0** (o GPL-3.0 si se quiere copyleft fuerte)
- Documentación: **CC BY-SA 4.0**

## Riesgos
- Luz solar directa satura receptores → modulación + filtros.
- Velocidad de escaneo con pantallas grandes (cientos de haces × diagonales) → PIO/DMA, escaneo por zonas.
- Montaje mecánico: el marco debe quedar plano y a 1–3 mm del cristal.
- macOS sin soporte nativo táctil.
