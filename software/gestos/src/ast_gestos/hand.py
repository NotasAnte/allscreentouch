"""Detección de la mano con MediaPipe Hand Landmarker."""

from __future__ import annotations

import hashlib
import math
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision

# Versión fijada + hash: el modelo lo procesa código nativo de MediaPipe, así que
# no usamos "latest" y comprobamos que el archivo es exactamente el esperado.
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_SHA256 = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
MODEL_PATH = Path.home() / ".cache" / "allscreentouch" / "hand_landmarker.task"

# Índices de los 21 puntos de MediaPipe
WRIST = 0
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_TIP = 8
MIDDLE_MCP = 9
RING_MCP = 13
PINKY_MCP = 17
KNUCKLES = (INDEX_MCP, MIDDLE_MCP, RING_MCP, PINKY_MCP)

CONNECTIONS = [(c.start, c.end) for c in vision.HandLandmarksConnections.HAND_CONNECTIONS]


@dataclass
class HandFrame:
    points: list[tuple[float, float]]  # 21 puntos normalizados (0..1) en la imagen
    pointer: tuple[float, float]       # punto que mueve el cursor (normalizado)
    pinch_ratio: float                 # métrica final de pellizco
    ratio_3d: float                    # distancia pulgar-índice / palma, en coordenadas "world"
    ratio_2d: float                    # lo mismo, medido sobre la imagen
    facing: float                      # 0 = mano de canto a la cámara, 1 = de frente (palma o dorso)
    palm_toward_camera: bool           # True = se ve la palma; False = se ve el dorso
    handedness: str                    # "Left" / "Right" (mano real; la imagen ya va espejada)


# Orientación de la palma: |cos| del ángulo entre su normal 3D y el eje de la cámara.
# 1 = palma (o dorso) mirando a la cámara, 0 = mano de canto.
FACING_SIDE = 0.45   # cos ≈ 0,45 → ~63° girada
FACING_FRONT = 0.75  # cos ≈ 0,75 → ~41° girada


def palm_alignment(wrist, index_mcp, pinky_mcp) -> float:
    """|componente z| de la normal de la palma (triángulo muñeca-índice-meñique), en 0..1."""
    a = [i - w for i, w in zip(index_mcp, wrist)]
    b = [p - w for p, w in zip(pinky_mcp, wrist)]
    n = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    norm = math.sqrt(sum(c * c for c in n))
    return 0.0 if norm == 0 else abs(n[2]) / norm


def facing_weight(alignment: float) -> float:
    """0 si la mano está de canto, 1 si está de frente, transición lineal entre medias."""
    w = (alignment - FACING_SIDE) / (FACING_FRONT - FACING_SIDE)
    return min(max(w, 0.0), 1.0)


def palm_toward_camera(handedness: str, wrist, index_mcp, pinky_mcp) -> bool:
    """¿Se ve la palma (True) o el dorso (False)? Puntos 2D de la imagen ESPEJADA (y hacia abajo).

    Para una mano derecha con la palma hacia la cámara y los dedos hacia arriba, en la imagen
    espejada el nudillo del índice queda a la izquierda del meñique: el producto vectorial
    (índice − muñeca) × (meñique − muñeca) es positivo. Con el dorso, o con la mano izquierda,
    cambia de signo. Usar la muñeca como origen lo hace válido aunque la mano esté girada en el plano.
    """
    ax, ay = index_mcp[0] - wrist[0], index_mcp[1] - wrist[1]
    bx, by = pinky_mcp[0] - wrist[0], pinky_mcp[1] - wrist[1]
    cross = ax * by - ay * bx
    return cross > 0 if handedness == "Right" else cross < 0


def combine_pinch(ratio_2d: float, ratio_3d: float, facing: float) -> float:
    """De frente manda el 2D (fiable). De canto el 2D da falsos pellizcos (el pulgar queda
    detrás del índice), así que exigimos que el 3D también lo vea cerrado: max(2D, 3D)."""
    return facing * ratio_2d + (1.0 - facing) * max(ratio_2d, ratio_3d)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_model(path: Path = MODEL_PATH) -> Path:
    if path.exists() and _sha256(path) == MODEL_SHA256:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Descargando modelo de mano en {path} ...")
    tmp = path.with_suffix(".part")
    urllib.request.urlretrieve(MODEL_URL, tmp)
    digest = _sha256(tmp)
    if digest != MODEL_SHA256:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"El modelo descargado no coincide con el hash esperado ({digest})")
    tmp.replace(path)
    return path


INDEX_DIP = 7


def _dist(a, b) -> float:
    return math.dist((a.x, a.y, a.z), (b.x, b.y, b.z))


def point_segment_dist(p, a, b) -> float:
    """Distancia de p al segmento a-b (tuplas de igual dimensión)."""
    ab = [bi - ai for ai, bi in zip(a, b)]
    ap = [pi - ai for ai, pi in zip(a, p)]
    denom = sum(c * c for c in ab)
    t = 0.0 if denom == 0 else max(0.0, min(1.0, sum(x * y for x, y in zip(ap, ab)) / denom))
    closest = [ai + t * c for ai, c in zip(a, ab)]
    return math.dist(p, closest)


class HandTracker:
    def __init__(self, model_path: Path | None = None) -> None:
        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path or ensure_model())),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._last_ts = -1

    def close(self) -> None:
        self._landmarker.close()

    def process(self, rgb: np.ndarray, timestamp_ms: int) -> HandFrame | None:
        frame_h, frame_w = rgb.shape[:2]
        # MediaPipe exige marcas de tiempo estrictamente crecientes
        timestamp_ms = max(timestamp_ms, self._last_ts + 1)
        self._last_ts = timestamp_ms
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self._landmarker.detect_for_video(image, timestamp_ms)
        if not result.hand_landmarks:
            return None

        lm = result.hand_landmarks[0]
        # Comprobado con pruebas reales: con la imagen ya espejada, MediaPipe Tasks devuelve la
        # etiqueta invertida (una mano derecha sale como "Left"), así que la damos la vuelta.
        raw = result.handedness[0][0].category_name if result.handedness else "Left"
        handedness = "Left" if raw == "Right" else "Right"
        # Coordenadas "world" (metros, centradas en la mano): estables frente a la distancia
        world = result.hand_world_landmarks[0] if result.hand_world_landmarks else lm

        # Distancia del pulgar al último tramo del índice (yema incluida), no solo punta con punta:
        # mucha gente pellizca contra la yema o el lateral del índice.
        def w3(i: int) -> tuple[float, float, float]:
            return world[i].x, world[i].y, world[i].z

        palm = max(_dist(world[WRIST], world[MIDDLE_MCP]), 1e-6)
        ratio_3d = point_segment_dist(w3(THUMB_TIP), w3(INDEX_DIP), w3(INDEX_TIP)) / palm

        # En la imagen (píxeles reales, sin deformar por el aspecto). Con datos reales es
        # mucho más fiable que el 3D, cuya profundidad estimada con una sola cámara es ruidosa.
        def px(i: int) -> tuple[float, float]:
            return lm[i].x * frame_w, lm[i].y * frame_h

        palm_2d = max(math.dist(px(WRIST), px(MIDDLE_MCP)), 1e-6)
        ratio_2d = point_segment_dist(px(THUMB_TIP), px(INDEX_DIP), px(INDEX_TIP)) / palm_2d
        # Las coordenadas "world" conservan la orientación respecto a la cámara (aunque la
        # profundidad absoluta sea ruidosa), así que sirven para saber si la mano está de canto.
        facing = facing_weight(palm_alignment(w3(WRIST), w3(INDEX_MCP), w3(PINKY_MCP)))

        # Media de los 4 nudillos: apenas se mueven al pellizcar y, al promediar,
        # el ruido de cada punto se compensa (menos temblor que un solo landmark).
        knuckle_x = sum(lm[i].x for i in KNUCKLES) / len(KNUCKLES)
        knuckle_y = sum(lm[i].y for i in KNUCKLES) / len(KNUCKLES)
        return HandFrame(
            points=[(p.x, p.y) for p in lm],
            pointer=(knuckle_x, knuckle_y),
            pinch_ratio=combine_pinch(ratio_2d, ratio_3d, facing),
            ratio_3d=ratio_3d,
            ratio_2d=ratio_2d,
            facing=facing,
            palm_toward_camera=palm_toward_camera(handedness, px(WRIST), px(INDEX_MCP), px(PINKY_MCP)),
            handedness=handedness,
        )
