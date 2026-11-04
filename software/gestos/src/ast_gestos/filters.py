"""Filtros de suavizado y detección con histéresis."""

from __future__ import annotations

import math


class OneEuroFilter:
    """Filtro 1€ (Casiez et al., 2012).

    Suaviza mucho cuando la señal va lenta (quita temblor) y poco cuando va
    rápida (quita retardo). `min_cutoff` controla el temblor en reposo y
    `beta` la reactividad en movimiento.
    """

    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.007, d_cutoff: float = 1.0) -> None:
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self._x_prev: float | None = None
        self._dx_prev = 0.0
        self._t_prev: float | None = None

    @staticmethod
    def _alpha(cutoff: float, dt: float) -> float:
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def reset(self) -> None:
        self._x_prev = None
        self._t_prev = None
        self._dx_prev = 0.0

    def __call__(self, x: float, t: float) -> float:
        if self._x_prev is None or self._t_prev is None or t <= self._t_prev:
            self._x_prev, self._t_prev = x, t
            return x
        dt = t - self._t_prev
        dx = (x - self._x_prev) / dt
        a_d = self._alpha(self.d_cutoff, dt)
        dx_hat = a_d * dx + (1.0 - a_d) * self._dx_prev
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = self._alpha(cutoff, dt)
        x_hat = a * x + (1.0 - a) * self._x_prev
        self._x_prev, self._dx_prev, self._t_prev = x_hat, dx_hat, t
        return x_hat


class HysteresisGate:
    """Interruptor con dos umbrales: se cierra al bajar de `low` y se abre al superar `high`.

    Se usa para permitir el clic solo con la palma hacia la cámara sin que parpadee
    cuando la mano está justo en el límite.
    """

    def __init__(self, low: float, high: float, initial: bool = True) -> None:
        if high <= low:
            raise ValueError("high debe ser mayor que low")
        self.low, self.high = low, high
        self.open = initial

    def update(self, value: float) -> bool:
        if self.open and value < self.low:
            self.open = False
        elif not self.open and value > self.high:
            self.open = True
        return self.open


class PinchDetector:
    """Pellizco índice-pulgar con histéresis.

    Se activa cuando la distancia baja de `on_ratio` y solo se suelta cuando
    supera `off_ratio` (mayor), para evitar clics dobles por temblor.
    La distancia va normalizada por el tamaño de la mano, así que no depende
    de lo lejos que estés de la cámara.
    """

    def __init__(self, on_ratio: float = 0.40, off_ratio: float = 0.55, confirm_frames: int = 2) -> None:
        if off_ratio <= on_ratio:
            raise ValueError("off_ratio debe ser mayor que on_ratio")
        self.on_ratio = on_ratio
        self.off_ratio = off_ratio
        self.confirm_frames = max(1, confirm_frames)
        self.pinched = False
        self._streak = 0

    def reset(self) -> None:
        self.pinched = False
        self._streak = 0

    def update(self, ratio: float) -> bool:
        """Cambia de estado solo tras `confirm_frames` fotogramas seguidos (evita parpadeos)."""
        wants_change = ratio > self.off_ratio if self.pinched else ratio < self.on_ratio
        self._streak = self._streak + 1 if wants_change else 0
        if self._streak >= self.confirm_frames:
            self.pinched = not self.pinched
            self._streak = 0
        return self.pinched
