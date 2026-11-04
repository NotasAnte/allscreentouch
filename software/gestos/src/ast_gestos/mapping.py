"""Caja de interacción: lleva la posición de la mano en la imagen a la pantalla."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass
class InteractionBox:
    """Rectángulo (normalizado 0..1 en la imagen ya espejada) que equivale a toda la pantalla.

    El alto se calcula para que la caja tenga la misma proporción que la pantalla,
    así un movimiento horizontal y uno vertical de la mano recorren lo mismo.
    """

    cx: float
    cy: float
    w: float
    h: float

    @classmethod
    def for_screen(cls, width_frac: float, frame_w: int, frame_h: int,
                   screen_w: int, screen_h: int, cx: float = 0.5, cy: float = 0.45) -> "InteractionBox":
        frame_aspect = frame_w / frame_h
        screen_aspect = screen_w / screen_h
        h = width_frac * frame_aspect / screen_aspect
        return cls(cx=cx, cy=cy, w=width_frac, h=min(h, 0.95))

    @property
    def left(self) -> float:
        return self.cx - self.w / 2

    @property
    def top(self) -> float:
        return self.cy - self.h / 2

    def to_screen(self, x: float, y: float, screen_w: int, screen_h: int) -> tuple[float, float]:
        u = (x - self.left) / self.w
        v = (y - self.top) / self.h
        u = min(max(u, 0.0), 1.0)
        v = min(max(v, 0.0), 1.0)
        return u * (screen_w - 1), v * (screen_h - 1)


class StickyCursor:
    """Zona muerta que "arrastra": elimina el temblor con la mano quieta.

    El cursor no se mueve mientras la posición filtrada esté dentro de un radio
    `radius_px`. Si sale, el cursor la sigue quedándose a `radius_px` por detrás
    (como tirar de una cuerda), así que no hay saltos ni retardo apreciable.
    """

    def __init__(self, radius_px: float) -> None:
        self.radius_px = radius_px
        self._pos: tuple[float, float] | None = None

    def reset(self) -> None:
        self._pos = None

    def update(self, x: float, y: float) -> tuple[float, float]:
        if self._pos is None or self.radius_px <= 0:
            self._pos = (x, y)
            return self._pos
        cx, cy = self._pos
        dx, dy = x - cx, y - cy
        d = (dx * dx + dy * dy) ** 0.5
        if d > self.radius_px:
            k = (d - self.radius_px) / d
            self._pos = (cx + dx * k, cy + dy * k)
        return self._pos


class DragGate:
    """Distingue clic de arrastre, como el "touch slop" de los móviles.

    Al pulsar, el cursor se queda clavado en el punto del clic. Solo si la mano
    se aleja más de `slop_px` se considera arrastre y el cursor vuelve a seguirla.
    Así un pellizco largo o con algo de temblor sigue siendo un clic.
    """

    def __init__(self, slop_px: float) -> None:
        self.slop_px = slop_px
        self.anchor: tuple[float, float] | None = None
        self.dragging = False

    def press(self, anchor: tuple[float, float]) -> None:
        self.anchor = anchor
        self.dragging = False

    def release(self) -> None:
        self.anchor = None
        self.dragging = False

    def position(self, x: float, y: float) -> tuple[float, float]:
        if self.anchor is None or self.dragging:
            return x, y
        ax, ay = self.anchor
        if ((x - ax) ** 2 + (y - ay) ** 2) ** 0.5 > self.slop_px:
            self.dragging = True
            return x, y
        return self.anchor


class PositionHistory:
    """Guarda posiciones recientes para "volver atrás" al empezar un clic.

    Al cerrar el pellizco la mano se desplaza un poco; usamos dónde apuntaba
    justo antes para que el clic caiga donde querías.
    """

    def __init__(self, max_age: float = 0.5) -> None:
        self.max_age = max_age
        self._items: deque[tuple[float, float, float]] = deque()

    def add(self, t: float, x: float, y: float) -> None:
        self._items.append((t, x, y))
        while self._items and t - self._items[0][0] > self.max_age:
            self._items.popleft()

    def at(self, t: float) -> tuple[float, float] | None:
        """Posición más reciente con marca de tiempo <= t."""
        best = None
        for ti, x, y in self._items:
            if ti <= t:
                best = (x, y)
            else:
                break
        return best

    def clear(self) -> None:
        self._items.clear()
