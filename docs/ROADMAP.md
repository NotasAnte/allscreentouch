# Roadmap

## Fase 0 — Investigación ✅
- [x] Tecnologías, mercado, open source previo, propuesta.

## Fase 1 — Decisiones y entorno
- [ ] Confirmar pantallas objetivo (tallas, SO) y requisitos (nº de dedos, presupuesto por unidad).
- [ ] Elegir MCU (RP2040/RP2350 vs ESP32-S3) y licencias.
- [ ] Inicializar repo git, estructura `hardware/`, `firmware/`, `software/`, `docs/`.
- [ ] (Opcional) Comprar un marco IR chino barato como referencia y desmontarlo.

## Fase 2 — MVP de software (sin hardware)
- [ ] Inyección de toques en el SO: Linux (`uinput`), Windows (`InjectTouchInput`).
- [ ] Spike A: reflejo tipo Sistine en portátil (Python 3 + OpenCV + uinput). Ver [05-webcam.md](investigacion/05-webcam.md).
- [ ] Spike B: cámara rasante en esquina, 1 dedo.
- [ ] Spike C: 2 cámaras rasantes + triangulación.
- [ ] Calibración automática con marcadores ArUco mostrados en pantalla.
- [x] Spike G1 (`software/gestos/`, probado 2026-11-04): control por gestos en modo caja (MediaPipe + filtro 1€ + pellizco + uinput). Pendiente: overlay en pantalla con el círculo de feedback. Ver [06-gestos.md](investigacion/06-gestos.md).
- [ ] Spike G2: arrastrar, scroll, clic derecho y pausa con la palma.
- [ ] Spike G3: modo rayo (hombro → mano → pantalla) con calibración apuntando a las 4 esquinas.
- [ ] Mapeo multimonitor y calibración de 4 puntos.

## Fase 3 — Prototipo de hardware en protoboard
- [ ] 8 LEDs + 8 receptores + RP2040: escaneo, lectura diferencial, detección de 1 dedo.
- [ ] Firmware USB HID digitizer (1 → 5 → 10 contactos) probado en Windows y Linux.
- [ ] Escaneo diagonal y multitáctil.

## Fase 4 — PCBs modulares v1
- [ ] Diseño KiCad: segmento TX, segmento RX, controladora.
- [ ] Carcasa paramétrica (OpenSCAD/CadQuery) por tamaño.
- [ ] Primer marco completo para un monitor de 24".

## Fase 5 — Producto abierto
- [ ] Configurador web (WebUSB/WebSerial) + actualización de firmware.
- [ ] Guía de fabricación (BOM, pedido JLCPCB, montaje).
- [ ] Driver/daemon para macOS, salida TUIO, BLE.
