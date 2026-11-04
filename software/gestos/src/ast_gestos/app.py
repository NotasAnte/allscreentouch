"""Bucle principal: webcam → mano → cursor + clic."""

from __future__ import annotations

import argparse
import csv
import re
import signal
import subprocess
import sys
import time

import cv2

from .camera import ExposurePriorityOff
from .filters import HysteresisGate, OneEuroFilter, PinchDetector
from .hand import CONNECTIONS, HandTracker
from .injector import NullPointer, VirtualPointer
from .mapping import DragGate, InteractionBox, PositionHistory, StickyCursor


def detect_screen_size() -> tuple[int, int]:
    """Tamaño del escritorio completo (todas las pantallas). Por defecto 1920x1080."""
    try:
        out = subprocess.run(["xrandr", "--query"], capture_output=True, text=True, timeout=3).stdout
        m = re.search(r"current (\d+) x (\d+)", out)
        if m:
            return int(m.group(1)), int(m.group(2))
    except (OSError, subprocess.SubprocessError):
        pass
    return 1920, 1080


def parse_size(s: str) -> tuple[int, int]:
    w, h = s.lower().split("x")
    return int(w), int(h)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ast-gestos",
        description="Apunta con la mano y pellizca (índice + pulgar) para hacer clic.",
    )
    p.add_argument("--camera", type=int, default=0, help="índice de la webcam (/dev/videoN)")
    p.add_argument("--camera-size", type=parse_size, default=(1280, 720), help="resolución de captura, p. ej. 1280x720")
    p.add_argument("--screen", type=parse_size, default=None, help="tamaño del escritorio, p. ej. 3440x1440 (auto)")
    p.add_argument("--box-width", type=float, default=0.45,
                   help="ancho de la caja de interacción como fracción de la imagen (menos = menos brazo, más sensible)")
    p.add_argument("--min-cutoff", type=float, default=0.4, help="filtro 1€: menos = menos temblor en reposo")
    p.add_argument("--beta", type=float, default=0.01, help="filtro 1€: más = menos retardo al mover rápido")
    p.add_argument("--pinch-on", type=float, default=0.40, help="umbral para empezar el pellizco")
    p.add_argument("--pinch-off", type=float, default=0.55, help="umbral para soltar el pellizco")
    p.add_argument("--deadzone", type=float, default=0.006,
                   help="radio de la zona muerta contra el temblor (fracción del ancho de pantalla; 0 = sin zona muerta)")
    p.add_argument("--facing-min", type=float, default=0.5,
                   help="cuánto de frente debe estar la palma para permitir el clic (0 = de canto, 1 = de frente)")
    p.add_argument("--drag-slop", type=float, default=0.03,
                   help="cuánto hay que mover la mano pellizcando para que sea arrastre "
                        "(fracción del ancho de pantalla); menos = arrastra antes")
    p.add_argument("--no-preview", action="store_true", help="no mostrar la ventana de la cámara")
    p.add_argument("--record", metavar="CSV", default=None,
                   help="guardar por fotograma los valores del pellizco (para ajustar umbrales)")
    p.add_argument("--dry-run", action="store_true", help="no mover el ratón real (solo vista previa)")
    return p


def open_camera(index: int, size: tuple[int, int]) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not cap.isOpened():
        sys.exit(f"No se pudo abrir la webcam {index}")
    return cap


def draw_preview(frame, box: InteractionBox, hand, pinched: bool, active: bool, fps: float,
                 click_ok: bool = True) -> None:
    h, w = frame.shape[:2]
    color_box = (0, 200, 0) if active else (0, 140, 255)
    cv2.rectangle(frame,
                  (int(box.left * w), int(box.top * h)),
                  (int((box.left + box.w) * w), int((box.top + box.h) * h)),
                  color_box, 2)
    if hand is not None:
        pts = [(int(x * w), int(y * h)) for x, y in hand.points]
        for a, b in CONNECTIONS:
            cv2.line(frame, pts[a], pts[b], (200, 200, 200), 1)
        px, py = int(hand.pointer[0] * w), int(hand.pointer[1] * h)
        cv2.circle(frame, (px, py), 12 if pinched else 8, (0, 0, 255) if pinched else (255, 160, 0), -1)
        cv2.putText(frame, f"pinch {hand.pinch_ratio:.2f} (2D {hand.ratio_2d:.2f} / 3D {hand.ratio_3d:.2f})  frente {hand.facing:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        lado = "PALMA" if hand.palm_toward_camera else "DORSO"
        cv2.putText(frame, f"{'derecha' if hand.handedness == 'Right' else 'izquierda'} - {lado}",
                    (10, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        if not click_ok:
            motivo = "MANO DE CANTO" if hand.palm_toward_camera else "DORSO HACIA LA CAMARA"
            cv2.putText(frame, f"{motivo}: muestra la palma para hacer clic",
                        (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 140, 255), 2)
    estado = "ACTIVO" if active else "PAUSA (p)"
    cv2.putText(frame, f"{estado}  {fps:4.1f} fps  [p] pausa  [q] salir", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_box, 2)


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    screen_w, screen_h = args.screen or detect_screen_size()

    cap = open_camera(args.camera, args.camera_size)
    exposure = ExposurePriorityOff(args.camera)
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    box = InteractionBox.for_screen(args.box_width, frame_w, frame_h, screen_w, screen_h)

    pointer = NullPointer(screen_w, screen_h) if args.dry_run else VirtualPointer(screen_w, screen_h)
    tracker = HandTracker()
    fx = OneEuroFilter(args.min_cutoff, args.beta)
    fy = OneEuroFilter(args.min_cutoff, args.beta)
    pinch = PinchDetector(args.pinch_on, args.pinch_off)
    history = PositionHistory()
    drag = DragGate(args.drag_slop * screen_w)
    sticky = StickyCursor(args.deadzone * screen_w)
    # Con la mano de canto una sola cámara no distingue un pellizco real de uno fantasma
    # (el pulgar queda detrás del índice), así que ahí no se permite hacer clic.
    click_gate = HysteresisGate(low=args.facing_min - 0.1, high=args.facing_min + 0.1)

    LOOKBACK = 0.10   # s: al pellizcar, usar dónde apuntabas hace 100 ms
    LOST_FRAMES = 6   # fotogramas sin mano antes de soltar el clic

    print(f"Pantalla {screen_w}x{screen_h} · cámara {frame_w}x{frame_h} · "
          f"{'DRY-RUN' if args.dry_run else 'ratón virtual activo'}")
    print("Apunta con la mano; junta índice y pulgar para hacer clic. Ctrl+C o [q] para salir.")

    # Que "kill"/TaskStop también pase por el finally (restaurar cámara, soltar clic)
    def _on_term(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, _on_term)

    rec_file = open(args.record, "w", newline="") if args.record else None
    rec = csv.writer(rec_file) if rec_file else None
    if rec:
        rec.writerow(["t", "hand", "ratio_3d", "ratio_2d", "facing", "pinch_ratio", "pinched", "raw_x", "raw_y", "x", "y", "click_ok", "palm", "hand_side"])

    active = True
    was_pinched = False
    lost = 0
    fps = 0.0
    t_prev = time.monotonic()
    t0 = t_prev

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Fallo leyendo la webcam", file=sys.stderr)
                break
            t = time.monotonic()
            fps = 0.9 * fps + 0.1 * (1.0 / max(t - t_prev, 1e-3))
            t_prev = t

            frame = cv2.flip(frame, 1)  # espejo: mueves la mano a la derecha → cursor a la derecha
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand = tracker.process(rgb, int((t - t0) * 1000))

            pinched = False
            click_ok = True
            if hand is not None:
                lost = 0
                sx, sy = box.to_screen(*hand.pointer, screen_w, screen_h)
                x, y = sticky.update(fx(sx, t), fy(sy, t))
                history.add(t, x, y)
                # Clic solo con la PALMA hacia la cámara: de canto o con el dorso, el pulgar y la
                # punta del índice quedan tapados y MediaPipe se inventa su posición.
                click_ok = click_gate.update(hand.facing if hand.palm_toward_camera else 0.0)
                # De canto se trata como "dedos abiertos": no empieza clic y suelta el que hubiera
                pinched = pinch.update(hand.pinch_ratio if click_ok else 1.0)
                if rec:
                    rec.writerow([f"{t - t0:.3f}", 1, f"{hand.ratio_3d:.3f}", f"{hand.ratio_2d:.3f}",
                                  f"{hand.facing:.3f}", f"{hand.pinch_ratio:.3f}", int(pinched),
                                  f"{sx:.1f}", f"{sy:.1f}", f"{x:.1f}", f"{y:.1f}", int(click_ok),
                                  int(hand.palm_toward_camera), hand.handedness])

                if active:
                    if pinched and not was_pinched:
                        anchor = history.at(t - LOOKBACK) or (x, y)
                        drag.press(anchor)
                        pointer.move(*anchor)
                        pointer.left(True)
                    elif not pinched and was_pinched:
                        pointer.left(False)
                        drag.release()
                    pointer.move(*drag.position(x, y))
                was_pinched = pinched
            else:
                if rec:
                    rec.writerow([f"{t - t0:.3f}", 0, "", "", "", "", 0, "", "", "", "", "", "", ""])
                lost += 1
                if lost >= LOST_FRAMES:
                    pointer.left(False)
                    fx.reset(); fy.reset(); sticky.reset(); pinch.reset(); history.clear(); drag.release()
                    was_pinched = False

            if not args.no_preview:
                draw_preview(frame, box, hand, pinched, active, fps, click_ok)
                cv2.imshow("AllScreenTouch · gestos", frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    break
                if key == ord("p"):
                    active = not active
                    pointer.left(False)
                    drag.release()
                    was_pinched = False
    except KeyboardInterrupt:
        pass
    finally:
        if rec_file:
            rec_file.close()
        pointer.close()
        tracker.close()
        exposure.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
