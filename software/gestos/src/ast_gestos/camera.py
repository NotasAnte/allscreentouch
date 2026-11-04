"""Ajustes V4L2 de la webcam que OpenCV no expone."""

from __future__ import annotations

import fcntl
import os
import struct

VIDIOC_G_CTRL = 0xC008561B
VIDIOC_S_CTRL = 0xC008561C
V4L2_CID_EXPOSURE_AUTO_PRIORITY = 0x009A0903


class ExposurePriorityOff:
    """Impide que la cámara baje los fps en poca luz (muchas Logitech lo hacen).

    Con la prioridad de exposición activada, en penumbra la cámara cae a 15 fps
    o menos; para seguir la mano preferimos fps altos aunque la imagen salga más oscura.
    Restaura el valor original al cerrar. Si el control no existe, no hace nada.
    """

    def __init__(self, device_index: int) -> None:
        self._fd: int | None = None
        self._original: int | None = None
        try:
            self._fd = os.open(f"/dev/video{device_index}", os.O_RDWR)
            self._original = self._get()
            self._set(0)
        except OSError:
            self.close()

    def _get(self) -> int:
        buf = fcntl.ioctl(self._fd, VIDIOC_G_CTRL, struct.pack("Ii", V4L2_CID_EXPOSURE_AUTO_PRIORITY, 0))
        return struct.unpack("Ii", buf)[1]

    def _set(self, value: int) -> None:
        fcntl.ioctl(self._fd, VIDIOC_S_CTRL, struct.pack("Ii", V4L2_CID_EXPOSURE_AUTO_PRIORITY, value))

    @property
    def applied(self) -> bool:
        return self._fd is not None

    def close(self) -> None:
        if self._fd is None:
            return
        try:
            if self._original is not None:
                self._set(self._original)
        except OSError:
            pass
        os.close(self._fd)
        self._fd = None
