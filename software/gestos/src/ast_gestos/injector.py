"""Ratón absoluto virtual vía uinput (funciona en Wayland y X11)."""

from __future__ import annotations

from evdev import AbsInfo, UInput
from evdev import ecodes as e


class VirtualPointer:
    """Dispositivo tipo "tableta absoluta" (como el de QEMU): X/Y absolutos + botones.

    libinput lo trata como un puntero absoluto que cubre todo el escritorio.
    """

    def __init__(self, width: int, height: int, name: str = "AllScreenTouch Gestos") -> None:
        self.width = width
        self.height = height
        caps = {
            e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE],
            e.EV_ABS: [
                (e.ABS_X, AbsInfo(value=0, min=0, max=width - 1, fuzz=0, flat=0, resolution=0)),
                (e.ABS_Y, AbsInfo(value=0, min=0, max=height - 1, fuzz=0, flat=0, resolution=0)),
            ],
        }
        self._ui = UInput(caps, name=name, vendor=0x1209, product=0xA57C, version=1)
        self._left_down = False

    def move(self, x: float, y: float) -> None:
        xi = int(min(max(x, 0), self.width - 1))
        yi = int(min(max(y, 0), self.height - 1))
        self._ui.write(e.EV_ABS, e.ABS_X, xi)
        self._ui.write(e.EV_ABS, e.ABS_Y, yi)
        self._ui.syn()

    def left(self, down: bool) -> None:
        if down == self._left_down:
            return
        self._left_down = down
        self._ui.write(e.EV_KEY, e.BTN_LEFT, 1 if down else 0)
        self._ui.syn()

    def close(self) -> None:
        self.left(False)
        self._ui.close()


class NullPointer:
    """Para --dry-run: no mueve nada."""

    def __init__(self, width: int, height: int) -> None:
        self.width, self.height = width, height

    def move(self, x: float, y: float) -> None: ...
    def left(self, down: bool) -> None: ...
    def close(self) -> None: ...
